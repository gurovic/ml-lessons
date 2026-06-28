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

# Минимумы для читаемости на слайде (см. docs/visuals.md)
MIN_LABEL_PT = 16
MIN_TITLE_PT = 18
MIN_TICK_PT = 14

TEXT_DARK = "#1a1a1a"
BG_LIGHT = "#ffffff"
BG_BOX = "#eef2ff"

DPI = 200

# Физический размер фигуры в дюймах (до savefig)
FIGSIZE_SINGLE = (5.5, 4.0)
FIGSIZE_DUAL = (11.0, 4.5)
FIGSIZE_TRIPLE = (11.0, 4.0)
FIGSIZE_GRID2X2 = (10.0, 8.0)

# Одна картинка на всю колонку (~5.5″ на слайде)
FONT_SINGLE = {
    "font.size": MIN_LABEL_PT,
    "axes.titlesize": MIN_TITLE_PT,
    "axes.labelsize": MIN_LABEL_PT,
    "xtick.labelsize": MIN_TICK_PT,
    "ytick.labelsize": MIN_TICK_PT,
    "legend.fontsize": MIN_TICK_PT,
    "figure.titlesize": MIN_TITLE_PT + 1,
}

# subplots(1, 2+) или 2×2 — сильнее сжимаются в PPTX → крупнее в исходнике
FONT_COMPACT = {
    "font.size": 20,
    "axes.titlesize": 22,
    "axes.labelsize": 20,
    "xtick.labelsize": 18,
    "ytick.labelsize": 18,
    "legend.fontsize": 18,
    "figure.titlesize": 24,
}

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


def apply_matplotlib_slide_style(*, compact: bool = False) -> None:
    """Применить rcParams: крупный шрифт + светлый фон + тёмный текст."""
    fonts = FONT_COMPACT if compact else FONT_SINGLE
    plt.rcParams.update({**fonts, **CONTRAST})
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


def save_slide_figure(fig, path: Path | str) -> None:
    """Сохранить PNG: белый непрозрачный фон, RGB."""
    path = Path(path)
    fig.savefig(path, dpi=DPI, facecolor=BG_LIGHT, bbox_inches="tight")
    plt.close(fig)
    Image.open(path).convert("RGB").save(path)
