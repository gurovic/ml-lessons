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
    source = enforce_code_line_lengths(source)
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


def count_code_lines(source: str, *, max_len: int | None = None) -> int:
    return len(normalize_code_lines(source, max_len=max_len))


def _split_source_lines(source: str) -> list[str]:
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    return lines if lines else [""]


def normalize_code_lines(source: str, *, max_len: int | None = None) -> list[str]:
    """Строки кода без хвостовых пустых переносов; опционально — перенос длинных строк."""
    lines = _split_source_lines(source)
    if max_len is None:
        return lines
    out: list[str] = []
    for line in lines:
        out.extend(wrap_code_line(line, max_len))
    return out if out else [""]


# Высота блока кода — должна совпадать с _render_code_examples в pptx_builder
CODE_FONT_PT = 11
CODE_LINE_H = CODE_FONT_PT / 72.0  # одна строка = высота шрифта
CODE_PAD_TOP = 0.05
CODE_PAD_BOTTOM = CODE_LINE_H  # одна пустая строка под последней строкой
CODE_PAD_X = 0.08
CODE_BLOCK_GAP = 0.06
CODE_CAPTION_H = 0.24
CODE_BLOCK_TAIL = 0.04
# Consolas в pptx: ~0.58 em ширины на pt; запас под длинные идентификаторы sklearn
CODE_CHAR_WIDTH_RATIO = 0.58
# Узкая колонка (BODY_WIDTH_VIS − 0.1): ~60 символов; см. max_code_line_length_for_width
CODE_MAX_LINE_LEN = 60


def max_code_line_length_for_width(code_width_inches: float) -> int:
    """Макс. символов в строке кода для заданной ширины блока (дюймы)."""
    inner = max(code_width_inches - 2 * CODE_PAD_X, 1.0)
    chars = int(inner * 72 / CODE_FONT_PT / CODE_CHAR_WIDTH_RATIO * 0.82)
    return max(24, min(chars, 120))


def _split_comma_items(text: str) -> list[str]:
    """Разбить по запятым верхнего уровня (внутри скобок)."""
    parts: list[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(depth - 1, 0)
        elif ch == "," and depth == 0:
            parts.append(text[start:i].strip())
            start = i + 1
    tail = text[start:].strip()
    if tail or not parts:
        parts.append(tail)
    return parts


def _wrap_call_or_container(line: str, max_len: int) -> list[str] | None:
    """Перенос вызова/контейнера: foo = Bar(...), from x import a, b, c."""
    stripped = line.strip()
    lead = len(line) - len(stripped)
    indent = line[:lead]
    cont = indent + "    "

    if stripped.startswith("from ") and " import " in stripped:
        head, tail = stripped.split(" import ", 1)
        prefix = f"{head} import "
        if len(indent + prefix) <= max_len and "," in tail:
            items = _split_comma_items(tail)
            if len(items) > 1:
                lines = [indent + prefix + "("]
                for j, item in enumerate(items):
                    suffix = "," if j < len(items) - 1 else ")"
                    lines.append(cont + item + suffix)
                if all(len(row) <= max_len for row in lines):
                    return lines

    eq = stripped.find("=")
    if eq <= 0:
        return None
    lhs = stripped[:eq].strip()
    rhs = stripped[eq + 1 :].lstrip()
    if not rhs:
        return None

    paren_open = rhs.find("(")
    if paren_open >= 0 and rhs.endswith(")"):
        func_head = rhs[: paren_open + 1]
        inner = rhs[paren_open + 1 : -1]
        head = indent + lhs + " = " + func_head
        if len(head) <= max_len and "," in inner:
            list_open = inner.startswith("[") and inner.endswith("]")
            if list_open:
                head = head + "["
                inner_items = _split_comma_items(inner[1:-1])
                close_suffix = "])"
            else:
                inner_items = _split_comma_items(inner)
                close_suffix = ")"
            if len(inner_items) > 1:
                lines = [head]
                for j, item in enumerate(inner_items):
                    suffix = "," if j < len(inner_items) - 1 else close_suffix
                    row = cont + item + suffix
                    if len(row) > max_len:
                        return None
                    lines.append(row)
                return lines

    open_ch = rhs[0] if rhs[0] in "([{" else ""
    if not open_ch:
        return None
    close_map = {"(": ")", "[": "]", "{": "}"}
    close_ch = close_map[open_ch]
    if not rhs.endswith(close_ch) or len(rhs) < 2:
        return None

    inner = rhs[1:-1]
    head = indent + lhs + " = " + open_ch
    if len(head) > max_len:
        return None

    items = _split_comma_items(inner)
    if len(items) <= 1:
        return None

    lines = [head]
    for j, item in enumerate(items):
        suffix = "," if j < len(items) - 1 else close_ch
        row = cont + item + suffix
        if len(row) > max_len:
            return None
        lines.append(row)
    return lines


def wrap_code_line(line: str, max_len: int) -> list[str]:
    """Разбить длинную строку: скобки, запятые, затем пробел."""
    if len(line) <= max_len:
        return [line]

    wrapped = _wrap_call_or_container(line, max_len)
    if wrapped:
        return wrapped

    lead = len(line) - len(line.lstrip())
    indent = line[:lead]
    cont = indent + "    "
    text = line.strip()
    if len(indent + text) <= max_len:
        return [line]

    words = text.split(" ")
    if len(words) > 1:
        rows: list[str] = []
        current = indent + words[0]
        for word in words[1:]:
            candidate = current + " " + word
            if len(candidate) <= max_len:
                current = candidate
            else:
                rows.append(current)
                current = cont + word
        rows.append(current)
        if all(len(row) <= max_len for row in rows):
            return rows

    out: list[str] = []
    chunk = indent
    for ch in text:
        if len(chunk) + 1 > max_len and chunk.strip():
            out.append(chunk.rstrip())
            chunk = cont + ch
        else:
            chunk += ch
    if chunk:
        out.append(chunk.rstrip())
    return out if out else [line[:max_len]]


def enforce_code_line_lengths(
    source: str,
    *,
    max_len: int = CODE_MAX_LINE_LEN,
) -> str:
    """Нормализовать переносы и уложить строки в лимит ширины блока кода."""
    lines = normalize_code_lines(source, max_len=max_len)
    return "\n".join(lines)


def apply_tight_code_paragraph(paragraph) -> None:
    """Одна строка в своём textbox — без межстрочного интервала."""
    from pptx.util import Pt

    paragraph.space_before = Pt(0)
    paragraph.space_after = Pt(0)
    paragraph.level = 0


def _single_code_block_height(n_lines: int, *, has_caption: bool) -> float:
    n = max(n_lines, 1)
    h = CODE_PAD_TOP + CODE_LINE_H * n + CODE_PAD_BOTTOM
    h += CODE_BLOCK_GAP
    if has_caption:
        h += CODE_CAPTION_H
    h += CODE_BLOCK_TAIL
    return h


def measure_code_block_height_inches(
    examples: list[dict],
    *,
    code_width: float | None = None,
) -> float:
    """Высота блока кода в дюймах — совпадает с _render_code_examples в pptx_builder."""
    max_len = (
        max_code_line_length_for_width(code_width)
        if code_width is not None
        else CODE_MAX_LINE_LEN
    )
    total = 0.0
    for block in examples:
        source = block.get("source", "")
        if not source:
            continue
        n_lines = len(normalize_code_lines(source, max_len=max_len))
        total += _single_code_block_height(n_lines, has_caption=bool(block.get("caption")))
    return total


def estimate_code_height_inches(
    examples: list[dict],
    *,
    code_width: float | None = None,
) -> float:
    """Оценка высоты блока кода в дюймах для pptx."""
    h = measure_code_block_height_inches(examples, code_width=code_width)
    return h if h else 0.0
