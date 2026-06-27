"""
Генератор code.ipynb по JSON-слайдам презентации.

Отбирает слайды, где уместен код, формирует промпт для AI,
собирает ноутбук из структурированного JSON-ответа.

Использование:
    python agents/notebook_generator.py <lesson_dir>
    python agents/notebook_generator.py <lesson_dir> --list
    python agents/notebook_generator.py <lesson_dir> --save [file]
"""

import json
import sys
from pathlib import Path

from notebook_utils import (
    build_ipynb,
    list_assets,
    parse_notebook_response,
    save_ipynb,
    select_slides_for_notebook,
    slide_to_notebook_context,
)
from slide_utils import read_slides

PROMPT_PATH = Path(__file__).parent / "prompts" / "notebook_generator.md"


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_user_prompt(lesson_dir: Path) -> str:
    info_path = lesson_dir / "info.json"
    slides_dir = lesson_dir / "slides_json"
    slides = read_slides(slides_dir)
    selected = select_slides_for_notebook(slides)

    info: dict = {}
    if info_path.exists():
        info = json.loads(read_file(info_path))

    if not selected:
        return ""

    slides_text = "\n\n".join(
        slide_to_notebook_context(idx, slide, cfg)
        for idx, slide, cfg in selected
    )
    assets = list_assets(lesson_dir)
    assets_block = "\n".join(f"- assets/{name}" for name in assets) if assets else "(нет изображений)"

    skipped = len(slides) - len(selected)

    return f"""# Урок для ноутбука

**Папка:** {lesson_dir.name}
**Тема:** {info.get('topic', lesson_dir.name)}
**Длительность:** {info.get('duration_minutes', '?')} мин
**Слайдов всего:** {len(slides)}; **кандидатов для ноутбука:** {len(selected)} (пропущено {skipped})

## Файлы assets/

{assets_block}

## Слайды-кандидаты (генерируй секции только для них)

{slides_text}

---
Сгенерируй JSON с ячейками ноутбука по шаблону из system prompt.
"""


def build_prompt(lesson_dir: Path) -> str:
    system = read_file(PROMPT_PATH)
    user = build_user_prompt(lesson_dir)
    if not user:
        return ""
    return f"{system}\n\n---\n\n{user}"


def cmd_list(lesson_dir: Path) -> None:
    slides = read_slides(lesson_dir / "slides_json")
    selected = select_slides_for_notebook(slides)
    if not selected:
        print("Нет слайдов для ноутбука.")
        return
    print(f"Кандидаты для code.ipynb ({len(selected)} из {len(slides)}):\n")
    for idx, slide, cfg in selected:
        kinds = ", ".join(cfg.get("kinds", []))
        print(f"  {idx:02d}. «{slide.get('title', '')}»  [{cfg.get('reason')}] → {kinds}")


def cmd_save(lesson_dir: Path, raw: str) -> None:
    info_path = lesson_dir / "info.json"
    topic = lesson_dir.name
    if info_path.exists():
        topic = json.loads(read_file(info_path)).get("topic", topic)

    data = parse_notebook_response(raw)
    notebook = build_ipynb(data["sections"], topic=topic)
    out = lesson_dir / "code.ipynb"
    save_ipynb(out, notebook)
    n_sections = len(data["sections"])
    n_cells = len(notebook["cells"])
    print(f"Ноутбук сохранён: {out} ({n_sections} секций, {n_cells} ячеек)")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if len(sys.argv) < 2:
        print(
            "Использование: python agents/notebook_generator.py <lesson_dir> [--list | --save [file]]"
        )
        sys.exit(1)

    lesson_dir = Path(sys.argv[1])
    if not lesson_dir.exists():
        print(f"Папка не найдена: {lesson_dir}")
        sys.exit(1)

    slides_dir = lesson_dir / "slides_json"
    if not slides_dir.exists():
        print(f"slides_json не найден: {slides_dir}")
        sys.exit(1)

    if len(sys.argv) >= 3 and sys.argv[2] == "--list":
        cmd_list(lesson_dir)
        return

    if len(sys.argv) >= 3 and sys.argv[2] == "--save":
        if len(sys.argv) >= 4:
            raw = read_file(Path(sys.argv[3]))
        else:
            raw = sys.stdin.read()
        if not raw.strip():
            print("Пустой ответ, ноутбук не сохранён.")
            sys.exit(1)
        try:
            cmd_save(lesson_dir, raw)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Ошибка разбора ответа: {e}")
            sys.exit(1)
        return

    prompt = build_prompt(lesson_dir)
    if not prompt:
        print("Нет слайдов для ноутбука. Проверьте эвристики или добавьте поле notebook в JSON.")
        sys.exit(1)

    print(prompt)
    print(f"\n---\nСписок кандидатов: python agents/notebook_generator.py {lesson_dir} --list")
    print(f"Сохранить: python agents/notebook_generator.py {lesson_dir} --save response.json")


if __name__ == "__main__":
    main()
