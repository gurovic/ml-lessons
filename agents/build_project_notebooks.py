"""Сборка project.ipynb для уроков ML (narrative pipeline)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents"))
from notebook_utils import build_ipynb, save_ipynb  # noqa: E402
from narrative_project_sections import (  # noqa: E402
    sections_derevo,
    sections_linear,
    sections_logistic,
)


def build_all() -> None:
    lessons = [
        (ROOT / "lessons" / "lineynaya_regressiya", "Линейная регрессия — мини-проект", sections_linear()),
        (ROOT / "lessons" / "logisticheskaya_regressiya", "Логистическая регрессия — мини-проект", sections_logistic()),
        (ROOT / "lessons" / "derevo_resheniy", "Дерево решений — мини-проект", sections_derevo()),
    ]
    for lesson_dir, topic, sections in lessons:
        nb = build_ipynb(sections, topic=topic)
        nb["cells"][0]["source"] = [
            f"# {topic}\n",
            "\n",
            "Сквозной мини-проект: один датасет, решения передаются между этапами.\n",
        ]
        out = lesson_dir / "project.ipynb"
        save_ipynb(out, nb)
        print(f"Saved {out} ({len(sections)} sections, {len(nb['cells'])} cells)")


if __name__ == "__main__":
    build_all()
