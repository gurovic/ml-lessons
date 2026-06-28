"""Текст с inline-формулами ($...$) для PowerPoint."""

from __future__ import annotations

import re
from typing import Literal

from lxml import etree

from omml_converter import latex_to_pptx_element

Segment = tuple[Literal["text", "math", "display"], str]

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

# $$...$$ (display), затем $...$ (inline); \$$ — литеральный $
_SEGMENT_RE = re.compile(
    r"\$\$(.+?)\$\$|\$(.+?)\$|\\\$"
)

# **жирный** (markdown); нежадное совпадение
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def iter_bold_chunks(text: str, default_bold: bool = False):
    """Разбивает текст на фрагменты (подстрока, bold). Маркеры ** снимаются."""
    if "**" not in text:
        if text:
            yield text, default_bold
        return

    pos = 0
    for match in _BOLD_RE.finditer(text):
        if match.start() > pos:
            yield text[pos : match.start()], default_bold
        yield match.group(1), True
        pos = match.end()
    if pos < len(text):
        yield text[pos:], default_bold


def parse_segments(text: str) -> list[Segment]:
    if not text:
        return []

    segments: list[Segment] = []
    pos = 0
    for match in _SEGMENT_RE.finditer(text):
        if match.start() > pos:
            segments.append(("text", text[pos:match.start()]))

        if match.group(0) == r"\$":
            segments.append(("text", "$"))
        elif match.group(1) is not None:
            segments.append(("display", match.group(1)))
        else:
            segments.append(("math", match.group(2)))
        pos = match.end()

    if pos < len(text):
        segments.append(("text", text[pos:]))

    return segments


def _clear_paragraph_runs(paragraph) -> None:
    p_el = paragraph._element
    for child in list(p_el):
        if child.tag.endswith("}r") or child.tag.endswith("}m"):
            p_el.remove(child)


def _append_text_run(p_el, text: str, *, font_size, bold, color) -> None:
    from pptx.oxml.ns import qn

    if not text:
        return

    r = etree.SubElement(p_el, qn("a:r"))
    r_pr = etree.SubElement(r, qn("a:rPr"))
    r_pr.set("lang", "ru-RU")
    r_pr.set("dirty", "0")
    sz_val = int(font_size.pt * 100) if font_size is not None else None
    if sz_val is not None:
        r_pr.set("sz", str(sz_val))
    if bold:
        r_pr.set("b", "1")
    if color is not None:
        solid = etree.SubElement(r_pr, qn("a:solidFill"))
        srgb = etree.SubElement(solid, qn("a:srgbClr"))
        srgb.set("val", f"{color[0]:02X}{color[1]:02X}{color[2]:02X}")

    t = etree.SubElement(r, qn("a:t"))
    t.text = text
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def _append_rich_text(
    p_el,
    text: str,
    *,
    font_size,
    bold: bool,
    color,
    warnings: list[str],
) -> None:
    """Текст с **bold** и $...$ в одном фрагменте."""
    for chunk, chunk_bold in iter_bold_chunks(text, default_bold=bold):
        effective_bold = bold or chunk_bold
        for kind, content in parse_segments(chunk):
            if kind == "text":
                _append_text_run(
                    p_el, content, font_size=font_size, bold=effective_bold, color=color
                )
                continue
            try:
                p_el.append(latex_to_pptx_element(content.strip()))
            except Exception as e:
                fallback = f"$${content}$$" if kind == "display" else f"${content}$"
                warnings.append(f"Формула не сконвертирована ({content!r}): {e}")
                _append_text_run(
                    p_el, fallback, font_size=font_size, bold=effective_bold, color=color
                )


def set_paragraph_content(
    paragraph,
    text: str,
    *,
    font_size=None,
    bold: bool = False,
    color=None,
) -> list[str]:
    """Заполняет абзац текстом и OMML-формулами. Возвращает список предупреждений."""
    warnings: list[str] = []
    _clear_paragraph_runs(paragraph)
    p_el = paragraph._element

    for kind, content in parse_segments(text):
        if kind == "text":
            _append_rich_text(
                p_el, content, font_size=font_size, bold=bold, color=color, warnings=warnings
            )
            continue

        try:
            p_el.append(latex_to_pptx_element(content.strip()))
        except Exception as e:
            fallback = f"$${content}$$" if kind == "display" else f"${content}$"
            warnings.append(f"Формула не сконвертирована ({content!r}): {e}")
            _append_text_run(p_el, fallback, font_size=font_size, bold=bold, color=color)

    return warnings


def has_math(text: str) -> bool:
    return any(kind != "text" for kind, _ in parse_segments(text))
