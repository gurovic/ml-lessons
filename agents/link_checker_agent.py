"""
Агент проверки ссылок: references.json, slides_json, поля link.

Использование:
    python agents/link_checker_agent.py <lesson_dir>
    python agents/link_checker_agent.py --all
    python agents/link_checker_agent.py <lesson_dir> --fix
    python agents/link_checker_agent.py <lesson_dir> --offline
    python agents/link_checker_agent.py <lesson_dir> --llm
"""

from __future__ import annotations

import sys
from pathlib import Path

from link_checker_utils import (
    REPO_ROOT,
    Severity,
    apply_colab_fixes,
    format_report,
    run_checks,
    worst_severity,
)

PROMPT_PATH = Path(__file__).parent / "prompts" / "link_checker_agent.md"

LESSONS = [
    "lineynaya_regressiya",
    "logisticheskaya_regressiya",
    "derevo_resheniy",
    "pandas",
    "vizualizatsiya",
]


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def lesson_dirs_from_args(args: list[str]) -> list[Path]:
    if "--all" in args:
        return [REPO_ROOT / "lessons" / name for name in LESSONS]
    positional = [a for a in args[1:] if not a.startswith("-")]
    if not positional:
        return []
    path = Path(positional[0])
    if not path.is_absolute():
        path = REPO_ROOT / path
    return [path]


def build_llm_prompt(lesson_dir: Path, report_text: str) -> str:
    system = read_file(PROMPT_PATH) if PROMPT_PATH.exists() else ""
    refs_path = lesson_dir / "references.json"
    refs_block = ""
    if refs_path.exists():
        refs_block = refs_path.read_text(encoding="utf-8")

    problems = []
    report = run_checks(lesson_dir, online=False)
    for entry in report.entries:
        if entry.worst != Severity.OK:
            problems.append(
                f"- {entry.source}: {entry.url or '(нет)'} — "
                + "; ".join(f"{i.severity.value}: {i.reason}" for i in entry.issues if i.severity != Severity.OK)
            )

    return f"""{system}

---

# Урок: {lesson_dir.name}

## references.json

```json
{refs_block}
```

## Проблемные ссылки (автопроверка)

{chr(10).join(problems) if problems else "(нет проблем в offline-режиме)"}

## Отчёт link_checker

```
{report_text}
```

Предложи бесплатные full-text альтернативы для проблемных paper-URL.
Ответ — JSON-массив объектов: `{{"title", "old_url", "suggested_url", "reason"}}`.
Не меняй Colab-ссылки.
"""


def cmd_check(
    lesson_dirs: list[Path],
    *,
    fix: bool,
    offline: bool,
) -> int:
    reports = []
    any_fix = False

    for lesson_dir in lesson_dirs:
        if not lesson_dir.is_dir():
            print(f"FAIL  Папка не найдена: {lesson_dir}")
            return 1

        if fix:
            changes = apply_colab_fixes(lesson_dir)
            if changes:
                any_fix = True
                print(f"\n=== {lesson_dir.name}: --fix ===")
                for c in changes:
                    print(f"  fixed: {c}")

        report = run_checks(lesson_dir, online=not offline)
        reports.append(report)
        print()
        print(format_report(report))

    worst = worst_severity(reports)
    print()
    print(f"Итого: {worst.value} ({len(reports)} урок(ов))")
    if any_fix:
        print("Colab URL обновлены из project_config. Перезапустите без --fix для проверки.")

    if worst == Severity.FAIL:
        return 1
    return 0


def cmd_llm(lesson_dir: Path) -> None:
    if not lesson_dir.is_dir():
        print(f"Папка не найдена: {lesson_dir}")
        sys.exit(1)
    report = run_checks(lesson_dir, online=True)
    print(build_llm_prompt(lesson_dir, format_report(report)))


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        print(
            "Использование:\n"
            "  python agents/link_checker_agent.py <lesson_dir>\n"
            "  python agents/link_checker_agent.py --all [--fix] [--offline]\n"
            "  python agents/link_checker_agent.py <lesson_dir> [--fix] [--offline] [--llm]\n"
            "\n"
            "Проверяет URL в references.json, references-слайдах и полях link.\n"
            "Код выхода: 0 — OK/WARN, 1 — есть FAIL."
        )
        return 0

    fix = "--fix" in args
    offline = "--offline" in args

    if "--llm" in args:
        dirs = lesson_dirs_from_args(sys.argv)
        if len(dirs) != 1:
            print("Режим --llm: укажите ровно один lesson_dir")
            return 1
        cmd_llm(dirs[0])
        return 0

    lesson_dirs = lesson_dirs_from_args(sys.argv)
    if not lesson_dirs:
        print("Укажите lesson_dir или --all")
        return 1

    return cmd_check(lesson_dirs, fix=fix, offline=offline)


if __name__ == "__main__":
    raise SystemExit(main())
