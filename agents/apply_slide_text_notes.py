"""Перенос текста из lessons/<slug>/slide_text.md в notes слайдов JSON."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_slide_text(md_path: Path) -> dict[int, str]:
    text = md_path.read_text(encoding="utf-8")
    blocks = re.split(r"\n## Слайд (\d+)\.", text)
    out: dict[int, str] = {}
    for i in range(1, len(blocks), 2):
        num = int(blocks[i])
        body = blocks[i + 1].strip()
        # убрать заголовок (первая строка до пустой)
        parts = body.split("\n\n", 1)
        if len(parts) == 2 and "\n" not in parts[0].strip()[:80]:
            body = parts[1].strip()
        body = re.sub(r"\n---\s*$", "", body).strip()
        out[num] = body
    return out


def apply(lesson_dir: Path) -> None:
    md_path = lesson_dir / "slide_text.md"
    if not md_path.exists():
        raise SystemExit(f"Нет файла: {md_path}")
    notes_by_num = parse_slide_text(md_path)
    slides_dir = lesson_dir / "slides_json"
    for path in sorted(slides_dir.glob("[0-9][0-9].json"), key=lambda p: int(p.stem)):
        num = int(path.stem)
        if num not in notes_by_num:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("type") == "references":
            continue
        data["notes"] = notes_by_num[num]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  {path.name}: notes обновлены")
    print(f"Готово: {len(notes_by_num)} слайдов")


def main() -> None:
    lesson = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "lessons" / "vizualizatsiya"
    apply(lesson)
    if "--pptx" in sys.argv:
        subprocess.run(
            [sys.executable, str(ROOT / "agents" / "pptx_builder.py"), str(lesson)],
            cwd=ROOT,
            check=True,
        )


if __name__ == "__main__":
    main()
