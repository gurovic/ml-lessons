"""
Рецензент урока: проверка JSON-слайдов до сборки presentation.pptx.

Формирует промпт для AI-рецензента (фактология, логика, понятность,
лаконичность, полнота). Отчёт сохраняется в review.md.
Автор проверяет готовый pptx; JSON правят агенты по замечаниям (см. docs/pipeline.md).

Использование:
    python agents/lesson_reviewer.py <lesson_dir>
    python agents/lesson_reviewer.py <lesson_dir> --save
    python agents/lesson_reviewer.py <lesson_dir> --save response.md
"""

import json
import re
import sys
from pathlib import Path

from slide_utils import list_slide_files, read_slides

PROMPT_PATH = Path(__file__).parent / "prompts" / "lesson_reviewer.md"
LESSONS_ROOT = Path(__file__).parent.parent / "lessons"


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_plan_slides(plan: str) -> list[str]:
    lines = plan.split("\n")
    blocks: list[str] = []
    current: list[str] = []
    for line in lines:
        stripped = line.strip()
        if re.match(r"\*{0,2}\s*Слайд\s+\d+", stripped):
            if current:
                blocks.append("\n".join(current))
            current = [stripped]
        elif current:
            current.append(stripped)
    if current:
        blocks.append("\n".join(current))
    return blocks


def slide_to_text(slide: dict) -> str:
    title = slide.get("title", "(без заголовка)")
    parts = [f"### «{title}»"]
    for bullet in slide.get("bullets", []):
        parts.append(f"- {bullet}")
    if slide.get("notes"):
        parts.append(f"_Заметки:_ {slide['notes']}")
    if slide.get("visuals"):
        names = [v.get("output", "?") for v in slide["visuals"]]
        parts.append(f"_Визуализации:_ {', '.join(names)}")
    if slide.get("link"):
        link = slide["link"]
        parts.append(f"_Ссылка:_ {link.get('label', '')} → {link.get('url', '')}")
    if slide.get("formula"):
        parts.append("_[warn] устаревшее поле formula — перенесите в $...$_")
    return "\n".join(parts)


def other_lessons_context(current_dir: Path) -> str:
    if not LESSONS_ROOT.exists():
        return "(других уроков в courses/lessons нет)"

    blocks: list[str] = []
    for lesson_dir in sorted(LESSONS_ROOT.iterdir()):
        if not lesson_dir.is_dir() or lesson_dir.resolve() == current_dir.resolve():
            continue
        readme = lesson_dir / "README.md"
        plan = lesson_dir / "plan.md"
        title = readme.read_text(encoding="utf-8").strip().split("\n")[0] if readme.exists() else lesson_dir.name
        plan_preview = ""
        if plan.exists():
            plan_preview = "\n".join(read_file(plan).split("\n")[:15])
        blocks.append(f"#### {lesson_dir.name} — {title}\n{plan_preview}")

    return "\n\n".join(blocks) if blocks else "(других уроков в lessons/ нет)"


def build_user_prompt(lesson_dir: Path) -> str:
    plan_path = lesson_dir / "plan.md"
    info_path = lesson_dir / "info.json"
    slides_dir = lesson_dir / "slides_json"

    plan = read_file(plan_path)
    plan_blocks = parse_plan_slides(plan)
    slides = read_slides(slides_dir)

    info: dict = {}
    if info_path.exists():
        info = json.loads(read_file(info_path))

    slides_text = "\n\n".join(
        slide_to_text(slide)
        for slide in slides
    )

    count_note = ""
    if len(slides) != len(plan_blocks):
        count_note = (
            f"\n**Внимание:** слайдов в JSON — {len(slides)}, "
            f"пунктов в plan.md — {len(plan_blocks)}.\n"
        )

    return f"""# Урок для рецензии

**Папка:** {lesson_dir.name}
**Тема:** {info.get('topic', lesson_dir.name)}
**Длительность:** {info.get('duration_minutes', '?')} мин
{count_note}
## План урока (plan.md)

{plan}

## Слайды (slides_json/)

{slides_text}

## Другие уроки курса

{other_lessons_context(lesson_dir)}

---
Проведи рецензию по всем пяти критериям. Ответ — markdown по шаблону из system prompt.
"""


def build_prompt(lesson_dir: Path) -> str:
    system = read_file(PROMPT_PATH)
    user = build_user_prompt(lesson_dir)
    return f"{system}\n\n---\n\n{user}"


def extract_markdown_response(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```markdown"):
        start = raw.index("```markdown") + 11
        end = raw.index("```", start)
        return raw[start:end].strip()
    if raw.startswith("```md"):
        start = raw.index("```md") + 5
        end = raw.index("```", start)
        return raw[start:end].strip()
    if raw.startswith("```") and raw.count("```") >= 2:
        start = raw.index("```") + 3
        end = raw.index("```", start)
        return raw[start:end].strip()
    return raw


def save_review(lesson_dir: Path, content: str) -> Path:
    path = lesson_dir / "review.md"
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"Рецензия сохранена: {path}")
    return path


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if len(sys.argv) < 2:
        print("Использование: python agents/lesson_reviewer.py <lesson_dir> [--save [file]]")
        sys.exit(1)

    lesson_dir = Path(sys.argv[1])
    if not lesson_dir.exists():
        print(f"Папка не найдена: {lesson_dir}")
        sys.exit(1)

    plan_path = lesson_dir / "plan.md"
    slides_dir = lesson_dir / "slides_json"
    if not plan_path.exists():
        print(f"plan.md не найден в {lesson_dir}")
        sys.exit(1)
    if not slides_dir.exists() or not list_slide_files(slides_dir):
        print(f"Нет JSON-слайдов в {slides_dir}")
        sys.exit(1)

    if len(sys.argv) >= 3 and sys.argv[2] == "--save":
        if len(sys.argv) >= 4:
            raw = read_file(Path(sys.argv[3]))
        else:
            raw = sys.stdin.read()
        if not raw.strip():
            print("Пустой ответ, рецензия не сохранена.")
            sys.exit(1)
        save_review(lesson_dir, extract_markdown_response(raw))
        return

    print(build_prompt(lesson_dir))
    print(f"\n---\nСохранить: python agents/lesson_reviewer.py {lesson_dir} --save review.md")
    print(f"  (или передать ответ через stdin: ... | python agents/lesson_reviewer.py {lesson_dir} --save)")


if __name__ == "__main__":
    main()
