"""Стиль matplotlib для иллюстраций на слайдах PPTX (правая колонка ~5.5″).

Эталон пропорций: слайд 14 (pipeline_leakage) — FONT_DIAGRAM в блоках, компактный FONT_TITLE.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image

SLIDE_BODY_PT = 20
SLIDE_TITLE_PT = 32

# Шкала (после масштабирования в колонке ~5.5″)
FONT_LABEL = 13   # подписи осей
FONT_TITLE = 11   # заголовок панели — меньше осей (как на слайде 14)
TITLE_PAD = 20    # «воздух» между заголовком и областью графика (было 28, −30%)
TITLE_AX_SHRINK = 0.93  # dual-panel: меньше сжатия оси → заголовок ближе к графику
FONT_TICK = 10
FONT_LEGEND = 9
FONT_ANNOT = 11
FONT_HEATMAP = 10
FONT_DIAGRAM = 13  # блок-схемы (слайд 14)
FONT_SYMBOL = 18

TEXT_DARK = "#1a1a1a"
BG_LIGHT = "#ffffff"
BG_BOX = "#eef2ff"

DPI = 200

# Одна высота для всех PNG в правой колонке → одинаковый масштаб шрифтов в pptx
FIGSIZE_SINGLE = (5.5, 5.0)
FIGSIZE_DUAL_COL = (5.5, 5.0)
FIGSIZE_TRIPLE_COL = (5.5, 5.0)

# hspace в subplots_adjust — зазор между панелями (доля высоты оси); больше → больше «воздуха»
HSPACE_LINE = 0.18  # ≈ +1 строка буллета (20 pt) между панелями
DUAL_COL_HSPACE = 0.62 + HSPACE_LINE
TRIPLE_COL_HSPACE = 1.18 + HSPACE_LINE
COL_HSPACE = DUAL_COL_HSPACE
STACK_HSPACE = DUAL_COL_HSPACE

FIGSIZE_DUAL_ROW = (11.5, 3.6)
FIGSIZE_TRIPLE_ROW = (11.5, 3.3)
ROW_WSPACE = 0.32
FIGSIZE_WIDE_SINGLE = (11.5, 3.6)
FIGSIZE_DUAL = FIGSIZE_DUAL_ROW
FIGSIZE_DUAL_STACK = FIGSIZE_DUAL_COL
FIGSIZE_TRIPLE = FIGSIZE_TRIPLE_ROW
FIGSIZE_GRID2X2 = (10.0, 8.0)

# Прямоугольники в координатах figure [left, bottom, width, height]
# Ось выше → меньше пустого поля сверху PNG (выравнивание с буллетами в pptx)
SINGLE_AX = (0.14, 0.10, 0.82, 0.78)
SINGLE_AX_WITH_LEGEND = (0.14, 0.26, 0.82, 0.52)
LEGEND_STRIP = (0.14, 0.02, 0.82, 0.09)

FONT_SLIDE = {
    "font.size": FONT_LABEL,
    "axes.titlesize": FONT_TITLE,
    "axes.titlepad": TITLE_PAD,
    "axes.labelsize": FONT_LABEL,
    "xtick.labelsize": FONT_TICK,
    "ytick.labelsize": FONT_TICK,
    "legend.fontsize": FONT_LEGEND,
    "figure.titlesize": FONT_TITLE,
}

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
    return {
        "loc": "center",
        "ncol": 1,
        "fontsize": FONT_LEGEND,
        "frameon": True,
        "handlelength": 1.0,
        **extra,
    }


def style_panel_title(ax, title: str, **extra) -> None:
    props = {"fontsize": FONT_TITLE, "pad": TITLE_PAD, "color": TEXT_DARK}
    props.update(extra)
    ax.set_title(title, **props)


def _flatten_axes(axes) -> list:
    import numpy as np

    if isinstance(axes, np.ndarray):
        return axes.flatten().tolist()
    return [axes]


def _refresh_title(ax) -> None:
    title = ax.get_title()
    if title:
        style_panel_title(ax, title)


def _strip_ax_legend(ax) -> None:
    leg = ax.get_legend()
    if leg is not None:
        leg.remove()


def _collect_legends(ax_list) -> tuple[list, list]:
    handles: list = []
    labels: list = []
    for ax in ax_list:
        h, lab = ax.get_legend_handles_labels()
        handles.extend(h)
        labels.extend(lab)
    return handles, labels


def _add_legend_strip(fig, handles, labels, *, ncol: int = 1) -> None:
    if not handles:
        return
    leg_ax = fig.add_axes(LEGEND_STRIP)
    leg_ax.set_axis_off()
    leg_ax.legend(handles, labels, **legend_kwargs(ncol=ncol))


def _shrink_ax_for_title(ax, *, scale: float = 0.86) -> None:
    """Чуть уменьшить высоту оси — заголовок не прилипает к графику."""
    pos = ax.get_position()
    nh = pos.height * scale
    ax.set_position([pos.x0, pos.y0, pos.width, nh])


def _trim_png_top_whitespace(
    path: Path | str,
    *,
    bg: tuple[int, int, int] = (255, 255, 255),
    tol: int = 10,
    keep_px: int = 2,
) -> None:
    """Обрезать пустое белое поле сверху — pptx выравнивает по верху PNG."""
    path = Path(path)
    im = Image.open(path).convert("RGB")
    px = im.load()
    w, h = im.size

    def _row_has_content(y: int) -> bool:
        for x in range(w):
            r, g, b = px[x, y]
            if abs(r - bg[0]) > tol or abs(g - bg[1]) > tol or abs(b - bg[2]) > tol:
                return True
        return False

    top = 0
    while top < h - 1 and not _row_has_content(top):
        top += 1
    top = max(0, top - keep_px)
    if top > 0:
        im.crop((0, top, w, h)).save(path)


def _write_png(fig, path: Path | str, *, trim_top: bool = False) -> None:
    path = Path(path)
    fig.savefig(path, dpi=DPI, facecolor=BG_LIGHT, bbox_inches=None)
    plt.close(fig)
    Image.open(path).convert("RGB").save(path)
    if trim_top:
        _trim_png_top_whitespace(path)


def save_single_panel_figure(
    fig,
    ax,
    path: Path | str,
    *,
    legend_ncol: int = 1,
) -> None:
    """Одна панель: легенда в отдельной полосе под графиком (вне axes)."""
    _refresh_title(ax)
    h, lab = ax.get_legend_handles_labels()
    _strip_ax_legend(ax)
    if h:
        ax.set_position(SINGLE_AX_WITH_LEGEND)
        _add_legend_strip(fig, h, lab, ncol=legend_ncol)
    else:
        ax.set_position(SINGLE_AX)
    _write_png(fig, path, trim_top=True)


def save_dual_col_figure(
    fig,
    axes,
    path: Path | str,
    *,
    hspace: float | None = None,
    legend_ncols: dict[int, int] | None = None,
) -> None:
    """Две/три панели в столбик: hspace + «воздух» под заголовком каждой."""
    ax_list = _flatten_axes(axes)
    for ax in ax_list:
        _refresh_title(ax)

    hs = hspace if hspace is not None else (
        TRIPLE_COL_HSPACE if len(ax_list) >= 3 else DUAL_COL_HSPACE
    )
    handles, labels = _collect_legends(ax_list)
    for ax in ax_list:
        _strip_ax_legend(ax)
    has_leg = bool(handles)
    fig.subplots_adjust(
        left=0.14,
        right=0.96,
        top=0.97,
        bottom=0.21 if has_leg else (0.06 if len(ax_list) >= 3 else 0.10),
        hspace=hs,
    )

    for ax in ax_list:
        _shrink_ax_for_title(ax, scale=TITLE_AX_SHRINK)

    if has_leg:
        ncol = 2 if len(labels) > 2 else 1
        if legend_ncols:
            ncol = max(legend_ncols.values(), default=ncol)
        _add_legend_strip(fig, handles, labels, ncol=ncol)

    _write_png(fig, path)


def apply_matplotlib_slide_style(*, compact: bool = False) -> None:
    _ = compact
    plt.rcParams.update({**FONT_SLIDE, **CONTRAST})
    plt.rcParams["figure.dpi"] = DPI
    plt.rcParams["savefig.dpi"] = DPI


def style_axes(ax, *, facecolor: str = BG_LIGHT) -> None:
    ax.set_facecolor(facecolor)
    ax.title.set_color(TEXT_DARK)
    ax.xaxis.label.set_color(TEXT_DARK)
    ax.yaxis.label.set_color(TEXT_DARK)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(TEXT_DARK)


def heatmap_text_color(value: float, vmin: float = 0.0, vmax: float = 1.0) -> str:
    t = (value - vmin) / (vmax - vmin) if vmax > vmin else 0.5
    return "#ffffff" if t > 0.55 else TEXT_DARK


def save_slide_figure(
    fig,
    path: Path | str,
    *,
    tight: bool = True,
    axes=None,
    legend_below: bool = True,
) -> None:
    if tight or axes is None:
        path = Path(path)
        fig.savefig(path, dpi=DPI, facecolor=BG_LIGHT, bbox_inches="tight" if tight else None)
        plt.close(fig)
        Image.open(path).convert("RGB").save(path)
        return
    ax_list = _flatten_axes(axes)
    if len(ax_list) == 1:
        save_single_panel_figure(fig, ax_list[0], path)
    else:
        save_dual_col_figure(fig, axes, path)


def adjust_figure_layout(*args, **kwargs) -> None:
    pass


def place_legend_below(ax, *, ncol: int = 1) -> None:
    """Deprecated: легенда ставится в save_*_figure."""
    _ = ncol
