"""Генерация всех иллюстраций pandas."""
from __future__ import annotations

import sys
import time
from io import StringIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "agents"))
from viz_style import (  # noqa: E402
    BG_BOX,
    TEXT_DARK,
    apply_matplotlib_slide_style,
    heatmap_text_color,
    save_slide_figure,
    style_axes,
)

ASSETS = Path(__file__).resolve().parent
RNG = np.random.default_rng(42)


def _titanic() -> pd.DataFrame:
    from sklearn.datasets import fetch_openml

    raw = fetch_openml("titanic", version=1, as_frame=True, parser="auto")
    df = raw.frame.copy()
    df["Survived"] = df["survived"].astype(int)
    df["Pclass"] = df["pclass"].astype(int)
    df["Age"] = pd.to_numeric(df["age"], errors="coerce")
    df["Fare"] = pd.to_numeric(df["fare"], errors="coerce")
    df["Sex"] = df["sex"].astype(str)
    df["Embarked"] = df["embarked"].astype(str)
    df["Name"] = df["name"].astype(str)
    return df


def fig_pandas_ml_pipeline():
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=(5, 3.2))
    style_axes(ax)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.3, "CSV / OpenML"),
        (2.5, "DataFrame"),
        (4.7, "очистка"),
        (6.5, "groupby / merge"),
        (8.3, "sklearn"),
    ]
    for i, (x, label) in enumerate(boxes):
        ax.add_patch(FancyBboxPatch((x, 1.0), 1.5, 0.9, boxstyle="round,pad=0.05", fc=BG_BOX, ec="#333333"))
        ax.text(x + 0.75, 1.45, label, ha="center", va="center", fontsize=11)
        if i < len(boxes) - 1:
            ax.add_patch(FancyArrowPatch((x + 1.55, 1.45), (boxes[i + 1][0] - 0.05, 1.45), arrowstyle="->", mutation_scale=12, color="#333333"))
    ax.set_title("Путь табличных данных к модели")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "pandas_ml_pipeline.png")


def fig_series_dataframe_schema():
    apply_matplotlib_slide_style(compact=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for ax in axes:
        style_axes(ax)
        ax.axis("off")
    axes[0].set_title("Series")
    axes[0].text(0.05, 0.75, "index", fontsize=13, fontweight="bold")
    for i, (idx, val) in enumerate([("a", 10), ("b", 20), ("c", 15)]):
        axes[0].text(0.05, 0.55 - i * 0.15, f"{idx}  →  {val}", fontsize=12)
    axes[1].set_title("DataFrame")
    cols = ["Age", "Fare", "Sex"]
    data = [[22, 7.25, "M"], [38, 71.28, "F"], [26, 7.92, "F"]]
    for j, c in enumerate(cols):
        axes[1].text(0.2 + j * 0.28, 0.78, c, fontsize=12, fontweight="bold")
    for i, row in enumerate(data):
        for j, val in enumerate(row):
            axes[1].text(0.2 + j * 0.28, 0.58 - i * 0.14, str(val), fontsize=11)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "series_dataframe_schema.png")


def fig_read_csv_flow():
    apply_matplotlib_slide_style()
    csv_text = "name,age,fare\nAnna,22,7.25\nBob,38,71.3\n"
    df = pd.read_csv(StringIO(csv_text))
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.axis("off")
    ax.text(0.02, 0.92, "read_csv(...)", fontsize=13, fontweight="bold")
    ax.text(0.02, 0.72, csv_text.replace("\n", "\\n"), fontsize=10, family="monospace")
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc="center",
        cellLoc="center",
        bbox=[0.05, 0.05, 0.9, 0.45],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    ax.set_title(f"DataFrame {df.shape[0]}×{df.shape[1]}")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "read_csv_flow.png")


def fig_describe_snapshot():
    apply_matplotlib_slide_style()
    df = _titanic()[["Age", "Fare", "Pclass"]].describe().round(2)
    fig, ax = plt.subplots(figsize=(5, 3.2))
    style_axes(ax)
    ax.axis("off")
    table = ax.table(
        cellText=df.values,
        rowLabels=df.index,
        colLabels=df.columns,
        loc="center",
        cellLoc="center",
        bbox=[0.02, 0.05, 0.96, 0.85],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    ax.set_title("describe() — сводка числовых столбцов")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "describe_snapshot.png")


def fig_index_set_reset():
    apply_matplotlib_slide_style(compact=True)
    df = pd.DataFrame({"id": [101, 102, 103], "Age": [22, 38, 26], "Fare": [7.2, 71.3, 7.9]})
    df_idx = df.set_index("id")
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
    for ax, data, title in [(axes[0], df, "исходный индекс 0…n"), (axes[1], df_idx, "set_index('id')")]:
        style_axes(ax)
        ax.axis("off")
        ax.set_title(title)
        show = data.reset_index() if title.startswith("исход") else data.reset_index().set_index("id")
        tbl = show if not title.startswith("исход") else data
        cell = tbl.values if title.startswith("исход") else df_idx.reset_index().values
        cols = list(tbl.columns) if title.startswith("исход") else ["index"] + list(df_idx.columns)
        if not title.startswith("исход"):
            cell = np.column_stack([df_idx.index.values, df_idx.values])
            cols = ["id", "Age", "Fare"]
        table = ax.table(cellText=cell, colLabels=cols, loc="center", cellLoc="center", bbox=[0.05, 0.15, 0.9, 0.7])
        table.auto_set_font_size(False)
        table.set_fontsize(11)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "index_set_reset.png")


def fig_loc_vs_iloc():
    apply_matplotlib_slide_style(compact=True)
    df = pd.DataFrame(np.arange(1, 17).reshape(4, 4), columns=list("ABCD"), index=list("wxyz"))
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, title, mask in [
        (axes[0], "loc['x':'y', 'B':'C']", df.loc["x":"y", "B":"C"].values),
        (axes[1], "iloc[1:3, 1:3]", df.iloc[1:3, 1:3].values),
    ]:
        style_axes(ax)
        full = df.values
        table = ax.table(
            cellText=full,
            rowLabels=df.index,
            colLabels=df.columns,
            loc="center",
            cellLoc="center",
            bbox=[0.08, 0.12, 0.84, 0.72],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        sel = mask
        for (i, j), val in np.ndenumerate(sel):
            ri, cj = (1 if title.startswith("loc") else 2) + i, (2 if title.startswith("loc") else 2) + j
            table[(ri, cj)].set_facecolor("#cce5ff")
        ax.set_title(title)
        ax.axis("off")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "loc_vs_iloc.png")


def fig_boolean_filter():
    apply_matplotlib_slide_style()
    df = _titanic()[["Name", "Age", "Pclass"]].dropna().head(12).copy()
    mask = (df["Age"] > 30) & (df["Pclass"] == 1)
    fig, ax = plt.subplots(figsize=(5, 3.8))
    style_axes(ax)
    ax.axis("off")
    show = df.copy()
    show["Name"] = show["Name"].str.slice(0, 12)
    colors = [["#ffffff"] * 3 for _ in range(len(show))]
    for i, ok in enumerate(mask):
        if ok:
            colors[i] = ["#cce5ff"] * 3
    table = ax.table(
        cellText=show.values,
        colLabels=show.columns,
        loc="center",
        cellLoc="center",
        bbox=[0.02, 0.05, 0.96, 0.85],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            continue
        cell.set_facecolor(colors[i - 1][j])
    ax.set_title("Маска: Age>30 & Pclass==1")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "boolean_filter.png")


def fig_groupby_fare_pclass():
    apply_matplotlib_slide_style()
    df = _titanic()
    means = df.groupby("Pclass")["Fare"].mean().sort_index()
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.bar(means.index.astype(str), means.values, color=["#2ca02c", "#ff7f0e", "#d62728"])
    ax.set_xlabel("Pclass")
    ax.set_ylabel("средний Fare")
    ax.set_title("groupby: Fare сильно падает с классом")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "groupby_fare_pclass.png")


def fig_merge_diagram():
    apply_matplotlib_slide_style(compact=True)
    left = pd.DataFrame({"id": [1, 2, 3], "val": ["A", "B", "C"]})
    right = pd.DataFrame({"id": [2, 3, 4], "extra": ["x", "y", "z"]})
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for ax, how, title in [(axes[0], "inner", "inner merge"), (axes[1], "left", "left merge")]:
        style_axes(ax)
        ax.axis("off")
        m = pd.merge(left, right, on="id", how=how)
        ax.text(0.05, 0.85, f"{title}: {len(m)} строк", fontsize=13, fontweight="bold")
        table = ax.table(
            cellText=m.values,
            colLabels=m.columns,
            loc="center",
            cellLoc="center",
            bbox=[0.05, 0.15, 0.9, 0.55],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(11)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "merge_diagram.png")


def fig_missing_counts():
    apply_matplotlib_slide_style()
    df = _titanic()
    miss = df[["Age", "Fare", "Embarked"]].isna().sum()
    miss["Cabin"] = df.get("cabin", pd.Series(dtype=float)).isna().sum() if "cabin" in df.columns else 687
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.bar(miss.index.astype(str), miss.values, color="#1f77b4")
    ax.set_ylabel("число пропусков")
    ax.set_title("Пропуски по столбцам (Titanic)")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "missing_counts.png")


def fig_dtype_category():
    apply_matplotlib_slide_style(compact=True)
    s = pd.Series(["male", "female"] * 500)
    mem_obj = s.memory_usage(deep=True)
    s_cat = s.astype("category")
    mem_cat = s_cat.memory_usage(deep=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for ax, label, mem in [(axes[0], "object", mem_obj), (axes[1], "category", mem_cat)]:
        style_axes(ax)
        ax.bar(["память (байт)"], [mem], color="#1f77b4")
        ax.set_title(f"Sex as {label}\n{mem:,} B")
    fig.suptitle("category экономит память на повторах", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "dtype_category.png")


def fig_apply_map_transform():
    apply_matplotlib_slide_style(compact=True)
    mapping = {"S": 0, "C": 1, "Q": 2}
    embarked = pd.Series(["S", "C", "Q", "S", "C"])
    mapped = embarked.map(mapping)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
    for ax, data, title in [(axes[0], embarked, "до map"), (axes[1], mapped, "после map")]:
        style_axes(ax)
        ax.axis("off")
        ax.set_title(title)
        for i, v in enumerate(data):
            ax.text(0.3, 0.7 - i * 0.12, str(v), fontsize=14)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "apply_map_transform.png")


def fig_pivot_survival():
    apply_matplotlib_slide_style()
    df = _titanic()
    pt = df.pivot_table(values="Survived", index="Pclass", columns="Sex", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    im = ax.imshow(pt.values, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(pt.columns)))
    ax.set_xticklabels(pt.columns)
    ax.set_yticks(range(len(pt.index)))
    ax.set_yticklabels([f"Pclass {i}" for i in pt.index])
    for i in range(pt.shape[0]):
        for j in range(pt.shape[1]):
            val = pt.values[i, j]
            ax.text(j, i, f"{val:.0%}", ha="center", va="center", color=heatmap_text_color(val))
    ax.set_title("Доля выживших: женщины 1 класса — максимум")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "pivot_survival.png")


def fig_perf_vectorized():
    apply_matplotlib_slide_style()
    n = 200_000
    s = pd.Series(RNG.normal(0, 1, n))
    t0 = time.perf_counter()
    _ = s.apply(lambda x: x * 2 + 1)
    t_apply = time.perf_counter() - t0
    t0 = time.perf_counter()
    _ = s * 2 + 1
    t_vec = time.perf_counter() - t0
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.bar(["apply", "векторизация"], [t_apply, t_vec], color=["#d62728", "#2ca02c"])
    ax.set_ylabel("секунды")
    ax.set_title(f"Векторизация ≈ {t_apply / max(t_vec, 1e-9):.0f}× быстрее")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "perf_vectorized.png")


def fig_pandas_leakage():
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=(5, 3.2))
    style_axes(ax)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    steps = [(0.5, "весь df"), (3.0, "fillna(median)"), (5.5, "train_test_split"), (8.0, "model")]
    for x, label in steps:
        ax.add_patch(FancyBboxPatch((x, 1.0), 1.8, 0.9, boxstyle="round,pad=0.05", fc=BG_BOX, ec="#333333"))
        ax.text(x + 0.9, 1.45, label, ha="center", va="center", fontsize=10)
    ax.add_patch(FancyArrowPatch((2.4, 1.45), (2.95, 1.45), arrowstyle="->", mutation_scale=12, color="#333333"))
    ax.add_patch(FancyArrowPatch((4.9, 1.45), (5.45, 1.45), arrowstyle="->", mutation_scale=12, color="#333333"))
    ax.add_patch(FancyArrowPatch((7.4, 1.45), (7.95, 1.45), arrowstyle="->", mutation_scale=12, color="#333333"))
    ax.annotate("", xy=(3.0, 0.55), xytext=(8.0, 0.55), arrowprops=dict(arrowstyle="->", color="#d62728", lw=2))
    ax.text(5.5, 0.25, "утечка: median знал test", ha="center", color="#d62728", fontsize=11)
    ax.set_title("fillna до split — data leakage")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "pandas_leakage.png")


def fig_pandas_sklearn_pipeline():
    apply_matplotlib_slide_style()
    fig, ax = plt.subplots(figsize=(5, 3.0))
    style_axes(ax)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 3)
    ax.axis("off")
    blocks = [(0.2, "DataFrame"), (2.2, "split"), (4.0, "Imputer"), (6.0, "OHE"), (8.0, "Model")]
    for i, (x, label) in enumerate(blocks):
        ax.add_patch(FancyBboxPatch((x, 1.0), 1.6, 0.9, boxstyle="round,pad=0.05", fc=BG_BOX, ec="#333333"))
        ax.text(x + 0.8, 1.45, label, ha="center", va="center", fontsize=10)
        if i < len(blocks) - 1:
            ax.add_patch(FancyArrowPatch((x + 1.65, 1.45), (blocks[i + 1][0] - 0.05, 1.45), arrowstyle="->", mutation_scale=12, color="#333333"))
    ax.set_title("Pipeline после train_test_split")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "pandas_sklearn_pipeline.png")


def main():
    fig_pandas_ml_pipeline()
    fig_series_dataframe_schema()
    fig_read_csv_flow()
    fig_describe_snapshot()
    fig_index_set_reset()
    fig_loc_vs_iloc()
    fig_boolean_filter()
    fig_groupby_fare_pclass()
    fig_merge_diagram()
    fig_missing_counts()
    fig_dtype_category()
    fig_apply_map_transform()
    fig_pivot_survival()
    fig_perf_vectorized()
    fig_pandas_leakage()
    fig_pandas_sklearn_pipeline()
    print("pandas visuals OK")


if __name__ == "__main__":
    main()
