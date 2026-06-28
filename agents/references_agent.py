"""
Агент слайда «Источники и практика»: классические статьи + Colab-ссылки.

Использование:
    python agents/references_agent.py <lesson_dir> --list
    python agents/references_agent.py <lesson_dir> --prompt
    python agents/references_agent.py <lesson_dir> --save [file]
    python agents/references_agent.py <lesson_dir> --apply
"""

import json
import subprocess
import sys
from pathlib import Path

from references_utils import (
    discover_colab_links,
    format_paper_bullet,
    get_git_github_info,
    merge_colab_into_references,
)
from slide_utils import list_slide_files, parse_json_response, save_slide

PROMPT_PATH = Path(__file__).parent / "prompts" / "references_agent.md"
REPO_ROOT = Path(__file__).parent.parent


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_config() -> dict:
    cfg_path = REPO_ROOT / "project_config.json"
    if cfg_path.exists():
        return json.loads(read_file(cfg_path))
    return {}


def find_references_slide_index(slides: list[dict]) -> int | None:
    for i, slide in enumerate(slides):
        if slide.get("type") == "references":
            return i
    return None


def find_references_slide_file(slides_dir: Path) -> Path | None:
    for path in list_slide_files(slides_dir):
        data = json.loads(read_file(path))
        if data.get("type") == "references":
            return path
    return None


def build_user_prompt(lesson_dir: Path) -> str:
    plan_path = lesson_dir / "plan.md"
    info_path = lesson_dir / "info.json"

    plan = read_file(plan_path) if plan_path.exists() else "(plan.md не найден)"
    info: dict = {}
    if info_path.exists():
        info = json.loads(read_file(info_path))

    return f"""# Урок для слайда «Источники и практика»

**Папка:** {lesson_dir.name}
**Тема:** {info.get('topic', lesson_dir.name)}
**Длительность:** {info.get('duration_minutes', '?')} мин

## План урока (plan.md)

{plan}

---
Подбери 3–6 классических статей по JSON-шаблону из system prompt.
Colab-ссылки добавит агент — не включай их в ответ.
"""


def build_prompt(lesson_dir: Path) -> str:
    system = read_file(PROMPT_PATH)
    user = build_user_prompt(lesson_dir)
    return f"{system}\n\n---\n\n{user}"


def build_slide_from_sources(
    lesson_dir: Path,
    papers_slide: dict | None = None,
) -> dict:
    config = load_config()
    colab = discover_colab_links(lesson_dir, REPO_ROOT, config)

    if papers_slide:
        slide = dict(papers_slide)
    else:
        slide = {
            "title": "Источники и практика",
            "type": "references",
            "references": [],
            "bullets": [],
        }

    return merge_colab_into_references(slide, colab)


def cmd_list(lesson_dir: Path) -> None:
    config = load_config()
    gh = get_git_github_info(REPO_ROOT, config)
    colab = discover_colab_links(lesson_dir, REPO_ROOT, config)

    slides_dir = lesson_dir / "slides_json"
    existing = None
    if slides_dir.exists():
        for path in list_slide_files(slides_dir):
            data = json.loads(read_file(path))
            if data.get("type") == "references":
                existing = data
                break

    print(f"Урок: {lesson_dir.name}")
    print(f"GitHub: {gh.get('owner', '?')}/{gh.get('repo', '?')} @ {gh.get('branch', '?')}\n")

    papers = []
    if existing:
        papers = [r for r in existing.get("references", []) if r.get("kind") == "paper"]

    if papers:
        print(f"Статьи ({len(papers)}):")
        for ref in papers:
            print(f"  • {format_paper_bullet(ref)}")
            if ref.get("url"):
                print(f"    {ref['url']}")
    else:
        print("Статьи: (нет — запустите --prompt и --save)")

    print()
    if colab:
        print(f"Colab ({len(colab)}):")
        for entry in colab:
            print(f"  • {entry.get('label', entry['title'])}: {entry['url']}")
    else:
        print("Colab: нет ноутбуков или не удалось определить GitHub remote.")


def cmd_save(lesson_dir: Path, raw: str) -> Path:
    data = parse_json_response(raw)
    if data.get("type") != "references":
        data["type"] = "references"
    slide = build_slide_from_sources(lesson_dir, data)
    out = lesson_dir / "references.json"
    out.write_text(json.dumps(slide, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Слайд сохранён: {out}")
    n_papers = sum(1 for r in slide.get("references", []) if r.get("kind") == "paper")
    n_colab = sum(1 for r in slide.get("references", []) if r.get("kind") == "colab")
    print(f"  статей: {n_papers}, Colab: {n_colab}")
    return out


def cmd_apply(lesson_dir: Path) -> None:
    slides_dir = lesson_dir / "slides_json"
    if not slides_dir.exists():
        print(f"slides_json не найден: {slides_dir}")
        sys.exit(1)

    ref_path = find_references_slide_file(slides_dir)
    refs_json = lesson_dir / "references.json"

    papers_slide = None
    if refs_json.exists():
        papers_slide = json.loads(read_file(refs_json))
    elif ref_path:
        papers_slide = json.loads(read_file(ref_path))

    slide = build_slide_from_sources(lesson_dir, papers_slide)

    if ref_path:
        slide_num = int(ref_path.stem)
        save_slide(slides_dir, slide, slide_num)
    else:
        slide_num = len(list_slide_files(slides_dir)) + 1
        save_slide(slides_dir, slide, slide_num)

    builder = Path(__file__).parent / "pptx_builder.py"
    print("\nПересборка presentation.pptx...")
    subprocess.run(
        [sys.executable, str(builder), str(lesson_dir)],
        cwd=REPO_ROOT,
        check=False,
    )


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if len(sys.argv) < 2:
        print(
            "Использование: python agents/references_agent.py <lesson_dir> "
            "[--list | --prompt | --save [file] | --apply]"
        )
        sys.exit(1)

    lesson_dir = Path(sys.argv[1])
    if not lesson_dir.exists():
        print(f"Папка не найдена: {lesson_dir}")
        sys.exit(1)

    if len(sys.argv) >= 3 and sys.argv[2] == "--list":
        cmd_list(lesson_dir)
        return

    if len(sys.argv) >= 3 and sys.argv[2] == "--prompt":
        plan_path = lesson_dir / "plan.md"
        if not plan_path.exists():
            print(f"plan.md не найден в {lesson_dir}")
            sys.exit(1)
        print(build_prompt(lesson_dir))
        print(f"\n---\nСохранить: python agents/references_agent.py {lesson_dir} --save references.json")
        return

    if len(sys.argv) >= 3 and sys.argv[2] == "--save":
        if len(sys.argv) >= 4:
            raw = read_file(Path(sys.argv[3]))
        else:
            raw = sys.stdin.read()
        if not raw.strip():
            print("Пустой ответ, слайд не сохранён.")
            sys.exit(1)
        try:
            cmd_save(lesson_dir, raw)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Ошибка разбора ответа: {e}")
            sys.exit(1)
        return

    if len(sys.argv) >= 3 and sys.argv[2] == "--apply":
        cmd_apply(lesson_dir)
        return

    print(
        "Укажите режим: --list, --prompt, --save [file] или --apply"
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
