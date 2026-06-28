"""
Агент примеров кода на слайдах презентации.

Использование:
    python agents/slide_code_agent.py <lesson_dir> --list
    python agents/slide_code_agent.py <lesson_dir> --prompt
    python agents/slide_code_agent.py <lesson_dir> --save [file]
    python agents/slide_code_agent.py <lesson_dir> --apply
"""

import json
import subprocess
import sys
from pathlib import Path

from slide_code_bootstrap import get_bootstrap_examples, list_bootstrap_titles
from slide_code_utils import (
    apply_response_to_slides,
    merge_code_examples,
    parse_slide_code_response,
    select_slides_for_code,
    slide_to_code_context,
)
from slide_utils import list_slide_files, read_slides, save_slide

PROMPT_PATH = Path(__file__).parent / "prompts" / "slide_code_agent.md"
REPO_ROOT = Path(__file__).parent.parent


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_user_prompt(lesson_dir: Path) -> str:
    info_path = lesson_dir / "info.json"
    slides = read_slides(lesson_dir / "slides_json")
    selected = select_slides_for_code(slides)

    info: dict = {}
    if info_path.exists():
        info = json.loads(read_file(info_path))

    if not selected:
        return ""

    slides_text = "\n\n".join(
        slide_to_code_context(idx, slide) for idx, slide in selected
    )

    return f"""# Урок для code_examples на слайдах

**Папка:** {lesson_dir.name}
**Тема:** {info.get('topic', lesson_dir.name)}
**Кандидатов:** {len(selected)} из {len(slides)}

## Слайды без code_examples (генерируй только для них)

{slides_text}

---
Верни JSON по шаблону из system prompt.
"""


def build_prompt(lesson_dir: Path) -> str:
    system = read_file(PROMPT_PATH)
    user = build_user_prompt(lesson_dir)
    if not user:
        return ""
    return f"{system}\n\n---\n\n{user}"


def cmd_list(lesson_dir: Path) -> None:
    slides = read_slides(lesson_dir / "slides_json")
    selected = select_slides_for_code(slides)
    if not selected:
        print("Нет кандидатов для code_examples.")
        return
    print(f"Кандидаты ({len(selected)} из {len(slides)}):\n")
    for idx, slide in selected:
        nb = "notebook" if slide.get("notebook") else "api"
        print(f"  {idx:02d}. «{slide.get('title', '')}»  [{nb}]")


def cmd_save(lesson_dir: Path, raw: str) -> None:
    slides_dir = lesson_dir / "slides_json"
    slides = read_slides(slides_dir)
    response = parse_slide_code_response(raw)
    updated, warnings = apply_response_to_slides(slides, response)

    changed = 0
    for i, (old, new) in enumerate(zip(slides, updated), 1):
        if old.get("code_examples") != new.get("code_examples"):
            save_slide(slides_dir, new, i)
            changed += 1

    for w in warnings:
        print(f"  [warn] {w}")
    print(f"Обновлено слайдов: {changed}")


def cmd_apply(lesson_dir: Path, *, rebuild_pptx: bool = False) -> int:
    slides_dir = lesson_dir / "slides_json"
    lesson_name = lesson_dir.name
    enriched = 0
    skipped = 0

    for path in list_slide_files(slides_dir):
        slide_num = int(path.stem)
        slide = json.loads(read_file(path))
        title = slide.get("title", "")

        if slide.get("code_examples"):
            skipped += 1
            continue

        examples = get_bootstrap_examples(lesson_name, title)
        if not examples:
            continue

        updated = merge_code_examples(slide, examples)
        save_slide(slides_dir, updated, slide_num)
        enriched += 1

    print(f"Bootstrap: обогащено {enriched}, пропущено (уже есть код): {skipped}")

    if rebuild_pptx:
        builder = Path(__file__).parent / "pptx_builder.py"
        print("\nПересборка presentation.pptx...")
        subprocess.run(
            [sys.executable, str(builder), str(lesson_dir)],
            cwd=REPO_ROOT,
            check=False,
        )

    return enriched


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if len(sys.argv) < 2:
        print(
            "Использование: python agents/slide_code_agent.py <lesson_dir> "
            "[--list | --prompt | --save [file] | --apply]"
        )
        sys.exit(1)

    lesson_dir = Path(sys.argv[1])
    if not lesson_dir.exists():
        print(f"Папка не найдена: {lesson_dir}")
        sys.exit(1)

    slides_dir = lesson_dir / "slides_json"
    if not slides_dir.exists() and len(sys.argv) >= 3 and sys.argv[2] != "--prompt":
        print(f"slides_json не найден: {slides_dir}")
        sys.exit(1)

    if len(sys.argv) >= 3 and sys.argv[2] == "--list":
        cmd_list(lesson_dir)
        return

    if len(sys.argv) >= 3 and sys.argv[2] == "--prompt":
        prompt = build_prompt(lesson_dir)
        if not prompt:
            print("Нет кандидатов для code_examples.")
            sys.exit(1)
        print(prompt)
        print(
            f"\n---\nСохранить: python agents/slide_code_agent.py {lesson_dir} --save response.json"
        )
        return

    if len(sys.argv) >= 3 and sys.argv[2] == "--save":
        if len(sys.argv) >= 4:
            raw = read_file(Path(sys.argv[3]))
        else:
            raw = sys.stdin.read()
        if not raw.strip():
            print("Пустой ответ, слайды не обновлены.")
            sys.exit(1)
        try:
            cmd_save(lesson_dir, raw)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Ошибка разбора ответа: {e}")
            sys.exit(1)
        return

    if len(sys.argv) >= 3 and sys.argv[2] == "--apply":
        cmd_apply(lesson_dir, rebuild_pptx="--rebuild" in sys.argv[3:])
        return

    print("Укажите режим: --list, --prompt, --save [file] или --apply")
    sys.exit(1)


if __name__ == "__main__":
    main()
