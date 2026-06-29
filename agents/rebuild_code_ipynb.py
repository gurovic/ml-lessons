"""Пересборка code.ipynb из существующего ноутбука (нормализация setup и секций)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents"))

from notebook_utils import build_ipynb, save_ipynb  # noqa: E402
from slide_utils import read_slides  # noqa: E402


def _source_text(cell: dict) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return src


def _parse_section_header(text: str) -> tuple[str, str]:
    m = re.match(r"^##\s+(.+?)(?:\s+`\(([^)]+)\)`)?\s*$", text.strip())
    if not m:
        return text.strip(), ""
    return m.group(1).strip(), m.group(2) or ""


def ipynb_to_sections(nb: dict) -> list[dict]:
    sections: list[dict] = []
    current: dict | None = None

    for cell in nb.get("cells", []):
        text = _source_text(cell)
        if cell["cell_type"] == "markdown" and text.strip().startswith("## "):
            if current:
                sections.append(current)
            title, kind = _parse_section_header(text)
            current = {"slide_title": title, "kind": kind, "cells": []}
            continue
        if current is None:
            continue
        if cell["cell_type"] == "code":
            source = text.strip()
            if source:
                current["cells"].append({"type": "code", "source": source})
        elif cell["cell_type"] == "markdown" and text.strip():
            current["cells"].append({"type": "markdown", "source": text})

    if current:
        sections.append(current)
    return sections


def rebuild(lesson_dir: Path) -> None:
    code_path = lesson_dir / "code.ipynb"
    if not code_path.exists():
        print(f"Нет {code_path}, пропуск.")
        return

    nb = json.loads(code_path.read_text(encoding="utf-8"))
    sections = ipynb_to_sections(nb)

    info_path = lesson_dir / "info.json"
    topic = lesson_dir.name
    if info_path.exists():
        topic = json.loads(info_path.read_text(encoding="utf-8")).get("topic", topic)

    new_nb = build_ipynb(sections, topic=topic, setup=True)

    save_ipynb(code_path, new_nb)
    slides = read_slides(lesson_dir / "slides_json")
    print(f"Пересобран {code_path}: {len(sections)} секций, {len(new_nb['cells'])} ячеек (слайдов в JSON: {len(slides)})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python agents/rebuild_code_ipynb.py <lesson_dir>")
        sys.exit(1)
    rebuild(Path(sys.argv[1]))
