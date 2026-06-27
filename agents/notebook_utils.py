"""Отбор слайдов для ноутбука и сборка code.ipynb."""

import json
import re
from pathlib import Path
from typing import Any

from slide_utils import parse_json_response

THEORY_TITLE_MARKERS = (
    "почему нам важна",
    "почему мы строим",
    "почему в узле",
    "зачем дерево",
    "джини или энтропия",
    "классические алгоритмы",
    "многоклассовая классификация без",
)

MOTIVATION_TITLE_MARKERS = (
    "от игры к математике",
    "акинатор",
)

STRONG_TEXT_MARKERS = (
    "jupyter",
    "notebook",
    "ipywidgets",
    "sklearn",
    "эксперимент",
    "сравни",
    "сравнен",
    "замер",
    "скорост",
    "время работы",
    "демо кода",
)

API_MARKERS = (
    "DecisionTree",
    "plot_tree",
    "export_graphviz",
    "export_text",
    "class_weight",
    ".fit(",
    "feature_importances",
    "train_test_split",
    "cross_val",
    "GridSearch",
)

VIZ_LIB_MARKERS = (
    "matplotlib",
    "seaborn",
    "graphviz",
    "plotly",
    "ipywidgets",
    "интерактив",
)


def _slide_text(slide: dict) -> str:
    parts = slide.get("bullets", []) + [slide.get("notes", "")]
    for v in slide.get("visuals", []):
        parts.append(v.get("description", ""))
    nb = slide.get("notebook")
    if isinstance(nb, dict) and nb.get("hint"):
        parts.append(str(nb["hint"]))
    return "\n".join(p for p in parts if p)


def _title_lower(slide: dict) -> str:
    return slide.get("title", "").lower()


def notebook_config(slide: dict) -> dict[str, Any] | None:
    """Вернуть конфиг ноутбука для слайда или None, если слайд пропускаем."""
    nb = slide.get("notebook")
    if nb is False:
        return None
    if isinstance(nb, dict) and nb.get("include") is False:
        return None
    if nb is True or (isinstance(nb, dict) and nb.get("include") is True):
        cfg = dict(nb) if isinstance(nb, dict) else {}
        cfg.setdefault("include", True)
        cfg.setdefault("reason", "explicit")
        return cfg

    title = _title_lower(slide)
    if any(m in title for m in MOTIVATION_TITLE_MARKERS):
        return None
    if any(m in title for m in THEORY_TITLE_MARKERS):
        return None

    text = _slide_text(slide)
    text_lower = text.lower()
    has_api = any(m in text for m in API_MARKERS)
    has_strong = any(m in text_lower for m in STRONG_TEXT_MARKERS)
    has_viz = bool(slide.get("visuals"))
    has_viz_code = has_viz and any(m in text_lower for m in VIZ_LIB_MARKERS)
    notes_lower = slide.get("notes", "").lower()
    notes_want_code = "jupyter" in notes_lower or "notebook" in notes_lower

    reasons: list[str] = []
    if has_api:
        reasons.append("api")
    if has_strong:
        reasons.append("keywords")
    if has_viz_code:
        reasons.append("visuals")
    if notes_want_code:
        reasons.append("notes_jupyter")

    if not reasons:
        return None

    kinds: list[str] = []
    if has_api:
        kinds.append("example")
    if any(w in text_lower for w in ("сравни", "сравнен", "скорост", "время", "эксперимент")):
        kinds.append("experiment")
    if has_viz_code:
        kinds.append("viz")
    if "ipywidgets" in text_lower or "интерактив" in text_lower or "слайдер" in text_lower:
        kinds.append("interactive")
    if not kinds:
        kinds = ["example"] if has_api else ["viz"]

    return {"include": True, "reason": "+".join(reasons), "kinds": kinds}


def select_slides_for_notebook(slides: list[dict]) -> list[tuple[int, dict, dict]]:
    """(номер слайда 1-based, slide, config)."""
    selected = []
    for i, slide in enumerate(slides, 1):
        cfg = notebook_config(slide)
        if cfg:
            selected.append((i, slide, cfg))
    return selected


def slide_to_notebook_context(index: int, slide: dict, cfg: dict) -> str:
    title = slide.get("title", "")
    lines = [f"### Слайд {index:02d}: «{title}»"]
    lines.append(f"_Отбор:_ {cfg.get('reason', '?')}; _типы:_ {', '.join(cfg.get('kinds', ['example']))}")
    if cfg.get("hint"):
        lines.append(f"_Подсказка автора:_ {cfg['hint']}")
    for bullet in slide.get("bullets", []):
        lines.append(f"- {bullet}")
    if slide.get("notes"):
        lines.append(f"_Заметки преподавателя:_ {slide['notes']}")
    for v in slide.get("visuals", []):
        out = v.get("output", "")
        exists = f" (файл assets/{out})" if out else ""
        lines.append(f"_Визуализация{exists}:_ {v.get('description', '')}")
    return "\n".join(lines)


def _normalize_source(source: str | list[str]) -> list[str]:
    if isinstance(source, list):
        return [line if line.endswith("\n") else line + "\n" for line in source]
    if not source:
        return []
    return [line + "\n" for line in source.split("\n")]


def _make_cell(cell_type: str, source: str | list[str]) -> dict:
    return {
        "cell_type": cell_type,
        "metadata": {},
        "source": _normalize_source(source),
    }


def default_setup_cell() -> dict:
    source = """\
# Практика к уроку — выполняйте ячейки по порядку
%matplotlib inline

import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
"""
    return _make_cell("code", source)


def build_ipynb(
    sections: list[dict],
    topic: str = "Урок",
    setup: bool = True,
) -> dict:
    cells: list[dict] = []
    if setup:
        cells.append(
            _make_cell(
                "markdown",
                f"# {topic}\n\nПрактические ячейки к слайдам презентации. "
                "Заголовки секций совпадают с заголовками слайдов.",
            )
        )
        cells.append(default_setup_cell())

    for section in sections:
        title = section.get("slide_title", "Без названия")
        kind = section.get("kind", "")
        header = f"## {title}"
        if kind:
            header += f" `({kind})`"
        cells.append(_make_cell("markdown", header))
        for cell in section.get("cells", []):
            ctype = cell.get("type", "code")
            if ctype not in ("markdown", "code"):
                ctype = "code"
            cells.append(_make_cell(ctype, cell.get("source", "")))

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def parse_notebook_response(raw: str) -> dict:
    data = parse_json_response(raw)
    if not isinstance(data, dict):
        raise ValueError("Ответ должен быть JSON-объектом")
    if "sections" not in data:
        raise ValueError("В ответе нет поля sections")
    if not isinstance(data["sections"], list):
        raise ValueError("sections должен быть массивом")
    return data


def save_ipynb(path: Path, notebook: dict) -> Path:
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def list_assets(lesson_dir: Path) -> list[str]:
    assets = lesson_dir / "assets"
    if not assets.exists():
        return []
    return sorted(p.name for p in assets.glob("*") if p.is_file() and p.suffix.lower() in (".png", ".svg", ".jpg"))
