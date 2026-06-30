"""Генерация всех иллюстраций урока vizualizatsiya (34 слайда).

Данные подобраны педагогически: эффект на графике виден сразу.
Plotly-темы — статические matplotlib-аппроксимации.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle, Wedge
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs, make_classification, make_regression
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import DecisionBoundaryDisplay, permutation_importance
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.manifold import TSNE
from sklearn.metrics import ConfusionMatrixDisplay, auc, precision_recall_curve, roc_curve
from sklearn.model_selection import cross_val_score, learning_curve
from sklearn.tree import DecisionTreeClassifier

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "agents"))
from viz_style import (  # noqa: E402
    BG_BOX,
    FIGSIZE_DUAL_COL,
    FIGSIZE_SINGLE,
    FIGSIZE_TRIPLE_COL,
    FONT_ANNOT,
    FONT_DIAGRAM,
    FONT_HEATMAP,
    FONT_TITLE,
    TEXT_DARK,
    apply_matplotlib_slide_style,
    heatmap_text_color,
    legend_kwargs,
    save_dual_col_figure,
    save_single_panel_figure,
    save_slide_figure,
    style_axes,
    style_panel_title,
)

ASSETS = Path(__file__).resolve().parent
RNG = np.random.default_rng(42)

C0, C1, C2, C3 = "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"


def _grid(ax, *, alpha: float = 0.35) -> None:
    ax.grid(True, alpha=alpha, linestyle=":", linewidth=0.7)


def _box(ax, xy, w, h, text, *, fc=BG_BOX, ec="#444444", fs=None):
    ax.add_patch(
        FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.03", fc=fc, ec=ec, lw=1.2)
    )
    ax.text(
        xy[0] + w / 2,
        xy[1] + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fs or FONT_DIAGRAM,
        color=TEXT_DARK,
    )


def _housing_df(n: int = 120) -> pd.DataFrame:
    area = RNG.uniform(30, 120, n)
    city = RNG.choice(["Москва", "СПб", "Казань"], n, p=[0.45, 0.35, 0.20])
    price = 2.8 * area + np.where(city == "Москва", 400, np.where(city == "СПб", 250, 100))
    price += RNG.normal(0, 45, n)
    income = np.where(
        city == "Москва",
        RNG.normal(120, 25, n),
        np.where(city == "СПб", RNG.normal(85, 18, n), RNG.normal(55, 12, n)),
    )
    return pd.DataFrame({"площадь": area, "цена": price, "город": city, "доход": income})


def fig_philosophy():
    """Слайд 1: три задачи визуализации в ML."""
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    style_panel_title(ax, "Каждый график — ответ на вопрос")
    tasks = [
        (0.4, 3.8, "EDA\nпонимание данных", "#d4edda"),
        (3.5, 3.8, "Диагностика\nмоделей", "#fff3cd"),
        (6.6, 3.8, "Объяснение\nбизнесу", "#cce5ff"),
    ]
    for x, y, txt, fc in tasks:
        _box(ax, (x, y), 2.6, 1.6, txt, fc=fc)
    ax.text(5.0, 2.6, "«3 секунды на инсайт»", ha="center", fontsize=FONT_ANNOT, color=C2, fontweight="bold")
    for x in [1.7, 4.8, 7.9]:
        ax.add_patch(
            FancyArrowPatch((x, 3.6), (5.0, 2.9), arrowstyle="->", color="#888888", mutation_scale=10)
        )
    save_single_panel_figure(fig, ax, ASSETS / "ml_viz_three_roles.png")


def fig_library_choice():
    """Слайд 2: выбор библиотеки."""
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")
    style_panel_title(ax, "Библиотека под задачу")
    libs = [
        (0.3, 4.8, "matplotlib\nполный контроль", "#eef2ff"),
        (2.6, 4.8, "seaborn\n90% EDA", "#d4edda"),
        (5.0, 4.8, "plotly\nинтерактив", "#fff3cd"),
        (7.3, 4.8, "pandas.plot\nбыстрый старт", "#f8d7da"),
    ]
    for x, y, txt, fc in libs:
        _box(ax, (x, y), 2.0, 1.5, txt, fc=fc)
    _box(ax, (1.0, 1.0), 8.0, 2.2, "seaborn → plotly → matplotlib\n(EDA → презентация → тонкая настройка)", fc="white")
    save_single_panel_figure(fig, ax, ASSETS / "library_choice_matrix.png")


def fig_pandas_plot():
    """Слайд 3: pandas built-in — крупные подписи для правой колонки."""
    apply_matplotlib_slide_style()
    df = _housing_df(80)
    fig, axes = plt.subplots(2, 2, figsize=FIGSIZE_SINGLE)
    for ax in axes.flat:
        style_axes(ax)
        ax.tick_params(labelsize=12)
        ax.xaxis.label.set_fontsize(14)
        ax.yaxis.label.set_fontsize(14)
        ax.title.set_fontsize(14)

    df["площадь"].plot(kind="hist", ax=axes[0, 0], bins=14, color=C0, alpha=0.88, edgecolor="white")
    axes[0, 0].set_xlabel("площадь")
    axes[0, 0].set_ylabel("частота")
    axes[0, 0].set_title("hist", fontweight="bold")

    df.boxplot(column="площадь", ax=axes[0, 1])
    axes[0, 1].set_title("box", fontweight="bold")
    axes[0, 1].set_ylabel("площадь")

    axes[1, 0].scatter(df["площадь"], df["цена"], c=C0, s=35, alpha=0.75)
    axes[1, 0].set_xlabel("площадь")
    axes[1, 0].set_ylabel("цена")
    axes[1, 0].set_title("scatter", fontweight="bold")

    vc = df["город"].value_counts()
    vc.plot(kind="bar", ax=axes[1, 1], color=[C0, C1, C2], edgecolor="white")
    axes[1, 1].set_xlabel("город")
    axes[1, 1].set_ylabel("кол-во")
    axes[1, 1].set_title("bar", fontweight="bold")
    axes[1, 1].tick_params(axis="x", rotation=15)

    fig.suptitle("df.plot() — быстрый обзор", fontsize=15, color=TEXT_DARK, y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save_slide_figure(fig, ASSETS / "pandas_builtin_overview.png", tight=True)


def _code_banner(fig, code: str, *, y: float = 0.97) -> None:
    fig.text(
        0.5,
        y,
        code,
        ha="center",
        va="top",
        fontsize=FONT_ANNOT,
        fontfamily="monospace",
        color=TEXT_DARK,
        transform=fig.transFigure,
    )


def fig_mpl_code_subplots():
    """Слайд 4: fig, ax = plt.subplots()."""
    apply_matplotlib_slide_style()
    fig = plt.figure(figsize=(4.2, 3.8))
    _code_banner(fig, "fig, ax = plt.subplots()")
    ax = fig.add_axes([0.14, 0.12, 0.78, 0.62])
    style_axes(ax)
    x = np.linspace(0, 8, 35)
    ax.scatter(x, 1.5 * x + RNG.normal(0, 1.2, 35), c=C0, s=28, alpha=0.85)
    ax.set_xlabel("признак")
    ax.set_ylabel("таргет")
    _grid(ax)
    fig.patches.append(
        Rectangle(
            (0.08, 0.08),
            0.84,
            0.68,
            fill=False,
            ec=C2,
            lw=2.0,
            linestyle="--",
            transform=fig.transFigure,
        )
    )
    fig.text(0.5, 0.06, "Figure", ha="center", fontsize=FONT_ANNOT - 1, color=C2, transform=fig.transFigure)
    save_slide_figure(fig, ASSETS / "mpl_code_subplots.png", tight=True)


def fig_mpl_code_axes_methods():
    """Слайд 4: методы Axes."""
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=(4.2, 3.8))
    _code_banner(fig, "ax.plot()  ·  ax.scatter()  ·  ax.set_xlabel()")
    style_axes(ax)
    x = np.linspace(0, 6, 40)
    y = 0.8 * x + 2 + RNG.normal(0, 0.4, 40)
    ax.plot(x, 0.8 * x + 2, color=C2, lw=2.2, linestyle="--", label="ax.plot()")
    ax.scatter(x[::3], y[::3], c=C0, s=35, alpha=0.75, label="ax.scatter()")
    ax.set_xlabel("признак X")
    ax.set_ylabel("таргет Y")
    _grid(ax)
    fig.subplots_adjust(top=0.82, bottom=0.18)
    save_slide_figure(fig, ASSETS / "mpl_code_axes_methods.png", tight=True)


def fig_mpl_code_tight_layout():
    """Слайд 4: plt.tight_layout()."""
    apply_matplotlib_slide_style()
    fig = plt.figure(figsize=(4.6, 3.6))
    _code_banner(fig, "plt.tight_layout()")
    ax_bad = fig.add_axes([0.02, 0.12, 0.42, 0.52])
    ax_good = fig.add_axes([0.52, 0.12, 0.44, 0.52])
    for ax, title in [(ax_bad, "без tight_layout"), (ax_good, "с tight_layout()")]:
        style_axes(ax)
        ax.plot([1, 2, 3], [1, 4, 2], "o-", color=C0)
        ax.set_xlabel("длинная подпись X")
        ax.set_ylabel("таргет")
        style_panel_title(ax, title)
    fig.text(0.24, 0.02, "← подпись обрезана", ha="center", fontsize=FONT_ANNOT - 1, color=C3)
    save_slide_figure(fig, ASSETS / "mpl_code_tight_layout.png", tight=True)


def fig_subplot_train_test_clear():
    """Слайд 5: понятное сравнение train vs test."""
    apply_matplotlib_slide_style()
    train_age = RNG.normal(32, 7, 250)
    test_age = RNG.normal(39, 8, 250)
    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE_SINGLE)
    for ax in axes:
        style_axes(ax)
    axes[0].hist(train_age, bins=18, color=C0, alpha=0.88, edgecolor="white")
    axes[0].set_xlabel("возраст")
    axes[0].set_ylabel("частота")
    style_panel_title(axes[0], "Train")
    axes[1].hist(test_age, bins=18, color=C1, alpha=0.88, edgecolor="white")
    axes[1].set_xlabel("возраст")
    style_panel_title(axes[1], "Test")
    fig.suptitle(
        "Один figure — две ячейки subplot",
        color=TEXT_DARK,
        fontsize=FONT_TITLE + 1,
        y=0.98,
    )
    fig.text(
        0.5,
        0.04,
        "Test сдвинут вправо → возможный data drift",
        ha="center",
        fontsize=FONT_ANNOT,
        color=C3,
        transform=fig.transFigure,
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.93])
    save_slide_figure(fig, ASSETS / "subplot_train_test_clear.png", tight=True)


def fig_mpl_architecture():
    """Слайд 4: Figure и Axes."""
    apply_matplotlib_slide_style()
    fig = plt.figure(figsize=FIGSIZE_SINGLE)
    ax = fig.add_axes([0.18, 0.12, 0.72, 0.62])
    style_axes(ax)
    x = np.linspace(0, 10, 40)
    y = 2 * x + RNG.normal(0, 1.5, 40)
    ax.scatter(x, y, c=C0, s=30)
    ax.set_xlabel("признак $x$")
    ax.set_ylabel("таргет $y$")
    style_panel_title(ax, "Axes — сам график")
    _grid(ax)
    fig.patches.append(
        Rectangle((0.08, 0.06), 0.84, 0.78, fill=False, ec=C2, lw=2.5, linestyle="--", transform=fig.transFigure)
    )
    fig.text(0.5, 0.92, "Figure — «холст»", ha="center", fontsize=FONT_ANNOT, color=C2)
    fig.text(0.5, 0.04, "fig, ax = plt.subplots()", ha="center", fontsize=FONT_ANNOT, color=TEXT_DARK)
    save_slide_figure(fig, ASSETS / "matplotlib_figure_axes_diagram.png", tight=True)


def fig_subplots():
    """Слайд 5: сетка subplot."""
    apply_matplotlib_slide_style()
    train_age = RNG.normal(32, 8, 200)
    test_age = RNG.normal(38, 9, 200)
    fig, axes = plt.subplots(2, 2, figsize=FIGSIZE_SINGLE)
    for ax in axes.flat:
        style_axes(ax)
    axes[0, 0].hist(train_age, bins=20, color=C0, alpha=0.85, edgecolor="white")
    axes[0, 0].set_title("train: возраст", fontsize=FONT_TITLE)
    axes[0, 1].hist(test_age, bins=20, color=C1, alpha=0.85, edgecolor="white")
    axes[0, 1].set_title("test: возраст", fontsize=FONT_TITLE)
    axes[1, 0].boxplot([train_age, test_age], tick_labels=["train", "test"], patch_artist=True,
                       boxprops=dict(facecolor=C0, alpha=0.5))
    axes[1, 0].set_title("сравнение", fontsize=FONT_TITLE)
    axes[1, 1].scatter(train_age[:60], test_age[:60], c=C2, s=22, alpha=0.7)
    axes[1, 1].set_xlabel("train")
    axes[1, 1].set_ylabel("test")
    axes[1, 1].set_title("пары", fontsize=FONT_TITLE)
    fig.suptitle("subplots(2, 2)", color=TEXT_DARK, fontsize=FONT_TITLE, y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save_slide_figure(fig, ASSETS / "subplot_grid_train_test.png", tight=True)


def fig_customization():
    """Слайд 6: цвета, стили, аннотации."""
    apply_matplotlib_slide_style()
    x = np.linspace(0, 10, 30)
    y = 2 * x + RNG.normal(0, 1.2, 30)
    y_out = y.copy()
    y_out[18] = 28
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ax.plot(x, 2 * x, "--", color=C2, lw=2.2, label="тренд")
    ax.scatter(x, y_out, c=C0, s=45, alpha=0.65, edgecolors="white", label="точки")
    ax.scatter([x[18]], [y_out[18]], c=C3, s=120, zorder=5)
    ax.annotate(
        "выброс",
        xy=(x[18], y_out[18]),
        xytext=(x[18] + 1.5, y_out[18] - 4),
        fontsize=FONT_ANNOT,
        color=C3,
        arrowprops=dict(arrowstyle="->", color=C3),
    )
    ax.set_xlabel("признак")
    ax.set_ylabel("таргет")
    style_panel_title(ax, "alpha, linestyle, annotate")
    _grid(ax)
    save_single_panel_figure(fig, ax, ASSETS / "customization_annotate_legend.png", legend_ncol=2)


def fig_save_export():
    """Слайд 7: сохранение и экспорт — все форматы из текста слайда."""
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    style_panel_title(ax, "Куда сохранять график")
    formats = [
        (0.35, 4.6, "PNG\ndpi = 300", "#d4edda"),
        (2.55, 4.6, "SVG / PDF\nвектор", "#cce5ff"),
        (4.75, 4.6, "transparent\n= True", "#f8d7da"),
        (6.95, 4.6, "HTML\n(plotly)", "#fff3cd"),
    ]
    for x, y, txt, fc in formats:
        _box(ax, (x, y), 1.85, 1.55, txt, fc=fc)
    _box(ax, (1.2, 1.55), 7.6, 1.35, "bbox_inches = 'tight'\nиначе обрежутся подписи осей", fc="white", ec=C3)
    ax.text(5.0, 0.55, "savefig · write_html", ha="center", fontsize=FONT_ANNOT, color="#666666")
    save_single_panel_figure(fig, ax, ASSETS / "export_formats_comparison.png")


def fig_plotly_scatter():
    """Слайд 8: plotly scatter (статическая аппроксимация)."""
    apply_matplotlib_slide_style()
    df = _housing_df(90)
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    cities = df["город"].unique()
    colors = {c: col for c, col in zip(cities, [C0, C1, C2])}
    for city in cities:
        sub = df[df["город"] == city]
        ax.scatter(sub["площадь"], sub["цена"], c=colors[city], s=40, alpha=0.75, label=city, edgecolors="white")
    ax.set_xlabel("площадь, м²")
    ax.set_ylabel("цена")
    style_panel_title(ax, "px.scatter(color=..., hover)")
    ax.text(0.03, 0.97, "≈ plotly: zoom + hover", transform=ax.transAxes, va="top", fontsize=FONT_ANNOT, color="#666666")
    _grid(ax)
    save_single_panel_figure(fig, ax, ASSETS / "plotly_express_scatter_hover.png", legend_ncol=3)


def fig_plotly_advanced():
    """Слайд 9: plotly advanced (3D + анимация как 2 панели)."""
    apply_matplotlib_slide_style()
    X, y = make_blobs(n_samples=90, centers=3, random_state=42, cluster_std=0.9)
    years = RNG.integers(2019, 2024, 90)
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)
    ax = axes[0]
    style_axes(ax)
    sc = ax.scatter(X[:, 0], X[:, 1], c=years, cmap="viridis", s=45, edgecolors="white")
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    style_panel_title(ax, "animation_frame='year' (цвет=год)")
    cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("год", fontsize=FONT_ANNOT)

    ax = axes[1]
    style_axes(ax)
    ax.scatter(X[:, 0], X[:, 1], c=y, cmap="Set2", s=45, alpha=0.85)
    ax.set_xlabel("PCA₁")
    ax.set_ylabel("PCA₂")
    style_panel_title(ax, "scatter_3d → 2D проекция")
    save_dual_col_figure(fig, axes, ASSETS / "plotly_3d_animation_demo.png")


def fig_hist_kde():
    """Слайд 10: гистограмма + KDE."""
    apply_matplotlib_slide_style()
    income = np.concatenate([RNG.lognormal(3.8, 0.35, 180), RNG.normal(120, 8, 40)])
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    sns.histplot(income, kde=True, ax=ax, color=C0, bins=28, edgecolor="white")
    ax.axvline(np.median(income), color=C3, ls="--", lw=1.8, label="медиана")
    ax.set_xlabel("доход")
    ax.set_ylabel("частота")
    style_panel_title(ax, "Heavy tail → log1p?")
    save_single_panel_figure(fig, ax, ASSETS / "histplot_kde_heavy_tail.png")


def fig_boxplot():
    """Слайд 11: box plot."""
    apply_matplotlib_slide_style()
    df = _housing_df(150)
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    sns.boxplot(data=df, x="город", y="цена", hue="город", ax=ax, palette=[C0, C1, C2], legend=False)
    n_out = sum(
        (s > s.quantile(0.75) + 1.5 * (s.quantile(0.75) - s.quantile(0.25))).sum()
        for _, s in df.groupby("город")["цена"]
    )
    ax.set_xlabel("город")
    ax.set_ylabel("цена")
    style_panel_title(ax, "точки за «усами» — выбросы")
    ax.text(0.98, 0.95, f"выбросов: {int(n_out)}", transform=ax.transAxes, ha="right", va="top", fontsize=FONT_ANNOT)
    save_single_panel_figure(fig, ax, ASSETS / "boxplot_outliers_iqr.png")


def fig_violin():
    """Слайд 12: violin plot — бimodal в одной группе."""
    apply_matplotlib_slide_style()
    moscow = np.concatenate([RNG.normal(70, 8, 60), RNG.normal(130, 10, 50)])
    spb = RNG.normal(85, 15, 110)
    kzn = RNG.normal(55, 10, 100)
    df = pd.DataFrame({
        "доход": np.concatenate([moscow, spb, kzn]),
        "город": ["Москва"] * 110 + ["СПб"] * 110 + ["Казань"] * 100,
    })
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    sns.violinplot(data=df, x="город", y="доход", hue="город", ax=ax, palette=[C0, C1, C2], inner="box", legend=False)
    ax.set_xlabel("город")
    ax.set_ylabel("доход")
    style_panel_title(ax, "бimodal в Москве — box скрыл бы")
    ax.annotate("2 группы", xy=(0, 125), xytext=(0.6, 145), fontsize=FONT_ANNOT, color=C3,
                arrowprops=dict(arrowstyle="->", color=C3))
    save_single_panel_figure(fig, ax, ASSETS / "violin_vs_box_bimodal.png")


def fig_scatter_joint():
    """Слайд 13: scatter + marginal."""
    apply_matplotlib_slide_style()
    df = _housing_df(100)
    g = sns.jointplot(data=df, x="площадь", y="цена", hue="город", height=4.2, palette=[C0, C1, C2], s=35)
    g.ax_joint.set_xlabel("площадь, м²")
    g.ax_joint.set_ylabel("цена")
    style_panel_title(g.ax_joint, "jointplot: связь + маргинали")
    g.ax_marg_x.set_ylabel("")
    g.ax_marg_y.set_xlabel("")
    save_slide_figure(g.fig, ASSETS / "jointplot_hex_marginals.png", tight=True)


def fig_missingno():
    """Слайд 14: паттерн пропусков (аппроксимация missingno)."""
    apply_matplotlib_slide_style()
    n, p = 40, 8
    cols = [f"признак_{i+1}" for i in range(p)]
    mask = np.ones((n, p), dtype=bool)
    mask[15:30, 2:5] = False
    mask[25:40, 6:8] = False
    mask[RNG.choice(n, 12, replace=False), 0] = False
    data = RNG.normal(0, 1, (n, p))
    data[~mask] = np.nan
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    present = np.where(mask, 1, 0)
    ax.imshow(present, aspect="auto", cmap="Greys", interpolation="nearest")
    ax.set_yticks([])
    ax.set_xticks(range(p))
    ax.set_xticklabels(cols, rotation=45, ha="right")
    style_panel_title(ax, "msno.matrix — блоки ≠ случайны")
    ax.text(0.02, 0.95, "MNAR: A и B пропадают вместе", transform=ax.transAxes, va="top", fontsize=FONT_ANNOT, color=C3)
    save_single_panel_figure(fig, ax, ASSETS / "missingno_matrix_dendrogram.png")


def fig_heatmap():
    """Слайд 15: heatmap корреляций."""
    apply_matplotlib_slide_style()
    n = 120
    x1 = RNG.normal(0, 1, n)
    x2 = 0.92 * x1 + RNG.normal(0, 0.15, n)
    x3 = -0.6 * x1 + RNG.normal(0, 0.4, n)
    y = 2 * x1 + RNG.normal(0, 0.5, n)
    df = pd.DataFrame({"площадь": x1, "площадь_ft": x2, "этаж": x3, "цена": y})
    corr = df.corr()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(corr.columns, rotation=30, ha="right")
    ax.set_yticklabels(corr.columns)
    for i in range(4):
        for j in range(4):
            v = corr.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=FONT_HEATMAP,
                    color=heatmap_text_color(abs(v), 0, 1))
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    style_panel_title(ax, "r > 0.9 → дубликат признака")
    save_single_panel_figure(fig, ax, ASSETS / "correlation_heatmap_multicollinearity.png")


def fig_ecdf_drift():
    """Слайд 16: ECDF train vs prod."""
    apply_matplotlib_slide_style()
    train = RNG.normal(32, 6, 300)
    prod = RNG.normal(40, 7, 300)
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    sns.ecdfplot(train, ax=ax, color=C0, label="train", linewidth=2.2)
    sns.ecdfplot(prod, ax=ax, color=C3, label="production", linewidth=2.2)
    ax.set_xlabel("возраст")
    ax.set_ylabel("доля < x")
    style_panel_title(ax, "расхождение ECDF = data drift")
    _grid(ax)
    save_single_panel_figure(fig, ax, ASSETS / "ecdf_train_prod_drift.png", legend_ncol=2)


def fig_countplot():
    """Слайд 17: дисбаланс классов."""
    apply_matplotlib_slide_style()
    counts = pd.Series({"класс 0": 950, "класс 1": 50})
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    bars = ax.bar(counts.index, counts.values, color=[C0, C3], edgecolor="white")
    ax.set_ylabel("количество")
    ax.set_xlabel("таргет")
    style_panel_title(ax, "100:1 — accuracy бесполезна")
    for bar, v in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 20, str(v), ha="center", fontsize=FONT_ANNOT)
    ax.text(0.5, 0.85, "→ PR-AUC, class_weight", transform=ax.transAxes, ha="center", fontsize=FONT_ANNOT, color=C3)
    save_single_panel_figure(fig, ax, ASSETS / "countplot_class_imbalance.png")


def fig_decision_boundary():
    """Слайд 18: границы решений."""
    apply_matplotlib_slide_style()
    X, y = make_classification(n_samples=120, n_features=2, n_redundant=0, n_clusters_per_class=1, random_state=42)
    clf = DecisionTreeClassifier(max_depth=3, random_state=42).fit(X, y)
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    DecisionBoundaryDisplay.from_estimator(clf, X, ax=ax, alpha=0.35, cmap="RdYlBu", response_method="predict")
    ax.scatter(X[y == 0, 0], X[y == 0, 1], c=C0, s=35, edgecolors="white", label="класс 0")
    ax.scatter(X[y == 1, 0], X[y == 1, 1], c=C1, s=35, edgecolors="white", label="класс 1")
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    style_panel_title(ax, "DecisionBoundaryDisplay")
    save_single_panel_figure(fig, ax, ASSETS / "decision_boundary_linear_nonlinear.png", legend_ncol=2)


def fig_pca_tsne():
    """Слайд 19: PCA и t-SNE."""
    apply_matplotlib_slide_style()
    X, y = make_blobs(n_samples=180, centers=4, random_state=42, cluster_std=0.85)
    pca = PCA(n_components=2, random_state=42).fit_transform(X)
    tsne = TSNE(n_components=2, random_state=42, perplexity=30, init="pca").fit_transform(X)
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)
    for ax, emb, title in [(axes[0], pca, "PCA — глобальная структура"), (axes[1], tsne, "t-SNE — локальные кластеры")]:
        style_axes(ax)
        for cls, col in zip(range(4), [C0, C1, C2, C3]):
            ax.scatter(emb[y == cls, 0], emb[y == cls, 1], c=col, s=30, label=f"кл. {cls}", alpha=0.85)
        ax.set_xlabel("компонента 1")
        ax.set_ylabel("компонента 2")
        style_panel_title(ax, title)
    save_dual_col_figure(fig, axes, ASSETS / "pca_vs_umap_clusters.png")


def fig_elbow_silhouette():
    """Слайд 20: elbow + silhouette."""
    apply_matplotlib_slide_style()
    X, _ = make_blobs(n_samples=200, centers=4, random_state=42, cluster_std=0.9)
    ks = range(2, 9)
    wcss = []
    for k in ks:
        wcss.append(KMeans(n_clusters=k, random_state=42, n_init=10).fit(X).inertia_)
    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE_SINGLE)
    style_axes(axes[0])
    axes[0].plot(list(ks), wcss, "o-", color=C0, lw=2.2, markersize=7)
    axes[0].axvline(4, color=C3, ls="--", lw=1.5, label="локоть K=4")
    axes[0].set_xlabel("K")
    axes[0].set_ylabel("WCSS")
    style_panel_title(axes[0], "Elbow method")

    from sklearn.metrics import silhouette_samples, silhouette_score

    k = 4
    labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
    sil = silhouette_samples(X, labels)
    style_axes(axes[1])
    y_lower = 0
    for i in range(k):
        vals = np.sort(sil[labels == i])
        y_upper = y_lower + len(vals)
        axes[1].fill_betweenx(np.arange(y_lower, y_upper), 0, vals, alpha=0.7, color=[C0, C1, C2, C3][i])
        axes[1].text(-0.05, y_lower + 0.5 * len(vals), f"K{i}", fontsize=FONT_ANNOT)
        y_lower = y_upper + 8
    axes[1].axvline(silhouette_score(X, labels), color=C3, ls="--", lw=1.8)
    axes[1].set_xlabel("silhouette")
    style_panel_title(axes[1], f"score={silhouette_score(X, labels):.2f}")
    fig.tight_layout()
    save_slide_figure(fig, ASSETS / "elbow_silhouette_kmeans.png", tight=True)


def fig_residuals():
    """Слайд 21: residual plot."""
    apply_matplotlib_slide_style()
    x = np.linspace(0.5, 10, 80)
    y = 2 * x + 1 + RNG.normal(0, 1.2, 80)
    y[40:55] += 0.35 * (x[40:55] - 5) ** 2
    pred = LinearRegression().fit(x.reshape(-1, 1), y).predict(x.reshape(-1, 1))
    resid = y - pred
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ax.scatter(pred, resid, c=C0, s=28, alpha=0.75)
    ax.axhline(0, color="#444444", lw=0.9)
    z = np.polyfit(pred, resid, 2)
    xx = np.linspace(pred.min(), pred.max(), 100)
    ax.plot(xx, np.polyval(z, xx), color=C3, lw=2, label="LOWESS-тренд")
    ax.set_xlabel("$\\hat{y}$")
    ax.set_ylabel("остаток")
    style_panel_title(ax, "U-форма → нелинейность")
    save_single_panel_figure(fig, ax, ASSETS / "residual_plot_good_bad.png")


def fig_qq():
    """Слайд 22: Q-Q plot."""
    apply_matplotlib_slide_style()
    resid = RNG.standard_t(df=3, size=200)
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    stats.probplot(resid, dist="norm", plot=ax)
    ax.get_lines()[0].set_markerfacecolor(C0)
    ax.get_lines()[0].set_markeredgecolor("white")
    ax.get_lines()[0].set_markersize(5)
    ax.get_lines()[1].set_color(C3)
    ax.get_lines()[1].set_linewidth(2)
    ax.set_xlabel("теор. квантили")
    ax.set_ylabel("остатки")
    style_panel_title(ax, "тяжёлые хвосты → MAE/Huber")
    save_single_panel_figure(fig, ax, ASSETS / "qqplot_residuals_normality.png")


def fig_pred_vs_actual():
    """Слайд 23: predicted vs actual."""
    apply_matplotlib_slide_style()
    y_true = RNG.uniform(20, 100, 70)
    y_pred = 0.92 * y_true + 8 + RNG.normal(0, 5, 70)
    r2 = 1 - np.sum((y_true - y_pred) ** 2) / np.sum((y_true - y_true.mean()) ** 2)
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ax.scatter(y_true, y_pred, c=C0, s=35, alpha=0.8)
    lim = [min(y_true.min(), y_pred.min()) - 5, max(y_true.max(), y_pred.max()) + 5]
    ax.plot(lim, lim, "r--", lw=2, label="$y=x$")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel("факт $y$")
    ax.set_ylabel("прогноз $\\hat{y}$")
    style_panel_title(ax, f"$R^2$={r2:.2f}, RMSE={rmse:.1f}")
    _grid(ax)
    save_single_panel_figure(fig, ax, ASSETS / "predicted_vs_actual_diagonal.png", legend_ncol=1)


def fig_confusion_matrix():
    """Слайд 24: confusion matrix."""
    apply_matplotlib_slide_style()
    X, y = make_classification(n_samples=200, weights=[0.7, 0.3], random_state=42)
    clf = LogisticRegression(max_iter=500).fit(X, y)
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ConfusionMatrixDisplay.from_estimator(clf, X, y, ax=ax, cmap="Blues", colorbar=False)
    ax.set_xlabel("прогноз")
    ax.set_ylabel("факт")
    style_panel_title(ax, "off-diagonal = путаница классов")
    save_single_panel_figure(fig, ax, ASSETS / "confusion_matrix_heatmap.png")


def fig_roc_pr():
    """Слайд 25: ROC и PR кривые."""
    apply_matplotlib_slide_style()
    X, y = make_classification(n_samples=300, weights=[0.85, 0.15], random_state=42)
    clf = LogisticRegression(max_iter=500).fit(X, y)
    prob = clf.predict_proba(X)[:, 1]
    fpr, tpr, _ = roc_curve(y, prob)
    prec, rec, _ = precision_recall_curve(y, prob)
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)
    style_axes(axes[0])
    axes[0].plot(fpr, tpr, color=C0, lw=2.2, label=f"ROC AUC={auc(fpr, tpr):.2f}")
    axes[0].plot([0, 1], [0, 1], "--", color="#888888", lw=1)
    axes[0].set_xlabel("FPR")
    axes[0].set_ylabel("TPR")
    style_panel_title(axes[0], "ROC")
    axes[0].legend(**legend_kwargs())

    style_axes(axes[1])
    axes[1].plot(rec, prec, color=C1, lw=2.2, label=f"PR AUC={auc(rec, prec):.2f}")
    axes[1].set_xlabel("recall")
    axes[1].set_ylabel("precision")
    style_panel_title(axes[1], "PR важнее при дисбалансе")
    axes[1].legend(**legend_kwargs())
    save_dual_col_figure(fig, axes, ASSETS / "roc_pr_curves_overlay.png")


def fig_learning_curve():
    """Слайд 26: learning curve."""
    apply_matplotlib_slide_style()
    X, y = make_regression(n_samples=200, n_features=8, noise=12, random_state=42)
    sizes, train_scores, val_scores = learning_curve(
        DecisionTreeClassifier(max_depth=6, random_state=42),
        X,
        np.digitize(y, bins=[-np.inf, np.median(y), np.inf]),
        cv=4,
        train_sizes=np.linspace(0.2, 1.0, 6),
        scoring="accuracy",
        random_state=42,
    )
    train_m, train_s = train_scores.mean(1), train_scores.std(1)
    val_m, val_s = val_scores.mean(1), val_scores.std(1)
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ax.plot(sizes, train_m, "o-", color=C0, lw=2, label="train")
    ax.fill_between(sizes, train_m - train_s, train_m + train_s, alpha=0.15, color=C0)
    ax.plot(sizes, val_m, "o-", color=C3, lw=2, label="validation")
    ax.fill_between(sizes, val_m - val_s, val_m + val_s, alpha=0.15, color=C3)
    ax.set_xlabel("размер выборки")
    ax.set_ylabel("accuracy")
    style_panel_title(ax, "train ↑ val ↓ → переобучение")
    _grid(ax)
    save_single_panel_figure(fig, ax, ASSETS / "learning_curve_overfitting.png", legend_ncol=2)


def fig_cv_boxplot():
    """Слайд 27: CV boxplot."""
    apply_matplotlib_slide_style()
    X, y = make_classification(n_samples=180, random_state=42)
    scores_a = cross_val_score(LogisticRegression(max_iter=500), X, y, cv=8, scoring="accuracy")
    scores_b = cross_val_score(RandomForestClassifier(n_estimators=30, random_state=42), X, y, cv=8, scoring="accuracy")
    df = pd.DataFrame({
        "accuracy": np.concatenate([scores_a, scores_b]),
        "модель": ["LogReg"] * 8 + ["RandomForest"] * 8,
    })
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    sns.boxplot(data=df, x="модель", y="accuracy", hue="модель", ax=ax, palette=[C0, C1], legend=False)
    ax.set_ylabel("accuracy по фолдам")
    style_panel_title(ax, "большой разброс = нестабильность")
    save_single_panel_figure(fig, ax, ASSETS / "cv_scores_stability_boxplot.png")


def fig_grid_search():
    """Слайд 28: grid search heatmap."""
    apply_matplotlib_slide_style()
    depths = [2, 4, 6, 8, 10]
    leaves = [1, 2, 5, 10, 20]
    grid = np.array([
        [0.72, 0.78, 0.81, 0.80, 0.77],
        [0.75, 0.82, 0.85, 0.84, 0.79],
        [0.73, 0.80, 0.86, 0.87, 0.81],
        [0.70, 0.77, 0.84, 0.85, 0.78],
        [0.68, 0.74, 0.80, 0.81, 0.75],
    ])
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    im = ax.imshow(grid, cmap="viridis", aspect="auto", vmin=0.65, vmax=0.9)
    ax.set_xticks(range(len(leaves)))
    ax.set_yticks(range(len(depths)))
    ax.set_xticklabels(leaves)
    ax.set_yticklabels(depths)
    ax.set_xlabel("min_samples_leaf")
    ax.set_ylabel("max_depth")
    for i in range(5):
        for j in range(5):
            v = grid[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=FONT_HEATMAP,
                    color=heatmap_text_color(v, 0.65, 0.9))
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="CV accuracy")
    style_panel_title(ax, "плато — широкий диапазон OK")
    save_single_panel_figure(fig, ax, ASSETS / "grid_search_heatmap_plateau.png")


def fig_permutation_importance():
    """Слайд 29: permutation importance."""
    apply_matplotlib_slide_style()
    X, y = make_classification(n_samples=200, n_features=6, n_informative=3, random_state=42)
    names = ["площадь", "этаж", "район", "возраст", "шум_1", "шум_2"]
    clf = RandomForestClassifier(n_estimators=60, random_state=42).fit(X, y)
    result = permutation_importance(clf, X, y, n_repeats=15, random_state=42)
    order = np.argsort(result.importances_mean)
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ax.barh(
        [names[i] for i in order],
        result.importances_mean[order],
        xerr=result.importances_std[order],
        color=C0,
        edgecolor="white",
        capsize=3,
    )
    ax.set_xlabel("падение accuracy")
    style_panel_title(ax, "permutation > feature_importances_")
    save_single_panel_figure(fig, ax, ASSETS / "permutation_importance_barh.png")


def fig_themes():
    """Слайд 30: стили и темы."""
    apply_matplotlib_slide_style()
    x = np.linspace(0, 5, 30)
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)
    with plt.style.context("default"):
        apply_matplotlib_slide_style()
        ax = axes[0]
        style_axes(ax)
        ax.plot(x, np.sin(x), color=C0, lw=2, label="sin")
        ax.plot(x, np.cos(x), color=C1, lw=2, label="cos")
        ax.set_xlabel("x")
        style_panel_title(ax, "slide style (контраст)")
        _grid(ax)
    with plt.style.context("ggplot"):
        ax = axes[1]
        ax.plot(x, np.sin(x), lw=2, label="sin")
        ax.plot(x, np.cos(x), lw=2, label="cos")
        ax.set_xlabel("x")
        ax.set_title("ggplot (другая тема)", fontsize=FONT_TITLE)
        ax.grid(True, alpha=0.4)
    save_dual_col_figure(fig, axes, ASSETS / "theme_before_after_seaborn.png")


def fig_overlay_hist():
    """pptx 32: overlay гистограмм train vs test."""
    apply_matplotlib_slide_style()
    train = RNG.normal(30, 5, 400)
    test = RNG.normal(36, 6, 400)
    fig = plt.figure(figsize=(4.2, 3.8))
    _code_banner(fig, "plt.hist(train, alpha=0.5); plt.hist(test, alpha=0.5)")
    ax = fig.add_axes([0.14, 0.12, 0.78, 0.62])
    style_axes(ax)
    ax.hist(train, bins=22, alpha=0.55, color=C0, label="train", edgecolor="white")
    ax.hist(test, bins=22, alpha=0.55, color=C3, label="test", edgecolor="white")
    ax.set_xlabel("возраст")
    ax.set_ylabel("частота")
    ax.legend(**legend_kwargs(ncol=2))
    _grid(ax)
    save_slide_figure(fig, ASSETS / "overlay_hist_train_test.png", tight=True)


def fig_overlay_lines():
    """pptx 32: overlay линий train vs val scores."""
    apply_matplotlib_slide_style()
    x = np.arange(1, 11)
    train_scores = 0.95 - 0.35 / x
    val_scores = 0.62 + 0.18 * (1 - np.exp(-x / 4))
    fig = plt.figure(figsize=(4.2, 3.8))
    _code_banner(fig, "plt.plot(train_scores); plt.plot(val_scores)")
    ax = fig.add_axes([0.14, 0.12, 0.78, 0.62])
    style_axes(ax)
    ax.plot(x, train_scores, "o-", color=C0, lw=2, label="train")
    ax.plot(x, val_scores, "o-", color=C3, lw=2, label="validation")
    ax.set_xlabel("эпоха / размер выборки")
    ax.set_ylabel("метрика")
    ax.legend(**legend_kwargs(ncol=2))
    _grid(ax)
    save_slide_figure(fig, ASSETS / "overlay_lines_scores.png", tight=True)


def fig_overlay_facetgrid():
    """pptx 32: FacetGrid по категории."""
    apply_matplotlib_slide_style()
    df = _housing_df(150)
    g = sns.FacetGrid(df, col="город", height=1.55, aspect=0.82)
    g.map_dataframe(sns.histplot, x="площадь", bins=10, color=C0, edgecolor="white")
    g.set_titles(col_template="{col_name}", size=11)
    g.set_axis_labels("площадь", "частота")
    fig = g.figure
    fig.set_size_inches(4.2, 3.8)
    _code_banner(fig, "sns.FacetGrid(df, col='category'); g.map(...)")
    save_slide_figure(fig, ASSETS / "overlay_facetgrid_demo.png", tight=True)


def fig_overlay_plotly_subplots():
    """pptx 32: схема make_subplots 2×2."""
    apply_matplotlib_slide_style()
    fig = plt.figure(figsize=(4.2, 3.8))
    _code_banner(fig, "make_subplots(rows=2, cols=2)")
    for i, (row, col) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)], start=1):
        left = 0.12 + col * 0.44
        bottom = 0.52 - row * 0.40
        ax = fig.add_axes([left, bottom, 0.36, 0.32])
        style_axes(ax)
        xs = np.linspace(0, 1, 12)
        ax.plot(xs, xs ** (i * 0.4 + 0.6), color=[C0, C1, C2, C3][i - 1], lw=2)
        ax.set_title(f"panel {i}", fontsize=10)
        _grid(ax)
    save_slide_figure(fig, ASSETS / "overlay_plotly_subplots.png", tight=True)


def fig_figsize_dpi():
    """Слайд 32: figsize и DPI."""
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)
    for ax, title, note in [
        (axes[0], "экран: 10×6 @ 100 dpi", "быстрый просмотр"),
        (axes[1], "печать: 10×6 @ 300 dpi", "статья / отчёт"),
    ]:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        style_panel_title(ax, title)
        ax.add_patch(Rectangle((0.15, 0.2), 0.7, 0.55, fc=BG_BOX, ec="#333333"))
        ax.text(0.5, 0.47, note, ha="center", va="center", fontsize=FONT_DIAGRAM, color=TEXT_DARK)
    save_dual_col_figure(fig, axes, ASSETS / "figsize_dpi_guidelines.png")


def fig_antipatterns():
    """Слайд 33: антипаттерны vs best practices."""
    apply_matplotlib_slide_style()
    vals = [40, 25, 20, 15]
    labels = ["A", "B", "C", "D"]
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)
    ax = axes[0]
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")
    style_panel_title(ax, "✗ pie chart — углы вводят в заблуждение", color=C3)
    start = 90
    colors_pie = [C0, C1, C2, C3]
    for v, lab, col in zip(vals, labels, colors_pie):
        w = Wedge((0, 0), 1, start, start - v / sum(vals) * 360, fc=col, ec="white")
        ax.add_patch(w)
        start -= v / sum(vals) * 360

    ax = axes[1]
    style_axes(ax)
    ax.bar(labels, vals, color=colors_pie, edgecolor="white")
    ax.set_ylabel("доля, %")
    style_panel_title(ax, "✓ bar chart — сравнение очевидно", color=C2)
    save_dual_col_figure(fig, axes, ASSETS / "viz_antipatterns_best_practices.png")


def fig_checklist():
    """Слайд 34: чек-лист «график → задача»."""
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    style_panel_title(ax, "Какой график для какой задачи")
    rows = [
        ("распределение", "hist + KDE"),
        ("выбросы", "box plot"),
        ("группы", "violin"),
        ("связь", "scatter / joint"),
        ("пропуски", "missingno"),
        ("дрейф", "ECDF"),
        ("классы", "count / CM / ROC"),
        ("качество рег.", "residual / Q-Q"),
    ]
    for i, (task, chart) in enumerate(rows):
        y = 6.8 - i * 0.78
        ax.text(0.3, y, task, fontsize=FONT_ANNOT, color=TEXT_DARK, va="center")
        ax.text(4.5, y, "→", fontsize=FONT_ANNOT, ha="center", va="center")
        ax.text(5.2, y, chart, fontsize=FONT_ANNOT, color=C0, va="center", fontweight="bold")
    save_single_panel_figure(fig, ax, ASSETS / "viz_checklist_diagram.png")


def main():
    fig_philosophy()
    fig_pandas_plot()
    fig_mpl_code_subplots()
    fig_mpl_code_axes_methods()
    fig_mpl_code_tight_layout()
    fig_subplot_train_test_clear()
    fig_customization()
    fig_save_export()
    fig_plotly_advanced()
    fig_hist_kde()
    fig_boxplot()
    fig_violin()
    fig_scatter_joint()
    fig_missingno()
    fig_heatmap()
    fig_ecdf_drift()
    fig_countplot()
    fig_decision_boundary()
    fig_pca_tsne()
    fig_elbow_silhouette()
    fig_residuals()
    fig_qq()
    fig_pred_vs_actual()
    fig_confusion_matrix()
    fig_roc_pr()
    fig_learning_curve()
    fig_cv_boxplot()
    fig_grid_search()
    fig_permutation_importance()
    fig_themes()
    fig_overlay_hist()
    fig_overlay_lines()
    fig_overlay_facetgrid()
    fig_overlay_plotly_subplots()
    fig_figsize_dpi()
    fig_antipatterns()
    print("vizualizatsiya visuals OK")


if __name__ == "__main__":
    main()
