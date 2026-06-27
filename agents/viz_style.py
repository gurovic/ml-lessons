"""Стиль matplotlib для иллюстраций на слайдах PPTX.

Согласован с pptx_builder: буллеты Pt(20), заголовок Pt(32).
Иллюстрация в правой колонке (~4.75″) или в ячейке сетки 2×2 (~2.3″) —
шрифт в PNG задаём так, чтобы после масштабирования читалось сравнимо с текстом слайда.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image

# Эталон из agents/pptx_builder.py
SLIDE_BODY_PT = 20
SLIDE_TITLE_PT = 32

TEXT_DARK = "#1a1a1a"
BG_LIGHT = "#ffffff"
BG_BOX = "#eef2ff"

# Одна картинка на всю колонку
FONT_SINGLE = {
    "font.size": 14,
    "axes.titlesize": 15,
    "axes.labelsize": 14,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "legend.fontsize": 13,
    "figure.titlesize": 16,
}

# subplots(1, 2) или 2×2 на слайде — сильнее сжимаются → крупнее в исходнике
FONT_COMPACT = {
    "font.size": 15,
    "axes.titlesize": 16,
    "axes.labelsize": 15,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 14,
    "figure.titlesize": 17,
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
    plt.rcParams["figure.dpi"] = 150
    plt.rcParams["savefig.dpi"] = 150


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
    fig.savefig(path, dpi=150, facecolor=BG_LIGHT, bbox_inches="tight")
    plt.close(fig)
    Image.open(path).convert("RGB").save(path)
