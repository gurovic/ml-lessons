"""Отбор слайдов для code_examples, merge и разбор ответа AI."""

from __future__ import annotations

import re
from typing import Any

from slide_utils import parse_json_response

API_MARKERS = (
    "sklearn",
    "pandas",
    "DecisionTree",
    "LinearRegression",
    "LogisticRegression",
    "StandardScaler",
    "Pipeline",
    "train_test_split",
    "cross_val",
    "GridSearch",
    "plot_tree",
    "plt.",
    "sns.",
    "seaborn",
    "matplotlib",
    "pd.",
    "np.",
    "DataFrame",
    "Series",
    ".fit(",
    ".predict(",
    "value_counts",
    "groupby",
    "merge(",
    "concat(",
    "read_csv",
    "read_parquet",
    "OneHotEncoder",
    "mean_absolute_error",
    "r2_score",
    "roc_curve",
    "confusion_matrix",
)

SKIP_TYPES = ("references",)


def _has_api_in_bullets(slide: dict) -> bool:
    text = "\n".join(slide.get("bullets", []))
    return any(m in text for m in API_MARKERS)


def _notebook_include(slide: dict) -> bool:
    nb = slide.get("notebook")
    if nb is True:
        return True
    if isinstance(nb, dict) and nb.get("include") is True:
        return True
    return False


def has_code_examples(slide: dict) -> bool:
    examples = slide.get("code_examples")
    return isinstance(examples, list) and len(examples) > 0


def should_enrich_slide(slide: dict) -> bool:
    if slide.get("type") in SKIP_TYPES:
        return False
    if has_code_examples(slide):
        return False
    if _notebook_include(slide):
        return True
    return _has_api_in_bullets(slide)


def select_slides_for_code(
    slides: list[dict],
) -> list[tuple[int, dict]]:
    """(номер слайда 1-based, slide)."""
    return [
        (i, slide)
        for i, slide in enumerate(slides, 1)
        if should_enrich_slide(slide)
    ]


def slide_to_code_context(index: int, slide: dict) -> str:
    title = slide.get("title", "")
    lines = [f"### Слайд {index:02d}: «{title}»"]
    nb = slide.get("notebook")
    if isinstance(nb, dict) and nb.get("hint"):
        lines.append(f"_Подсказка:_ {nb['hint']}")
    for bullet in slide.get("bullets", []):
        lines.append(f"- {bullet}")
    if slide.get("notes"):
        lines.append(f"_Заметки:_ {slide['notes']}")
    return "\n".join(lines)


def normalize_code_example(item: dict) -> dict:
    source = item.get("source", "")
    if isinstance(source, list):
        source = "".join(source)
    source = source.strip()
    if not source:
        raise ValueError("code_examples[].source не может быть пустым")
    out: dict[str, Any] = {"source": source}
    caption = item.get("caption")
    if caption:
        out["caption"] = str(caption).strip()
    return out


def merge_code_examples(slide: dict, examples: list[dict]) -> dict:
    merged = dict(slide)
    normalized = [normalize_code_example(ex) for ex in examples]
    merged["code_examples"] = normalized
    return merged


def parse_slide_code_response(raw: str) -> dict:
    data = parse_json_response(raw)
    if not isinstance(data, dict):
        raise ValueError("Ответ должен быть JSON-объектом")
    slides = data.get("slides")
    if not isinstance(slides, list):
        raise ValueError("В ответе нет поля slides (массив)")
    for entry in slides:
        if "code_examples" not in entry:
            raise ValueError(f"Нет code_examples у слайда {entry.get('slide_index')}")
        if not isinstance(entry["code_examples"], list):
            raise ValueError("code_examples должен быть массивом")
    return data


def apply_response_to_slides(
    slides: list[dict],
    response: dict,
    *,
    strict_title: bool = True,
) -> tuple[list[dict], list[str]]:
    """Возвращает (обновлённые slides, предупреждения)."""
    updated = [dict(s) for s in slides]
    warnings: list[str] = []

    for entry in response.get("slides", []):
        idx = entry.get("slide_index")
        if idx is None:
            warnings.append("Пропущена запись без slide_index")
            continue
        if not (1 <= idx <= len(updated)):
            warnings.append(f"slide_index {idx} вне диапазона")
            continue
        slide = updated[idx - 1]
        expected_title = entry.get("title", "")
        actual_title = slide.get("title", "")
        if strict_title and expected_title and expected_title != actual_title:
            warnings.append(
                f"Слайд {idx}: title не совпадает "
                f"(ожидали «{expected_title}», в JSON «{actual_title}»)"
            )
        try:
            updated[idx - 1] = merge_code_examples(
                slide, entry["code_examples"]
            )
        except ValueError as e:
            warnings.append(f"Слайд {idx}: {e}")

    return updated, warnings


def count_code_lines(source: str) -> int:
    return len([ln for ln in source.split("\n") if ln.strip()])


def measure_code_block_height_inches(examples: list[dict]) -> float:
    """Высота блока кода в дюймах — совпадает с _render_code_examples в pptx_builder."""
    total = 0.0
    for block in examples:
        source = block.get("source", "")
        if not source:
            continue
        n_lines = max(len(source.split("\n")), 1)
        total += 0.17 * n_lines + 0.10 + 0.06
        if block.get("caption"):
            total += 0.24
        total += 0.04
    return total


def estimate_code_height_inches(examples: list[dict]) -> float:
    """Оценка высоты блока кода в дюймах для pptx."""
    h = measure_code_block_height_inches(examples)
    return h if h else 0.0
