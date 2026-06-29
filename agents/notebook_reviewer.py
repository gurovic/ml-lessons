"""
Рецензент ноутбуков урока: code.ipynb и project.ipynb.

Программная проверка (синтаксис, setup, imports, покрытие слайдов, narrative)
и промпт для AI-рецензии с исправлениями.

Использование:
    python agents/notebook_reviewer.py lessons/<slug>
    python agents/notebook_reviewer.py --pilot
    python agents/notebook_reviewer.py lessons/<slug> --check-only
    python agents/notebook_reviewer.py lessons/<slug> --save [file]
    python agents/notebook_reviewer.py lessons/<slug> --apply [file]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from notebook_utils import (
    NOTEBOOK_FILES,
    build_ipynb,
    check_lesson_notebooks,
    list_assets,
    notebook_to_prompt_block,
    parse_reviewer_response,
    save_ipynb,
    select_slides_for_notebook,
    slide_to_notebook_context,
)
from slide_utils import read_slides

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "notebook_reviewer.md"
PILOT_LESSON = "lineynaya_regressiya"


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def pilot_lesson_dir() -> Path:
    return REPO_ROOT / "lessons" / PILOT_LESSON


def extract_markdown_report(raw: str) -> str:
    raw = raw.strip()
    for fence in ("```markdown", "```md"):
        if raw.startswith(fence):
            start = raw.index(fence) + len(fence)
            end = raw.index("```", start)
            return raw[start:end].strip()
    if raw.startswith("```") and raw.count("```") >= 2:
        start = raw.index("```") + 3
        end = raw.index("```", start)
        return raw[start:end].strip()
    return raw


def build_user_prompt(lesson_dir: Path, auto_issues: list[str]) -> str:
    info_path = lesson_dir / "info.json"
    slides_dir = lesson_dir / "slides_json"

    info: dict = {}
    if info_path.exists():
        info = json.loads(read_file(info_path))

    slides = read_slides(slides_dir) if slides_dir.exists() else []
    selected = select_slides_for_notebook(slides)

    slides_block = "\n\n".join(
        slide_to_notebook_context(idx, slide, cfg)
        for idx, slide, cfg in selected
    ) or "(нет слайдов-кандидатов для code.ipynb)"

    assets = list_assets(lesson_dir)
    assets_block = "\n".join(f"- assets/{name}" for name in assets) if assets else "(нет изображений)"

    nb_blocks = "\n\n".join(
        notebook_to_prompt_block(lesson_dir / name) for name in NOTEBOOK_FILES
    )

    auto_block = (
        "\n".join(f"- {i}" for i in auto_issues)
        if auto_issues
        else "- программных замечаний нет"
    )

    return f"""# Урок: {lesson_dir.name}

**Тема:** {info.get('topic', lesson_dir.name)}
**Длительность:** {info.get('duration_minutes', '?')} мин

## Файлы assets/

{assets_block}

## Слайды-кандидаты для code.ipynb

{slides_block}

## Текущие ноутбуки

{nb_blocks}

## Автопроверка (notebook_reviewer --check-only)

{auto_block}

---
Проведи рецензию обоих ноутбуков по критериям system prompt.
Верни JSON с report и исправленными sections (если нужны правки).
"""


def build_prompt(lesson_dir: Path) -> str:
    auto_issues = check_lesson_notebooks(lesson_dir)
    system = read_file(PROMPT_PATH)
    user = build_user_prompt(lesson_dir, auto_issues)
    return f"{system}\n\n---\n\n{user}"


def save_review_report(lesson_dir: Path, content: str) -> Path:
    path = lesson_dir / "notebook_review.md"
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"Отчёт сохранён: {path}")
    return path


def apply_notebook_sections(
    lesson_dir: Path,
    nb_name: str,
    sections: list[dict],
    *,
    topic: str,
    intro: str | None = None,
) -> None:
    from notebook_utils import _make_cell

    if not sections:
        print(f"  {nb_name}: sections пуст — файл не изменён")
        return

    notebook = build_ipynb(sections, topic=topic, setup=True)

    if nb_name == "project.ipynb":
        proj_intro = intro or (
            f"# {topic}\n\n"
            "Сквозной мини-проект: один датасет, решения передаются между этапами. "
            "См. docs/project_notebook.md.\n"
        )
        notebook["cells"][0] = _make_cell("markdown", proj_intro)

    out = lesson_dir / nb_name
    save_ipynb(out, notebook)
    print(f"  {nb_name}: сохранён ({len(sections)} секций, {len(notebook['cells'])} ячеек)")


def cmd_apply(lesson_dir: Path, raw: str) -> None:
    info_path = lesson_dir / "info.json"
    topic = lesson_dir.name
    if info_path.exists():
        topic = json.loads(read_file(info_path)).get("topic", topic)

    data = parse_reviewer_response(raw)
    report = data.get("report")
    if isinstance(report, str) and report.strip():
        save_review_report(lesson_dir, extract_markdown_report(report))

    code_block = data.get("code")
    if isinstance(code_block, dict) and code_block.get("sections"):
        apply_notebook_sections(lesson_dir, "code.ipynb", code_block["sections"], topic=topic)

    project_block = data.get("project")
    if isinstance(project_block, dict) and project_block.get("sections"):
        proj_title = f"{topic} — мини-проект"
        apply_notebook_sections(
            lesson_dir,
            "project.ipynb",
            project_block["sections"],
            topic=proj_title,
            intro=None,
        )

    remaining = check_lesson_notebooks(lesson_dir)
    if remaining:
        print(f"\nПосле --apply осталось {len(remaining)} предупреждений:")
        for issue in remaining:
            print(f"  [warn] {issue}")
    else:
        print("\nАвтопроверка: замечаний нет")


def cmd_check(lesson_dir: Path) -> list[str]:
    print(f"\n=== Проверка ноутбуков: {lesson_dir.name} ===")
    issues = check_lesson_notebooks(lesson_dir)
    if issues:
        for issue in issues:
            print(f"  [warn] {issue}")
    else:
        print("  OK: замечаний нет")
    return issues


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(1)

    if argv[0] == "--pilot":
        lesson_dir = pilot_lesson_dir()
        argv = argv[1:]
    else:
        lesson_dir = Path(argv[0])
        if not lesson_dir.is_absolute():
            lesson_dir = REPO_ROOT / lesson_dir
        argv = argv[1:]

    if not lesson_dir.exists():
        print(f"Папка не найдена: {lesson_dir}")
        sys.exit(1)

    mode = argv[0] if argv else "prompt"
    mode_args = argv[1:] if argv else []

    if mode == "--check-only":
        issues = cmd_check(lesson_dir)
        sys.exit(1 if issues else 0)

    if mode == "--save":
        if mode_args:
            raw = read_file(Path(mode_args[0]))
        else:
            raw = sys.stdin.read()
        if not raw.strip():
            print("Пустой ответ, отчёт не сохранён.")
            sys.exit(1)
        save_review_report(lesson_dir, extract_markdown_report(raw))
        return

    if mode == "--apply":
        if mode_args:
            raw = read_file(Path(mode_args[0]))
        else:
            raw = sys.stdin.read()
        if not raw.strip():
            print("Пустой ответ, ноутбуки не изменены.")
            sys.exit(1)
        try:
            cmd_apply(lesson_dir, raw)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Ошибка разбора ответа: {e}")
            sys.exit(1)
        return

    issues = cmd_check(lesson_dir)
    print("\n" + build_prompt(lesson_dir))
    print(f"\n---\nСохранить отчёт: python agents/notebook_reviewer.py {lesson_dir} --save notebook_review.md")
    print(f"Применить правки: python agents/notebook_reviewer.py {lesson_dir} --apply fixes.json")
    if issues:
        print(f"Автопроверка: {len(issues)} предупреждений — см. промпт выше")


if __name__ == "__main__":
    main()
