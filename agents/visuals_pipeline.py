"""
Пайплайн иллюстраций урока: генерация PNG, программная проверка, сборка pptx.

Использование:
    python agents/visuals_pipeline.py <lesson_dir>              # generate + check + pptx
    python agents/visuals_pipeline.py <lesson_dir> --check-only
    python agents/visuals_pipeline.py <lesson_dir> --review    # промпт AI-рецензии визуалов
    python agents/visuals_pipeline.py <lesson_dir> --generate-only
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS = Path(__file__).resolve().parent
PROMPT_PATH = AGENTS / "prompts" / "visuals_reviewer.md"

# Широкие PNG (>1.6) плохо читаются в правой колонке pptx (~5.5″)
MAX_COLUMN_ASPECT = 1.65


def _read_slides(slides_dir: Path) -> list[dict]:
    from slide_utils import read_slides

    return read_slides(slides_dir)


def _image_aspect(path: Path) -> float:
    from PIL import Image

    with Image.open(path) as im:
        w, h = im.size
    return w / h if h else 1.0


def find_generate_script(lesson_dir: Path) -> Path | None:
    script = lesson_dir / "assets" / "generate_visuals.py"
    return script if script.exists() else None


def run_generate_visuals(lesson_dir: Path) -> bool:
    script = find_generate_script(lesson_dir)
    if not script:
        print(f"  [skip] нет {lesson_dir / 'assets' / 'generate_visuals.py'}")
        return False
    print(f"  generate: {script.name}")
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode != 0:
        print(result.stderr or "generate_visuals failed")
        return False
    return True


def check_visuals_quality(lesson_dir: Path) -> list[str]:
    """Программная рецензия: файлы, осиротевшие PNG, aspect, описания."""
    from slide_utils import read_slides

    issues: list[str] = []
    slides_dir = lesson_dir / "slides_json"
    assets_dir = lesson_dir / "assets"
    if not slides_dir.exists():
        return ["нет slides_json/"]

    slides = read_slides(slides_dir)
    referenced: set[str] = set()
    missing_desc: list[str] = []

    for slide in slides:
        title = slide.get("title", "?")
        visuals = slide.get("visuals") or []
        if not visuals and slide.get("type") != "references":
            bullets = slide.get("bullets") or []
            title_l = title.lower()
            skip_no_visual = "чек-лист" in title_l or title_l.startswith("итоги")
            if len(bullets) >= 3 and not slide.get("link") and not skip_no_visual:
                issues.append(
                    f"«{title}»: нет visuals при {len(bullets)} буллетах "
                    "(см. docs/visuals.md — по умолчанию ≥1 иллюстрация)"
                )
        for viz in visuals:
            output = viz.get("output", "")
            if not output:
                issues.append(f"«{title}»: visuals без output")
                continue
            referenced.add(output)
            if not viz.get("description", "").strip():
                missing_desc.append(output)
            path = assets_dir / output
            if not path.exists():
                issues.append(f"«{title}»: отсутствует PNG {output}")
            else:
                asp = _image_aspect(path)
                if asp > MAX_COLUMN_ASPECT:
                    issues.append(
                        f"{output}: aspect {asp:.2f} > {MAX_COLUMN_ASPECT} "
                        "— сожмётся в правой колонке; используйте FIGSIZE_SINGLE "
                        "или (2,1) multi-panel"
                    )

    if missing_desc:
        issues.append(f"нет description в JSON: {', '.join(missing_desc)}")

    if assets_dir.exists():
        for png in sorted(assets_dir.glob("*.png")):
            if png.name not in referenced:
                issues.append(f"orphan PNG (не в slides_json): {png.name}")

    return issues


def run_pptx_builder(lesson_dir: Path) -> bool:
    builder = AGENTS / "pptx_builder.py"
    print(f"  pptx: {lesson_dir.name}")
    result = subprocess.run(
        [sys.executable, str(builder), str(lesson_dir)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode != 0:
        print(result.stderr or "pptx_builder failed")
        return False
    return True


def build_review_prompt(lesson_dir: Path) -> str:
    from slide_utils import read_slides

    system = PROMPT_PATH.read_text(encoding="utf-8")
    slides = read_slides(lesson_dir / "slides_json")
    assets_dir = lesson_dir / "assets"

    blocks: list[str] = []
    for slide in slides:
        title = slide.get("title", "?")
        bullets = slide.get("bullets", [])
        visuals = slide.get("visuals") or []
        if not visuals:
            continue
        viz_lines = []
        for v in visuals:
            out = v.get("output", "")
            desc = v.get("description", "")
            exists = (assets_dir / out).exists() if out else False
            viz_lines.append(f"- `{out}` {'OK' if exists else 'MISSING'}: {desc}")
        blocks.append(
            f"### «{title}»\nБуллеты:\n"
            + "\n".join(f"- {b}" for b in bullets)
            + "\n\nИллюстрации:\n"
            + "\n".join(viz_lines)
        )

    auto_issues = check_visuals_quality(lesson_dir)
    auto_block = (
        "\n".join(f"- {i}" for i in auto_issues)
        if auto_issues
        else "- программных замечаний нет"
    )

    user = f"""# Урок: {lesson_dir.name}

## Слайды с иллюстрациями

{chr(10).join(blocks) if blocks else "(нет visuals)"}

## Автопроверка (visuals_pipeline --check-only)

{auto_block}

---
Проведи рецензию иллюстраций по критериям system prompt.
"""
    return f"{system}\n\n---\n\n{user}"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    lesson_dir = Path(sys.argv[1])
    if not lesson_dir.exists():
        print(f"Папка не найдена: {lesson_dir}")
        sys.exit(1)

    mode = sys.argv[2] if len(sys.argv) >= 3 else "--all"

    if mode == "--review":
        print(build_review_prompt(lesson_dir))
        return

    if mode in ("--generate-only", "--all"):
        if not run_generate_visuals(lesson_dir):
            if mode == "--generate-only":
                sys.exit(1)

    if mode in ("--check-only", "--all"):
        print("\n=== Проверка иллюстраций ===")
        issues = check_visuals_quality(lesson_dir)
        if issues:
            for i in issues:
                print(f"  [warn] {i}")
        else:
            print("  OK: замечаний нет")

    if mode == "--all":
        if not run_pptx_builder(lesson_dir):
            sys.exit(1)
        print("\nГотово: PNG + presentation.pptx")
        if issues := check_visuals_quality(lesson_dir):
            print(f"Осталось {len(issues)} предупреждений — см. --review для AI-рецензии")


if __name__ == "__main__":
    main()
