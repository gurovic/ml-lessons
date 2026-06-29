"""Генерация всех иллюстраций урока pandas (rebuild from plan.md)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "agents"))
from viz_style import (  # noqa: E402
    BG_BOX,
    COL_HSPACE,
    FIGSIZE_DUAL_COL,
    FIGSIZE_TRIPLE_COL,
    TEXT_DARK,
    FONT_ANNOT,
    FONT_SYMBOL,
    apply_matplotlib_slide_style,
    heatmap_text_color,
    legend_kwargs,
    save_dual_col_figure,
    save_slide_figure,
    style_axes,
)

ASSETS = Path(__file__).resolve().parent
RNG = np.random.default_rng(42)


def _box(ax, xy, w, h, text, fc=BG_BOX, ec="#444444"):
    patch = FancyBboxPatch(
        xy, w, h, boxstyle="round,pad=0.02", fc=fc, ec=ec, lw=1.2
    )
    ax.add_patch(patch)
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=FONT_ANNOT, color=TEXT_DARK)


def fig_pandas_numpy_schema():
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=(5.5, 3.8))
    style_axes(ax)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    _box(ax, (0.3, 1.5), 2.2, 3.5, "Индекс\n0\n1\n2\n3")
    _box(ax, (3.0, 3.2), 2.0, 1.8, "age\nnumpy\nfloat64", fc="#d4edda")
    _box(ax, (3.0, 1.5), 2.0, 1.5, "name\nobject\n→ Python", fc="#f8d7da")
    _box(ax, (5.5, 2.2), 2.0, 2.5, "city\nstring\n[pyarrow]", fc="#fff3cd")
    ax.annotate("", xy=(5.2, 4.0), xytext=(5.0, 4.0), arrowprops=dict(arrowstyle="->", color="#888"))
    ax.set_title("DataFrame = numpy + индексы + метаданные")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "pandas_numpy_schema.png", tight=False, axes=ax)


def fig_index_ragged_reset():
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(3, 1, figsize=FIGSIZE_TRIPLE_COL, gridspec_kw={"hspace": COL_HSPACE})
    idx_before = [0, 1, 2, 3, 4]
    ages = [22, 35, 28, 41, 33]
    for ax, title, idx in [
        (axes[0], "исходный", idx_before),
        (axes[1], "после фильтра", [1, 3]),
        (axes[2], "reset_index", [0, 1]),
    ]:
        style_axes(ax)
        sub_idx = idx
        sub_ages = [ages[i] for i in sub_idx] if title != "исходный" else ages
        if title == "после фильтра":
            sub_ages = [35, 41]
        ax.barh(range(len(sub_ages)), sub_ages, color="#1f77b4")
        ax.set_yticks(range(len(sub_ages)))
        ax.set_yticklabels([str(i) for i in (sub_idx if title != "reset_index" else [0, 1])])
        ax.set_xlabel("age")
        ax.set_ylabel("индекс")
        ax.set_title(title)
    fig.suptitle("«Рваный» индекс после фильтрации", color=TEXT_DARK)
    plt.tight_layout()
    save_dual_col_figure(fig, axes, ASSETS / "index_ragged_reset.png")


def fig_boolean_mask_flow():
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(3, 1, figsize=FIGSIZE_TRIPLE_COL, gridspec_kw={"hspace": COL_HSPACE})
    ages = np.array([25, 40, 22, 38, 31])
    mask = ages > 30
    for ax, data, title, colors in [
        (axes[0], ages, "age", ["#1f77b4"] * 5),
        (axes[1], mask.astype(int), "mask", ["#2ca02c" if m else "#d62728" for m in mask]),
        (axes[2], ages[mask], "df[mask]", ["#1f77b4"] * mask.sum()),
    ]:
        style_axes(ax)
        ax.bar(range(len(data)), data if title != "mask" else mask.astype(int), color=colors[: len(data)])
        ax.set_title(title)
        ax.set_xticks(range(len(data)))
    fig.suptitle("Булева индексация: age → mask → строки", color=TEXT_DARK)
    plt.tight_layout()
    save_dual_col_figure(fig, axes, ASSETS / "boolean_mask_flow.png")


def fig_loc_vs_iloc():
    apply_matplotlib_slide_style()
    df = pd.DataFrame(
        {"A": [10, 20, 30, 40], "B": [1, 2, 3, 4]},
        index=[10, 20, 30, 40],
    )
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.axis("off")
    table = ax.table(
        cellText=df.values,
        rowLabels=df.index,
        colLabels=df.columns,
        loc="center",
        cellLoc="center",
    )
    table.scale(1.2, 1.8)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#444444")
        if r == 2 and c == 1:
            cell.set_facecolor("#fff3cd")
        if r == 2 and c == 0:
            cell.set_facecolor("#d4edda")
    ax.text(0.5, 0.92, "loc[20, 'A']=20 (жёлтый)  |  iloc[1,0]=20 (зелёный)", transform=ax.transAxes, ha="center", fontsize=FONT_ANNOT)
    ax.set_title(".loc по метке vs .iloc по позиции")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "loc_vs_iloc.png", tight=False, axes=ax)


def fig_setting_with_copy():
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    _box(ax, (0.5, 4), 2, 1, "df")
    _box(ax, (3.5, 4), 2, 1, "df[mask]")
    _box(ax, (6.5, 4.5), 2.5, 0.8, "view? copy?", fc="#fff3cd")
    ax.annotate("", xy=(3.4, 4.5), xytext=(2.6, 4.5), arrowprops=dict(arrowstyle="->", color="#d62728", lw=2))
    _box(ax, (3.5, 2), 2, 1, "subset['x']=1\n⚠ Warning", fc="#f8d7da")
    _box(ax, (6.5, 1.5), 2.5, 1.2, ".copy() ✓\n.loc на df ✓", fc="#d4edda")
    ax.set_title("SettingWithCopyWarning")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "setting_with_copy.png", tight=False, axes=ax)


def fig_view_vs_copy():
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL, gridspec_kw={"hspace": COL_HSPACE})
    for ax, title, shared in [(axes[0], "View (общая память)", True), (axes[1], "Copy (независимо)", False)]:
        style_axes(ax)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.axis("off")
        _box(ax, (1, 2.5), 3, 1.5, "данные", fc="#d4edda" if shared else "#cce5ff")
        if shared:
            _box(ax, (5.5, 3.5), 2.5, 1, "view A", fc="#fff3cd")
            _box(ax, (5.5, 1.5), 2.5, 1, "view B", fc="#fff3cd")
            ax.annotate("", xy=(5.4, 4), xytext=(4.1, 3.2), arrowprops=dict(arrowstyle="->", color="#444"))
            ax.annotate("", xy=(5.4, 2), xytext=(4.1, 3.2), arrowprops=dict(arrowstyle="->", color="#444"))
        else:
            _box(ax, (5.5, 3.5), 2.5, 1, "копия A", fc="#fff3cd")
            _box(ax, (5.5, 1.5), 2.5, 1, "копия B", fc="#fff3cd")
        ax.set_title(title)
    fig.suptitle("View vs Copy; CoW — копия при записи", color=TEXT_DARK)
    plt.tight_layout()
    save_dual_col_figure(fig, axes, ASSETS / "view_vs_copy.png")


def fig_missing_counts():
    apply_matplotlib_slide_style()
    cols = ["Age", "Fare", "Embarked", "Cabin"]
    counts = [177, 0, 2, 687]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    bars = ax.bar(cols, counts, color=["#d62728" if c > 100 else "#ff7f0e" for c in counts])
    ax.set_ylabel("число пропусков")
    ax.set_title("df.isnull().sum() — диагностика")
    for b, v in zip(bars, counts):
        ax.text(b.get_x() + b.get_width() / 2, v + 10, str(v), ha="center", fontsize=FONT_ANNOT)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "missing_counts.png", tight=False, axes=ax)


def fig_nullable_int_types():
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL, gridspec_kw={"hspace": COL_HSPACE})
    for ax, title, ok in [(axes[0], "int64 + NaN → float64", False), (axes[1], "Int64 + pd.NA", True)]:
        style_axes(ax)
        ax.axis("off")
        _box(ax, (1, 3), 3, 1.2, "int64" if not ok else "Int64", fc="#fff3cd")
        _box(ax, (1, 1.2), 3, 1.2, "np.nan / pd.NA", fc="#f8d7da" if not ok else "#d4edda")
        ax.text(5, 3.6, "✗" if not ok else "✓", fontsize=FONT_SYMBOL, color="#d62728" if not ok else "#2ca02c")
        ax.set_title(title)
    plt.tight_layout()
    save_dual_col_figure(fig, axes, ASSETS / "nullable_int_types.png")


def fig_corr_heatmap():
    apply_matplotlib_slide_style()
    cols = ["x1", "x2", "x3", "x4"]
    corr = np.array([[1.0, 0.95, 0.3, 0.1], [0.95, 1.0, 0.25, 0.05], [0.3, 0.25, 1.0, 0.6], [0.1, 0.05, 0.6, 1.0]])
    fig, ax = plt.subplots(figsize=(4.5, 4))
    style_axes(ax)
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(cols)
    ax.set_yticklabels(cols)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{corr[i, j]:.2f}", ha="center", va="center", color=heatmap_text_color(abs(corr[i, j])))
    ax.set_title("corr() — мультиколлинеарность x1–x2")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "corr_heatmap.png", tight=False, axes=ax)


def fig_value_counts_bar():
    apply_matplotlib_slide_style()
    labels = ["A", "B", "C", "D"]
    counts = [900, 70, 20, 10]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.bar(labels, counts, color=["#d62728", "#ff7f0e", "#1f77b4", "#2ca02c"])
    ax.set_ylabel("частота")
    ax.set_title("value_counts() — дисбаланс 90/10")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "value_counts_bar.png", tight=False, axes=ax)


def fig_agg_vs_transform():
    apply_matplotlib_slide_style()
    cities = ["M", "S", "P"]
    means = [55, 48, 62]
    incomes = np.array([50, 60, 45, 52, 70, 48, 55, 65, 58])
    city_labels = ["M", "M", "S", "S", "P", "P", "M", "P", "S"]
    dev = incomes - np.array([means[["M", "S", "P"].index(c)] for c in city_labels])
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL, gridspec_kw={"hspace": COL_HSPACE})
    style_axes(axes[0])
    axes[0].bar(cities, means, color="#1f77b4")
    axes[0].set_title("agg → 3 строки")
    axes[0].set_ylabel("средний income")
    style_axes(axes[1])
    axes[1].bar(range(9), dev, color=["#2ca02c" if d >= 0 else "#d62728" for d in dev])
    axes[1].set_title("transform → 9 строк (отклонение)")
    axes[1].set_xlabel("строка")
    fig.suptitle("agg vs transform", color=TEXT_DARK)
    plt.tight_layout()
    save_dual_col_figure(fig, axes, ASSETS / "agg_vs_transform.png")


def fig_multiindex_reset():
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    style_axes(ax)
    ax.axis("off")
    _box(ax, (0.3, 2), 4, 2.5, "MultiIndex\n(city, cat)\n× (mean, std)", fc="#fff3cd")
    ax.annotate("", xy=(5.2, 3.2), xytext=(4.4, 3.2), arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=2))
    _box(ax, (5.3, 2), 4, 2.5, "reset_index()\nплоские столбцы", fc="#d4edda")
    ax.set_title("MultiIndex → reset_index")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "multiindex_reset.png", tight=False, axes=ax)


def fig_encoding_methods():
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(3, 1, figsize=FIGSIZE_TRIPLE_COL, gridspec_kw={"hspace": COL_HSPACE})
    cats = ["low", "med", "high"]
    for ax, title, data in [
        (axes[0], "Ordinal", [0, 1, 2]),
        (axes[1], "One-Hot", None),
        (axes[2], "Target", [0.2, 0.5, 0.8]),
    ]:
        style_axes(ax)
        if title == "One-Hot":
            mat = np.eye(3, dtype=int)[:, 1:]
            ax.imshow(mat, cmap="Blues", vmin=0, vmax=1)
            ax.set_xticks([0])
            ax.set_xticklabels(["med,high"])
        else:
            ax.bar(cats, data, color="#1f77b4")
        ax.set_title(title)
    plt.tight_layout()
    save_dual_col_figure(fig, axes, ASSETS / "encoding_methods.png")


def fig_clip_outliers():
    apply_matplotlib_slide_style()
    x = RNG.lognormal(3, 0.6, 200)
    x_clip = np.clip(x, None, np.quantile(x, 0.99))
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL, gridspec_kw={"hspace": COL_HSPACE})
    for ax, data, title in [(axes[0], x, "до clip"), (axes[1], x_clip, "после clip (99%)")]:
        style_axes(ax)
        ax.hist(data, bins=30, color="#1f77b4", edgecolor="white")
        ax.set_title(title)
        ax.set_xlabel("income")
    fig.suptitle("Winsorization через clip", color=TEXT_DARK)
    plt.tight_layout()
    save_dual_col_figure(fig, axes, ASSETS / "clip_outliers.png")


def fig_cut_bins():
    apply_matplotlib_slide_style()
    data = RNG.normal(50, 15, 300)
    bins = pd.cut(data, 5)
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.hist(data, bins=5, color="#aec7e8", edgecolor="white")
    for b in np.linspace(data.min(), data.max(), 6):
        ax.axvline(b, color="#d62728", ls="--", lw=1)
    ax.set_title("pd.cut — равные интервалы")
    ax.set_xlabel("значение")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "cut_bins.png", tight=False, axes=ax)


def fig_str_extract():
    apply_matplotlib_slide_style()
    emails = ["a@mail.ru", "b@yandex.ru", "c@gmail.com", "d@mail.ru", "e@corp.io"]
    domains = [e.split("@")[1] for e in emails]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.axis("off")
    rows = [[e, d] for e, d in zip(emails, domains)]
    table = ax.table(cellText=rows, colLabels=["email", "domain"], loc="center", cellLoc="left")
    table.scale(1, 1.6)
    ax.set_title(".str.extract / split домена")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "str_extract.png", tight=False, axes=ax)


def fig_dt_cyclic_hour():
    apply_matplotlib_slide_style()
    hours = np.arange(24)
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.plot(hours, np.sin(2 * np.pi * hours / 24), "o-", label="sin", color="#1f77b4")
    ax.plot(hours, np.cos(2 * np.pi * hours / 24), "s-", label="cos", color="#ff7f0e")
    ax.axvline(23, color="#d62728", ls=":", label="23:00 близко к 0")
    ax.axvline(0, color="#2ca02c", ls=":", label="00:00")
    ax.set_xlabel("час")
    ax.set_title("Циклическое кодирование часа")
    ax.legend(**legend_kwargs())
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "dt_cyclic_hour.png", tight=False, axes=ax)


def fig_to_numpy_bridge():
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL, gridspec_kw={"hspace": COL_HSPACE})
    for ax, title, ok in [(axes[0], "только числа → float", True), (axes[1], "object + числа → object", False)]:
        style_axes(ax)
        ax.axis("off")
        _box(ax, (0.8, 2), 2.5, 1.5, "DataFrame")
        _box(ax, (4.5, 2), 2.5, 1.5, "ndarray\nfloat64" if ok else "ndarray\nobject ✗", fc="#d4edda" if ok else "#f8d7da")
        ax.annotate("", xy=(4.4, 2.8), xytext=(3.4, 2.8), arrowprops=dict(arrowstyle="->", color="#444"))
        ax.set_title(title)
    plt.tight_layout()
    save_dual_col_figure(fig, axes, ASSETS / "to_numpy_bridge.png")


def fig_merge_cartesian():
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    _box(ax, (0.5, 3.5), 2, 1.5, "A: 3 строки\nid=1,2,3")
    _box(ax, (0.5, 1), 2, 1.5, "B: id=2\nдважды")
    _box(ax, (5, 2), 3.5, 2, "merge → 4 строки\n(раздувание!)", fc="#f8d7da")
    ax.annotate("", xy=(4.9, 3), xytext=(2.6, 2.5), arrowprops=dict(arrowstyle="->", color="#d62728", lw=2))
    ax.set_title("merge: неуникальный ключ")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "merge_cartesian.png", tight=False, axes=ax)


def fig_concat_index_trap():
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL, gridspec_kw={"hspace": COL_HSPACE})
    for ax, title, nans in [(axes[0], "concat: рваные индексы", True), (axes[1], "после reset_index", False)]:
        style_axes(ax)
        if nans:
            mat = np.array([[1, np.nan], [np.nan, 2], [3, np.nan]])
        else:
            mat = np.array([[1, 1], [2, 2], [3, 3]])
        im = ax.imshow(np.nan_to_num(mat, nan=-1), cmap="RdYlGn", vmin=-1, vmax=3)
        for i in range(3):
            for j in range(2):
                val = mat[i, j]
                txt = "NaN" if np.isnan(val) else f"{val:.0f}"
                ax.text(j, i, txt, ha="center", va="center", color=TEXT_DARK)
        ax.set_title(title)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["df1", "df2"])
    plt.tight_layout()
    save_dual_col_figure(fig, axes, ASSETS / "concat_index_trap.png")


def fig_merge_asof_timeline():
    apply_matplotlib_slide_style()
    t_tx = np.array([2.2, 5.1, 7.8])
    t_rate = np.array([0, 2, 4, 6, 8])
    rates = np.array([1.0, 1.1, 1.2, 1.15, 1.3])
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    style_axes(ax)
    ax.step(t_rate, rates, where="post", color="#1f77b4", label="курс")
    ax.scatter(t_tx, [1.1, 1.15, 1.3], c="#d62728", s=80, zorder=5, label="транзакции")
    for tx, ry in zip(t_tx, [1.1, 1.15, 1.3]):
        ax.annotate("", xy=(tx, ry), xytext=(tx - 0.5, 1.05), arrowprops=dict(arrowstyle="->", color="#888"))
    ax.set_xlabel("время")
    ax.set_ylabel("курс")
    ax.set_title("merge_asof backward")
    ax.legend(**legend_kwargs())
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "merge_asof_timeline.png", tight=False, axes=ax)


def fig_pandas_sklearn_pipeline():
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    style_axes(ax)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")
    boxes = [(0.3, 1.5, "DataFrame"), (2.8, 1.5, "Column\nTransformer"), (5.3, 1.5, "numpy X"), (7.8, 1.5, "Model")]
    for i, (x, y, t) in enumerate(boxes):
        _box(ax, (x, y), 2, 1.2, t)
        if i < len(boxes) - 1:
            ax.annotate("", xy=(x + 2.1, y + 0.6), xytext=(x + 1.9, y + 0.6), arrowprops=dict(arrowstyle="->", color="#444"))
    ax.set_title("pandas → sklearn Pipeline")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "pandas_sklearn_pipeline.png", tight=False, axes=ax)


def fig_pandas_pytorch_bridge():
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL, gridspec_kw={"hspace": COL_HSPACE})
    for ax, title, shared in [(axes[0], "from_numpy (shared)", True), (axes[1], "torch.tensor (copy)", False)]:
        style_axes(ax)
        ax.axis("off")
        _box(ax, (0.8, 2), 2, 1.2, "numpy")
        _box(ax, (4.5, 2), 2, 1.2, "Tensor")
        if shared:
            ax.plot([3, 4.4], [2.6, 2.6], "g-", lw=2)
            ax.text(3.7, 2.9, "shared", fontsize=FONT_ANNOT, color="#2ca02c")
        else:
            ax.annotate("", xy=(4.4, 2.6), xytext=(2.9, 2.6), arrowprops=dict(arrowstyle="->", color="#1f77b4"))
            ax.text(3.3, 2.9, "copy", fontsize=FONT_ANNOT)
        ax.set_title(title)
    plt.tight_layout()
    save_dual_col_figure(fig, axes, ASSETS / "pandas_pytorch_bridge.png")


def fig_pandas_leakage():
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL, gridspec_kw={"hspace": COL_HSPACE})
    for ax, title, leak in [(axes[0], "fillna до split ✗", True), (axes[1], "Imputer в Pipeline ✓", False)]:
        style_axes(ax)
        ax.set_xlim(0, 8)
        ax.set_ylim(0, 5)
        ax.axis("off")
        _box(ax, (0.5, 3), 2, 1, "fillna\n(all data)", fc="#f8d7da" if leak else "#d4edda")
        _box(ax, (3, 3), 2, 1, "split")
        _box(ax, (5.5, 3), 2, 1, "train/test")
        if not leak:
            _box(ax, (3, 1), 4, 1, "SimpleImputer fit on train", fc="#d4edda")
        ax.set_title(title)
    plt.tight_layout()
    save_dual_col_figure(fig, axes, ASSETS / "pandas_leakage.png")


def fig_read_csv_chunks():
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    style_axes(ax)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")
    _box(ax, (0.3, 2), 2, 2, "CSV\n50 GB")
    for i, y in enumerate([3.2, 2.2, 1.2]):
        _box(ax, (3.5, y), 2, 0.8, f"chunk {i+1}", fc="#cce5ff")
        ax.annotate("", xy=(3.4, y + 0.4), xytext=(2.4, 3), arrowprops=dict(arrowstyle="->", color="#444"))
    _box(ax, (6.5, 2), 2.5, 2, "агрегаты\nв RAM", fc="#d4edda")
    ax.set_title("read_csv(chunksize=...)")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "read_csv_chunks.png", tight=False, axes=ax)


def fig_profiling_report_mock():
    apply_matplotlib_slide_style()
    fig = plt.figure(figsize=(5.5, 4))
    gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])
    for ax in [ax1, ax2, ax3]:
        style_axes(ax)
    ax1.hist(RNG.normal(0, 1, 200), bins=20, color="#1f77b4", edgecolor="white")
    ax1.set_title("распределения")
    im = ax2.imshow(RNG.uniform(-1, 1, (4, 4)), cmap="RdBu_r", vmin=-1, vmax=1)
    ax2.set_title("корреляции")
    ax3.bar(["Age", "Fare", "Name"], [10, 0, 0], color="#d62728")
    ax3.set_title("пропуски / предупреждения")
    fig.suptitle("ydata-profiling (макет отчёта)", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "profiling_report_mock.png")


def fig_perf_vectorized():
    apply_matplotlib_slide_style()
    n = 200_000
    s = pd.Series(range(n))
    t0 = time.perf_counter()
    _ = s.apply(lambda x: x * 2)
    t_apply = time.perf_counter() - t0
    t0 = time.perf_counter()
    _ = s * 2
    t_vec = time.perf_counter() - t0
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    methods = ["apply", "vectorized"]
    times = [t_apply, t_vec]
    bars = ax.bar(methods, times, color=["#d62728", "#2ca02c"])
    ax.set_ylabel("секунды")
    ax.set_title(f"Series×2, n={n:,}")
    ratio = t_apply / max(t_vec, 1e-9)
    ax.text(1, t_vec + t_apply * 0.05, f"{ratio:.0f}× быстрее", ha="center")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "perf_vectorized.png", tight=False, axes=ax)


def fig_dtype_memory():
    apply_matplotlib_slide_style()
    n = 100_000
    labels = ["object", "category", "int8"]
    mem = [
        pd.Series(["city"] * n, dtype=object).memory_usage(deep=True) / 1024,
        pd.Series(["city"] * n, dtype="category").memory_usage(deep=True) / 1024,
        pd.Series([1] * n, dtype="int8").memory_usage(deep=True) / 1024,
    ]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.bar(labels, mem, color=["#d62728", "#2ca02c", "#1f77b4"])
    ax.set_ylabel("KiB")
    ax.set_title("Память столбца 100k строк")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "dtype_memory.png", tight=False, axes=ax)


def fig_csv_vs_parquet():
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL, gridspec_kw={"hspace": COL_HSPACE})
    labels = ["CSV", "Parquet"]
    size_mb = [120, 18]
    read_s = [45, 3]
    style_axes(axes[0])
    axes[0].bar(labels, size_mb, color=["#d62728", "#2ca02c"])
    axes[0].set_ylabel("МБ")
    axes[0].set_title("размер файла")
    style_axes(axes[1])
    axes[1].bar(labels, read_s, color=["#d62728", "#2ca02c"])
    axes[1].set_ylabel("сек чтения")
    axes[1].set_title("скорость (схематично)")
    fig.suptitle("CSV vs Parquet", color=TEXT_DARK)
    plt.tight_layout()
    save_dual_col_figure(fig, axes, ASSETS / "csv_vs_parquet.png")


def fig_export_formats():
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    _box(ax, (3.5, 2.5), 3, 1.5, "DataFrame")
    for x, y, t in [(0.5, 4.5, "SQL"), (0.5, 1, "JSON"), (7, 4.5, "Feather"), (7, 1, "Parquet")]:
        _box(ax, (x, y), 2, 1, t)
        ax.annotate("", xy=(x + 2 if x < 5 else 3.4, y + 0.5), xytext=(3.5 if x < 5 else 6.5, 3.2),
                    arrowprops=dict(arrowstyle="->", color="#888", connectionstyle="arc3,rad=0.1"))
    ax.set_title("Экспорт: index=False")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "export_formats.png", tight=False, axes=ax)


def fig_alternatives_compare():
    apply_matplotlib_slide_style()
    libs = ["pandas", "Polars", "Dask", "DuckDB"]
    speed = [1, 15, 8, 12]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.barh(libs, speed, color=["#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd"])
    ax.set_xlabel("относительная скорость (схема)")
    ax.set_title("Альтернативы pandas")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "alternatives_compare.png", tight=False, axes=ax)


def fig_rapids_gpu_flow():
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    style_axes(ax)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis("off")
    _box(ax, (0.3, 2), 2.2, 1.5, "pandas\nCPU/RAM", fc="#fff3cd")
    _box(ax, (3.5, 2), 2.2, 1.5, "cuDF\nGPU/VRAM", fc="#cce5ff")
    _box(ax, (6.7, 2), 2.2, 1.5, "PyTorch\n.cuda()", fc="#d4edda")
    for x1, x2 in [(2.6, 3.4), (5.8, 6.6)]:
        ax.annotate("", xy=(x2, 2.8), xytext=(x1, 2.8), arrowprops=dict(arrowstyle="->", color="#444", lw=2))
    ax.set_title("RAM → VRAM: pandas не на GPU сам")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "rapids_gpu_flow.png", tight=False, axes=ax)


def fig_jupyter_memory():
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL, gridspec_kw={"hspace": COL_HSPACE})
    for ax, title, n_blocks in [(axes[0], "Jupyter OOM", 5), (axes[1], "del + gc.collect()", 2)]:
        style_axes(ax)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 5)
        ax.axis("off")
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
        for i in range(n_blocks):
            _box(ax, (0.5 + i * 1.7, 2), 1.4, 1.5, f"df{i+1}", fc=colors[i % len(colors)])
        if n_blocks > 3:
            ax.text(5, 4.2, "скрытые ссылки _", fontsize=FONT_ANNOT, color="#d62728")
        ax.set_title(title)
    plt.tight_layout()
    save_dual_col_figure(fig, axes, ASSETS / "jupyter_memory.png")


def fig_pandas_ml_pipeline():
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    style_axes(ax)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4)
    ax.axis("off")
    steps = ["CSV/Parquet", "EDA\npandas", "Pipeline\nsklearn", "numpy", "model"]
    for i, s in enumerate(steps):
        _box(ax, (0.3 + i * 2.6, 1.5), 2.2, 1.3, s, fc="#d4edda" if i == 1 else BG_BOX)
        if i < len(steps) - 1:
            ax.annotate("", xy=(2.6 + i * 2.6, 2.1), xytext=(2.4 + i * 2.6, 2.1),
                        arrowprops=dict(arrowstyle="->", color="#444"))
    ax.set_title("Ментальная модель ML-пайплайна")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "pandas_ml_pipeline.png", tight=False, axes=ax)


FUNCTIONS = [
    fig_pandas_numpy_schema,
    fig_index_ragged_reset,
    fig_boolean_mask_flow,
    fig_loc_vs_iloc,
    fig_setting_with_copy,
    fig_view_vs_copy,
    fig_missing_counts,
    fig_nullable_int_types,
    fig_corr_heatmap,
    fig_value_counts_bar,
    fig_agg_vs_transform,
    fig_multiindex_reset,
    fig_encoding_methods,
    fig_clip_outliers,
    fig_cut_bins,
    fig_str_extract,
    fig_dt_cyclic_hour,
    fig_to_numpy_bridge,
    fig_merge_cartesian,
    fig_concat_index_trap,
    fig_merge_asof_timeline,
    fig_pandas_sklearn_pipeline,
    fig_pandas_pytorch_bridge,
    fig_pandas_leakage,
    fig_read_csv_chunks,
    fig_profiling_report_mock,
    fig_perf_vectorized,
    fig_dtype_memory,
    fig_csv_vs_parquet,
    fig_export_formats,
    fig_alternatives_compare,
    fig_rapids_gpu_flow,
    fig_jupyter_memory,
    fig_pandas_ml_pipeline,
]


def main() -> None:
    for fn in FUNCTIONS:
        name = fn.__name__
        print(f"  {name}...")
        fn()
    print(f"Done: {len(FUNCTIONS)} figures in {ASSETS}")


if __name__ == "__main__":
    main()
