"""Проверка URL в references.json, slides_json и полях link."""

from __future__ import annotations

import json
import re
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

from references_utils import (
    build_colab_github_url,
    get_git_github_info,
    notebook_repo_path,
)
from slide_utils import list_slide_files

REPO_ROOT = Path(__file__).parent.parent

COLAB_PATTERN = re.compile(
    r"^https://colab\.research\.google\.com/github/"
    r"(?P<owner>[^/]+)/(?P<repo>[^/]+)/blob/(?P<branch>[^/]+)/(?P<path>.+)$"
)

PAYWALL_HOSTS = (
    "jstor.org",
    "acm.org",
    "ieeexplore.ieee.org",
    "sciencedirect.com",
    "onlinelibrary.wiley.com",
    "tandfonline.com",
    "link.springer.com",
    "springer.com",
    "nature.com",
)

PAYWALL_PATH_HINTS = ("/doi/", "/document/", "/article/", "/abs/")

FREE_HOSTS = (
    "arxiv.org",
    "zenodo.org",
    "github.com",
    "raw.githubusercontent.com",
    "colab.research.google.com",
)

# Sites that block automated HEAD/GET (403) but work in a browser.
BOT_BLOCKING_HOSTS = (
    "akinator.com",
)


class Severity(str, Enum):
    OK = "OK"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass
class LinkIssue:
    severity: Severity
    reason: str


@dataclass
class LinkEntry:
    url: str
    source: str
    kind: str = "unknown"
    label: str = ""
    issues: list[LinkIssue] = field(default_factory=list)

    @property
    def worst(self) -> Severity:
        if any(i.severity == Severity.FAIL for i in self.issues):
            return Severity.FAIL
        if any(i.severity == Severity.WARN for i in self.issues):
            return Severity.WARN
        return Severity.OK


@dataclass
class LessonReport:
    lesson: str
    entries: list[LinkEntry] = field(default_factory=list)

    @property
    def worst(self) -> Severity:
        if not self.entries:
            return Severity.OK
        order = {Severity.FAIL: 0, Severity.WARN: 1, Severity.OK: 2}
        return min((e.worst for e in self.entries), key=lambda s: order[s])


def load_config(repo_root: Path | None = None) -> dict:
    repo_root = repo_root or REPO_ROOT
    cfg_path = repo_root / "project_config.json"
    if cfg_path.exists():
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    return {}


def parse_colab_url(url: str) -> dict | None:
    match = COLAB_PATTERN.match(url.strip())
    if not match:
        return None
    return {
        "owner": match.group("owner"),
        "repo": match.group("repo"),
        "branch": match.group("branch"),
        "path": match.group("path"),
    }


def _host(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:
        return ""


def _path(url: str) -> str:
    return urlparse(url).path.lower()


def is_bot_blocking_host(url: str) -> bool:
    host = _host(url)
    for pattern in BOT_BLOCKING_HOSTS:
        if host == pattern or host.endswith("." + pattern):
            return True
    return False


def is_likely_paywall(url: str) -> str | None:
    """Эвристика без сети; None если по URL нет признаков paywall."""
    host = _host(url)
    path = _path(url)

    if host == "doi.org":
        if "/10.5281/zenodo" in url.lower():
            return None
        return "DOI-ссылка — часто ведёт на paywall; предпочтите прямой PDF или arXiv"

    for free in FREE_HOSTS:
        if host == free or host.endswith("." + free):
            if free == "zenodo.org":
                return None
            if url.lower().rstrip("/").endswith(".pdf") or "/pdf" in path:
                return None
            if free in ("arxiv.org", "github.com", "raw.githubusercontent.com", "colab.research.google.com"):
                return None

    if url.lower().endswith(".pdf") or "/pdf" in path or "pdf" in path.split("/")[-1]:
        return None

    for paywall in PAYWALL_HOSTS:
        if host == paywall or host.endswith("." + paywall):
            if "pdf" in path:
                return None
            return f"Хост {paywall} — вероятен paywall без прямого PDF"

    for hint in PAYWALL_PATH_HINTS:
        if hint in path and not url.lower().endswith(".pdf"):
            return f"URL содержит «{hint}» — возможен paywall"

    return None


def http_check(url: str, timeout: float = 15.0, online: bool = True) -> list[LinkIssue]:
    if not online:
        return []

    if not url.startswith(("http://", "https://")):
        return [LinkIssue(Severity.FAIL, "Некорректная схема URL (ожидается http/https)")]

    ctx = ssl.create_default_context()
    headers = {"User-Agent": "ml-lessons-link-checker/1.0"}

    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                status = resp.status
                final_url = resp.geturl()
                ctype = resp.headers.get("Content-Type", "")
                if status >= 400:
                    return [LinkIssue(Severity.FAIL, f"HTTP {status}")]
                issues: list[LinkIssue] = []
                paywall = is_likely_paywall(final_url)
                if paywall:
                    issues.append(LinkIssue(Severity.WARN, paywall))
                elif final_url != url and _host(url) == "doi.org":
                    issues.append(
                        LinkIssue(
                            Severity.WARN,
                            f"DOI перенаправляет на {_host(final_url)} — проверьте доступность",
                        )
                    )
                if method == "GET" and "text/html" in ctype and not url.lower().endswith(".pdf"):
                    if _host(final_url) not in FREE_HOSTS and not final_url.lower().endswith(".pdf"):
                        hint = is_likely_paywall(final_url)
                        if hint and not any(i.reason == hint for i in issues):
                            issues.append(LinkIssue(Severity.WARN, hint))
                return issues or [LinkIssue(Severity.OK, "HTTP доступен")]
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (405, 501, 403):
                continue
            if e.code >= 400:
                if e.code == 403 and is_bot_blocking_host(url):
                    return [
                        LinkIssue(
                            Severity.WARN,
                            "Сайт блокирует автоматические запросы (403); URL оставлен",
                        )
                    ]
                return [LinkIssue(Severity.FAIL, f"HTTP {e.code}")]
        except urllib.error.URLError as e:
            if method == "GET":
                reason = str(e.reason)
                if "timed out" in reason.lower() or "getaddrinfo" in reason.lower():
                    return [LinkIssue(Severity.WARN, f"Сеть недоступна: {e.reason}")]
                return [LinkIssue(Severity.FAIL, f"Сеть: {e.reason}")]
        except Exception as e:
            if method == "GET":
                return [LinkIssue(Severity.FAIL, f"Ошибка запроса: {e}")]

    return [LinkIssue(Severity.FAIL, "Не удалось проверить URL")]


def check_colab_url(
    url: str,
    gh: dict,
    lesson_dir: Path,
    repo_root: Path,
    online: bool = True,
) -> list[LinkIssue]:
    issues: list[LinkIssue] = []
    parsed = parse_colab_url(url)
    if not parsed:
        return [
            LinkIssue(
                Severity.FAIL,
                "Неверный формат Colab URL (ожидается colab.research.google.com/github/owner/repo/blob/branch/path)",
            )
        ]

    expected_owner = gh.get("owner")
    expected_repo = gh.get("repo")
    expected_branch = gh.get("branch")

    if expected_owner and parsed["owner"] != expected_owner:
        issues.append(
            LinkIssue(
                Severity.FAIL,
                f"owner «{parsed['owner']}» ≠ project_config «{expected_owner}»",
            )
        )
    if expected_repo and parsed["repo"] != expected_repo:
        issues.append(
            LinkIssue(
                Severity.FAIL,
                f"repo «{parsed['repo']}» ≠ project_config «{expected_repo}»",
            )
        )
    if expected_branch and parsed["branch"] != expected_branch:
        issues.append(
            LinkIssue(
                Severity.WARN,
                f"branch «{parsed['branch']}» ≠ project_config «{expected_branch}»",
            )
        )

    nb_name = Path(parsed["path"]).name
    if nb_name not in ("code.ipynb", "project.ipynb"):
        issues.append(LinkIssue(Severity.WARN, f"Неожиданный ноутбук: {nb_name}"))

    local_nb = lesson_dir / nb_name
    if not local_nb.exists():
        issues.append(LinkIssue(Severity.FAIL, f"Локально нет файла {nb_name}"))

    rel = notebook_repo_path(lesson_dir, repo_root, nb_name)
    if parsed["path"].replace("\\", "/") != rel:
        issues.append(
            LinkIssue(
                Severity.WARN,
                f"Путь в URL «{parsed['path']}» ≠ ожидаемый «{rel}»",
            )
        )

    if online and expected_owner and expected_repo and expected_branch:
        raw = (
            f"https://raw.githubusercontent.com/{expected_owner}/{expected_repo}/"
            f"{expected_branch}/{rel}"
        )
        raw_issues = http_check(raw, online=True)
        for ri in raw_issues:
            if ri.severity == Severity.FAIL:
                issues.append(
                    LinkIssue(
                        Severity.WARN,
                        f"На GitHub ({expected_branch}) файл не найден: {ri.reason}",
                    )
                )

    if not issues:
        issues.append(LinkIssue(Severity.OK, "Colab URL корректен"))
    return issues


def check_paper_url(url: str, online: bool = True) -> list[LinkIssue]:
    if not url:
        return [LinkIssue(Severity.WARN, "URL отсутствует")]

    issues: list[LinkIssue] = []
    paywall = is_likely_paywall(url)
    if paywall:
        issues.append(LinkIssue(Severity.WARN, paywall))

    issues.extend(http_check(url, online=online))
    if not issues:
        return [LinkIssue(Severity.OK, "Доступен")]
    return issues


def check_generic_url(url: str, online: bool = True) -> list[LinkIssue]:
    if not url:
        return [LinkIssue(Severity.WARN, "URL отсутствует")]
    return http_check(url, online=online) or [LinkIssue(Severity.OK, "Доступен")]


def collect_lesson_links(lesson_dir: Path, repo_root: Path | None = None) -> list[LinkEntry]:
    repo_root = repo_root or REPO_ROOT
    entries: list[LinkEntry] = []
    seen: set[tuple[str, str]] = set()

    def add(url: str | None, source: str, kind: str, label: str = "") -> None:
        if not url:
            entries.append(
                LinkEntry(url="", source=source, kind=kind, label=label, issues=[
                    LinkIssue(Severity.WARN, "URL отсутствует"),
                ])
            )
            return
        key = (url, source)
        if key in seen:
            return
        seen.add(key)
        entries.append(LinkEntry(url=url, source=source, kind=kind, label=label))

    refs_json = lesson_dir / "references.json"
    if refs_json.exists():
        data = json.loads(refs_json.read_text(encoding="utf-8"))
        for i, ref in enumerate(data.get("references", [])):
            kind = ref.get("kind", "unknown")
            title = ref.get("title", ref.get("label", f"ref[{i}]"))
            add(ref.get("url"), f"references.json → {title}", kind, title)

    slides_dir = lesson_dir / "slides_json"
    if slides_dir.exists():
        for path in list_slide_files(slides_dir):
            slide = json.loads(path.read_text(encoding="utf-8"))
            slide_label = f"{path.name} «{slide.get('title', '')}»"

            if slide.get("type") == "references":
                for i, ref in enumerate(slide.get("references", [])):
                    kind = ref.get("kind", "unknown")
                    title = ref.get("title", ref.get("label", f"ref[{i}]"))
                    add(ref.get("url"), f"{slide_label} → {title}", kind, title)

            link = slide.get("link")
            if isinstance(link, dict) and link.get("url"):
                add(
                    link["url"],
                    f"{slide_label} → link",
                    "slide_link",
                    link.get("label", ""),
                )

    return entries


def run_checks(
    lesson_dir: Path,
    repo_root: Path | None = None,
    online: bool = True,
) -> LessonReport:
    repo_root = repo_root or REPO_ROOT
    config = load_config(repo_root)
    gh = get_git_github_info(repo_root, config)
    report = LessonReport(lesson=lesson_dir.name)

    for entry in collect_lesson_links(lesson_dir, repo_root):
        if entry.url == "":
            report.entries.append(entry)
            continue

        if entry.kind == "colab":
            entry.issues = check_colab_url(
                entry.url, gh, lesson_dir, repo_root, online=online
            )
        elif entry.kind == "paper":
            entry.issues = check_paper_url(entry.url, online=online)
        else:
            entry.issues = check_generic_url(entry.url, online=online)

        report.entries.append(entry)

    return report


def expected_colab_url(
    url: str,
    gh: dict,
    lesson_dir: Path,
    repo_root: Path,
) -> str | None:
    """Возвращает исправленный Colab URL или None, если менять нечего."""
    parsed = parse_colab_url(url)
    if not parsed:
        return None

    nb_name = Path(parsed["path"]).name
    if nb_name not in ("code.ipynb", "project.ipynb"):
        return None
    if not (lesson_dir / nb_name).exists():
        return None

    owner = gh.get("owner") or parsed["owner"]
    repo = gh.get("repo") or parsed["repo"]
    branch = gh.get("branch") or parsed["branch"]
    rel = notebook_repo_path(lesson_dir, repo_root, nb_name)
    fixed = build_colab_github_url(owner, repo, branch, rel)
    return fixed if fixed != url else None


def apply_colab_fixes(lesson_dir: Path, repo_root: Path | None = None) -> list[str]:
    """Исправляет branch/owner/repo/path в Colab URL. Возвращает список изменений."""
    repo_root = repo_root or REPO_ROOT
    config = load_config(repo_root)
    gh = get_git_github_info(repo_root, config)
    changes: list[str] = []

    targets: list[Path] = []
    refs_json = lesson_dir / "references.json"
    if refs_json.exists():
        targets.append(refs_json)
    slides_dir = lesson_dir / "slides_json"
    if slides_dir.exists():
        for path in list_slide_files(slides_dir):
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("type") == "references":
                targets.append(path)

    for path in targets:
        data = json.loads(path.read_text(encoding="utf-8"))
        modified = False
        for ref in data.get("references", []):
            if ref.get("kind") != "colab" or not ref.get("url"):
                continue
            fixed = expected_colab_url(ref["url"], gh, lesson_dir, repo_root)
            if fixed:
                old = ref["url"]
                ref["url"] = fixed
                modified = True
                changes.append(f"{path.name}: {old} → {fixed}")
        if modified:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    return changes


def format_report(report: LessonReport) -> str:
    lines = [f"=== {report.lesson} ({report.worst.value}) ==="]
    if not report.entries:
        lines.append("  (ссылок не найдено)")
        return "\n".join(lines)

    for entry in report.entries:
        status = entry.worst.value
        label = f" [{entry.label}]" if entry.label else ""
        lines.append(f"  {status}  {entry.kind}{label}")
        lines.append(f"         {entry.url or '(нет URL)'}")
        lines.append(f"         ← {entry.source}")
        for issue in entry.issues:
            if issue.severity != Severity.OK:
                lines.append(f"         • {issue.severity.value}: {issue.reason}")
            elif len(entry.issues) == 1:
                lines.append(f"         • {issue.reason}")
    return "\n".join(lines)


def worst_severity(reports: list[LessonReport]) -> Severity:
    order = {Severity.FAIL: 0, Severity.WARN: 1, Severity.OK: 2}
    if not reports:
        return Severity.OK
    return min((r.worst for r in reports), key=lambda s: order[s])
