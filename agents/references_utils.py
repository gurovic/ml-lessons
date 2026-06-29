"""Утилиты для Colab-ссылок, git remote и QR-кодов."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse


NOTEBOOK_FILES = ("code.ipynb", "project.ipynb")
COLAB_GITHUB_TEMPLATE = (
    "https://colab.research.google.com/github/{owner}/{repo}/blob/{branch}/{path}"
)


def _run_git(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def strip_url_credentials(url: str) -> str:
    """Убирает user:token@ из HTTPS URL."""
    parsed = urlparse(url)
    if parsed.scheme in ("http", "https") and parsed.netloc and "@" in parsed.netloc:
        host = parsed.netloc.split("@", 1)[1]
        return parsed._replace(netloc=host).geturl()
    return url


def parse_github_remote(remote_url: str) -> tuple[str, str] | None:
    """Возвращает (owner, repo) из origin URL."""
    url = strip_url_credentials(remote_url.strip())

    ssh_match = re.match(r"git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$", url)
    if ssh_match:
        return ssh_match.group(1), ssh_match.group(2)

    parsed = urlparse(url)
    if "github.com" not in parsed.netloc:
        return None

    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return unquote(owner), unquote(repo)


def get_git_github_info(repo_root: Path, config: dict | None = None) -> dict:
    """owner, repo, branch из project_config или git."""
    config = config or {}
    gh_cfg = config.get("github", {})

    owner = gh_cfg.get("owner")
    repo = gh_cfg.get("repo")
    branch = gh_cfg.get("branch")

    if not owner or not repo:
        remote = _run_git(["remote", "get-url", "origin"], repo_root)
        if remote:
            parsed = parse_github_remote(remote)
            if parsed:
                owner = owner or parsed[0]
                repo = repo or parsed[1]

    if not branch:
        branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_root) or "main"

    return {"owner": owner, "repo": repo, "branch": branch}


def notebook_repo_path(lesson_dir: Path, repo_root: Path, filename: str) -> str:
    """Путь к ноутбуку относительно корня репозитория (прямые слэши)."""
    rel = lesson_dir.resolve().relative_to(repo_root.resolve()) / filename
    return rel.as_posix()


def build_colab_github_url(
    owner: str,
    repo: str,
    branch: str,
    notebook_path: str,
) -> str:
    path = notebook_path.lstrip("/").replace("\\", "/")
    return COLAB_GITHUB_TEMPLATE.format(
        owner=owner, repo=repo, branch=branch, path=path
    )


def discover_colab_links(
    lesson_dir: Path,
    repo_root: Path | None = None,
    config: dict | None = None,
) -> list[dict]:
    """Список записей kind=colab для существующих ноутбуков."""
    repo_root = repo_root or Path(__file__).parent.parent
    gh = get_git_github_info(repo_root, config)

    if not gh.get("owner") or not gh.get("repo"):
        return []

    labels = {
        "code.ipynb": "Примеры по слайдам",
        "project.ipynb": "Мини-проект",
    }
    entries: list[dict] = []
    for name in NOTEBOOK_FILES:
        nb_path = lesson_dir / name
        if not nb_path.exists():
            continue
        rel = notebook_repo_path(lesson_dir, repo_root, name)
        url = build_colab_github_url(
            gh["owner"], gh["repo"], gh["branch"], rel
        )
        entries.append(
            {
                "kind": "colab",
                "title": name,
                "label": labels.get(name, name),
                "url": url,
            }
        )
    return entries


def merge_colab_into_references(
    slide: dict,
    colab_entries: list[dict],
) -> dict:
    """Обновляет colab-записи, сохраняя manual URL и paper-записи."""
    refs = slide.get("references", [])
    papers = sorted(
        [r for r in refs if r.get("kind") == "paper"],
        key=lambda r: (r.get("year") or 9999, r.get("title", "")),
    )
    old_colab = {r.get("title"): r for r in refs if r.get("kind") == "colab"}

    merged_colab: list[dict] = []
    for entry in colab_entries:
        title = entry["title"]
        prev = old_colab.get(title, {})
        if prev.get("manual") and prev.get("url"):
            merged_colab.append({**entry, "url": prev["url"], "manual": True})
        else:
            merged_colab.append(entry)

    slide["references"] = papers + merged_colab
    slide.setdefault("type", "references")
    slide.setdefault("title", "Источники и практика")
    return slide


def format_paper_bullet(ref: dict) -> str:
    authors = ref.get("authors", "")
    year = ref.get("year", "")
    title = ref.get("title", "")
    year_str = f" ({year})" if year else ""
    return f"{authors}{year_str}. {title}"


def generate_qr_png(url: str, output_path: Path, box_size: int = 8) -> Path:
    """Сохраняет QR-код в PNG; возвращает путь к файлу."""
    import qrcode

    output_path.parent.mkdir(parents=True, exist_ok=True)
    qr = qrcode.QRCode(box_size=box_size, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(str(output_path))
    return output_path
