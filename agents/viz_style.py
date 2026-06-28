"""Стиль matplotlib для иллюстраций на слайдах PPTX.

Согласован с pptx_builder: буллеты Pt(20), заголовок Pt(32).
Иллюстрация в правой колонке (~5.5″) или в широкой полосе (~7.8″) —
шрифт в PNG задаём так, чтобы после масштабирования читалось сравнимо с текстом слайда.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image

# Эталон из agents/pptx_builder.py
SLIDE_BODY_PT = 20
SLIDE_TITLE_PT = 32

# Единая шкала шрифтов для всех иллюстраций (см. docs/visuals.md).
# Чуть выше pt слайда: PNG масштабируется в правой колонке (~5.5″).
FONT_LABEL = 18
FONT_TITLE = 20
FONT_TICK = 14
FONT_LEGEND = 14
FONT_ANNOT = 14  # подписи на графике, annotate, bar labels
FONT_HEATMAP = 12  # текст в ячейках heatmap (мало места)
FONT_DIAGRAM = 16  # блоки block-схем, graphviz-узлы
FONT_SYMBOL = 22  # крупные символы ✓/✗ на схемах

TEXT_DARK = "#1a1a1a"
BG_LIGHT = "#ffffff"
BG_BOX = "#eef2ff"

DPI = 200

# Физический размер фигуры в дюймах (до savefig)
#
# Правая колонка PPTX (~5.5″): одна панель или multi-panel в столбик (2,1) / (3,1).
# Полоса под текстом на всю ширину: панели в ряд (1,2) / (1,3) или FIGSIZE_WIDE_SINGLE.

FIGSIZE_SINGLE = (5.5, 4.0)

# Multi-panel в правой колонке: subplots(2, 1) / (3, 1) — умеренная высота, меньше сжатия в PPTX
FIGSIZE_DUAL_COL = (5.5, 5.8)
FIGSIZE_TRIPLE_COL = (5.5, 7.8)
COL_HSPACE = 0.55

# Multi-panel на всю ширину под текстом: subplots(1, 2) / (1, 3)
FIGSIZE_DUAL_ROW = (11.5, 3.6)
FIGSIZE_TRIPLE_ROW = (11.5, 3.3)
ROW_WSPACE = 0.32
FIGSIZE_WIDE_SINGLE = (11.5, 3.6)

# Обратная совместимость (алиасы старых имён)
FIGSIZE_DUAL = FIGSIZE_DUAL_ROW
FIGSIZE_DUAL_STACK = FIGSIZE_DUAL_COL
STACK_HSPACE = COL_HSPACE
FIGSIZE_TRIPLE = FIGSIZE_TRIPLE_ROW
FIGSIZE_GRID2X2 = (10.0, 8.0)

FONT_SLIDE = {
    "font.size": FONT_LABEL,
    "axes.titlesize": FONT_TITLE,
    "axes.labelsize": FONT_LABEL,
    "xtick.labelsize": FONT_TICK,
    "ytick.labelsize": FONT_TICK,
    "legend.fontsize": FONT_LEGEND,
    "figure.titlesize": FONT_TITLE,
}

# Алиасы (deprecated names — те же значения, что FONT_SLIDE)
FONT_SINGLE = FONT_SLIDE
FONT_COMPACT = FONT_SLIDE

CONTRAST = {
    "figure.facecolor": BG_LIGHT,
    "axes.facecolor": BG_LIGHT,
    "savefig.facecolor": BG_LIGHT,
    "text.color": TEXT_DARK,
    "axes.labelcolor": TEXT_DARK,
    "axes.edgecolor": "#444444",
    "axes.titlecolor": TEXT_DARK,
    "xtick.color": TEXT_DARK,
    "ytick.color": TEXT_DARK,
    "grid.color": "#cccccc",
}


def legend_kwargs(**extra) -> dict:
    """Стандартные kwargs для ax.legend() на слайдах."""
    return {
        "fontsize": FONT_LEGEND,
        "framealpha": 0.92,
        "borderpad": 0.35,
        "labelspacing": 0.35,
        "handlelength": 1.4,
        **extra,
    }


def apply_matplotlib_slide_style(*, compact: bool = False) -> None:
    """Применить rcParams: единый шрифт + светлый фон + тёмный текст.

    Аргумент ``compact`` сохранён для обратной совместимости и не меняет шрифты.
    """
    _ = compact
    plt.rcParams.update({**FONT_SLIDE, **CONTRAST})
    plt.rcParams["figure.dpi"] = DPI
    plt.rcParams["savefig.dpi"] = DPI


def style_axes(ax, *, facecolor: str = BG_LIGHT) -> None:
    """Явно задать фон оси и цвет подписей (защита от тёмных тем matplotlib)."""
    ax.set_facecolor(facecolor)
    ax.title.set_color(TEXT_DARK)
    ax.xaxis.label.set_color(TEXT_DARK)
    ax.yaxis.label.set_color(TEXT_DARK)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(TEXT_DARK)


def heatmap_text_color(value: float, vmin: float = 0.0, vmax: float = 1.0) -> str:
    """Цвет текста на heatmap: светлый на тёмной ячейке, тёмный на светлой."""
    t = (value - vmin) / (vmax - vmin) if vmax > vmin else 0.5
    return "#ffffff" if t > 0.55 else TEXT_DARK


def save_slide_figure(fig, path: Path | str, *, tight: bool = True) -> None:
    """Сохранить PNG: белый непрозрачный фон, RGB."""
    path = Path(path)
    fig.savefig(
        path,
        dpi=DPI,
        facecolor=BG_LIGHT,
        bbox_inches="tight" if tight else None,
    )
    plt.close(fig)
    Image.open(path).convert("RGB").save(path)
