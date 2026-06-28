"""Генерация всех иллюстраций урока derevo_resheniy (viz_style + graphviz)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from graphviz import Digraph
from matplotlib.patches import Rectangle
from sklearn.tree import DecisionTreeClassifier

# Graphviz на Windows часто не в PATH для Python
for _gv in (
    Path(r"C:\Program Files\Graphviz\bin"),
    Path(r"C:\Program Files (x86)\Graphviz\bin"),
):
    if _gv.is_dir():
        os.environ["PATH"] = str(_gv) + os.pathsep + os.environ.get("PATH", "")
        break

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "agents"))
from viz_style import (  # noqa: E402
    FIGSIZE_SINGLE,
    TEXT_DARK,
    FONT_ANNOT,
    FONT_DIAGRAM,
    FONT_HEATMAP,
    FONT_SYMBOL,
    FONT_TICK,
    FONT_TITLE,
    apply_matplotlib_slide_style,
    save_slide_figure,
    style_axes,
)

ASSETS = Path(__file__).resolve().parent



def _graph_defaults(dot: Digraph) -> None:
    dot.attr(
        "node",
        shape="box",
        style="rounded,filled",
        fillcolor="white",
        fontcolor="#1a1a1a",
        fontname="Arial",
        fontsize=str(FONT_DIAGRAM),
    )
    dot.attr("edge", fontname="Arial", fontcolor="#1a1a1a", fontsize=str(FONT_TICK))


def fig_guess_number_tree() -> None:
    dot = Digraph()
    _graph_defaults(dot)
    dot.node("root", "Число > 4?")
    dot.node("l1", "Число > 2?")
    dot.node("r1", "Число > 6?")
    dot.node("ll", ">1?")
    dot.node("lr", ">3?")
    dot.node("rl", ">5?")
    dot.node("rr", ">7?")
    for name, label in [
        ("lll", "1"),
        ("llr", "2"),
        ("lrl", "3"),
        ("lrr", "4"),
        ("rll", "5"),
        ("rlr", "6"),
        ("rrl", "7"),
        ("rrr", "8"),
    ]:
        dot.node(name, label)
    for src, dst, label in [
        ("root", "l1", "Нет"),
        ("root", "r1", "Да"),
        ("l1", "ll", "Нет"),
        ("l1", "lr", "Да"),
        ("r1", "rl", "Нет"),
        ("r1", "rr", "Да"),
        ("ll", "lll", "Нет"),
        ("ll", "llr", "Да"),
        ("lr", "lrl", "Нет"),
        ("lr", "lrr", "Да"),
        ("rl", "rll", "Нет"),
        ("rl", "rlr", "Да"),
        ("rr", "rrl", "Нет"),
        ("rr", "rrr", "Да"),
    ]:
        dot.edge(src, dst, label=label, labeldistance="3")
    out = ASSETS / "guess_number_tree"
    dot.render(str(out), format="png", cleanup=True)
    print(f"Done: {out.name}.png")


def fig_akinator_tree() -> None:
    dot = Digraph()
    _graph_defaults(dot)
    dot.node("root", "Это человек?")
    dot.node("real", "Это реальный\nчеловек?")
    dot.node("animal", "Это животное?")
    dot.node("pushkin", "Пушкин")
    dot.node("sherlock", "Шерлок\nХолмс")
    dot.node("hedgehog", "Ёж")
    dot.node("orange", "Апельсин")
    dot.edge("root", "real", label="Да", labeldistance="2.5")
    dot.edge("root", "animal", label="Нет", labeldistance="2.5")
    dot.edge("real", "pushkin", label="Да", labeldistance="2.5")
    dot.edge("real", "sherlock", label="Нет", labeldistance="2.5")
    dot.edge("animal", "hedgehog", label="Да", labeldistance="2.5")
    dot.edge("animal", "orange", label="Нет", labeldistance="2.5")
    out = ASSETS / "akinator_tree"
    dot.render(str(out), format="png", cleanup=True)
    print(f"Done: {out.name}.png")


def fig_binary_classification_rectangles() -> None:
    apply_matplotlib_slide_style()
    rng = np.random.default_rng(42)
    n = 40
    x1 = rng.uniform(0, 10, n)
    x2 = rng.uniform(0, 10, n)
    y = ((x1 > 4) & (x2 > 3)) | ((x1 < 3) & (x2 < 6))
    y = y.astype(int)

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    colors = ["#1f77b4", "#ff7f0e"]
    markers = ["o", "^"]
    for c in (0, 1):
        mask = y == c
        ax.scatter(
            x1[mask],
            x2[mask],
            c=colors[c],
            marker=markers[c],
            s=60,
            label=f"Класс {c}",
            edgecolors=TEXT_DARK if c else "none",
            linewidths=0.5,
        )
    ax.add_patch(Rectangle((0, 0), 4, 10, alpha=0.12, color="blue"))
    ax.add_patch(Rectangle((4, 3), 6, 7, alpha=0.12, color="orange"))
    ax.add_patch(Rectangle((4, 0), 6, 3, alpha=0.12, color="blue"))
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.set_title("Границы решения: дерево глубины 2")
    ax.legend()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.grid(alpha=0.2)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "binary_classification_rectangles.png")
    print("Done: binary_classification_rectangles.png")


def fig_decision_boundary() -> None:
    apply_matplotlib_slide_style()
    rng = np.random.default_rng(42)
    n = 60
    x1 = rng.uniform(0, 10, n)
    x2 = rng.uniform(0, 10, n)
    y = np.zeros(n)
    y[(x1 > 3) & (x2 > 6)] = 1
    y[(x1 < 3) & (x2 > 3)] = 2

    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    clf.fit(np.column_stack([x1, x2]), y)

    xx, yy = np.meshgrid(np.linspace(0, 10, 200), np.linspace(0, 10, 200))
    z = clf.predict(np.column_stack([xx.ravel(), yy.ravel()])).reshape(xx.shape)

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ax.contourf(
        xx,
        yy,
        z,
        alpha=0.25,
        levels=[-0.5, 0.5, 1.5, 2.5],
        colors=["#1f77b4", "#ff7f0e", "#2ca02c"],
    )
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    markers = ["o", "^", "s"]
    for c in (0, 1, 2):
        mask = y == c
        ax.scatter(x1[mask], x2[mask], c=colors[c], marker=markers[c], s=60, label=f"Класс {c}")
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.set_title("Границы решения: дерево глубины 3")
    ax.legend()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "decision_boundary.png")
    print("Done: decision_boundary.png")


def fig_feature_importance() -> None:
    apply_matplotlib_slide_style()
    features = ["Возраст", "Доход", "Образование", "Стаж", "Пол", "Город", "ID"]
    importance = np.array([0.35, 0.25, 0.15, 0.12, 0.07, 0.04, 0.02])
    idx = np.argsort(importance)

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ax.barh(range(len(features)), importance[idx], color="steelblue")
    ax.set_yticks(range(len(features)))
    ax.set_yticklabels([features[i] for i in idx])
    ax.set_xlabel("Важность")
    ax.set_title("Важность признаков (feature_importances_)")
    ax.set_xlim(0, 0.45)
    ax.grid(alpha=0.3, axis="x")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "feature_importance.png")
    print("Done: feature_importance.png")


def fig_overfitting_curve() -> None:
    apply_matplotlib_slide_style()
    depth = np.arange(1, 16)
    train_acc = 0.7 + 0.3 * (1 - np.exp(-depth / 3))
    test_acc = 0.7 + 0.25 * np.exp(-((depth - 5) ** 2) / 8)

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ax.plot(depth, train_acc, "o-", label="Train accuracy", linewidth=2)
    ax.plot(depth, test_acc, "s-", label="Test accuracy", linewidth=2)
    ax.axvline(x=5, color="gray", linestyle=":", alpha=0.5)
    ax.axvspan(5, 15, alpha=0.1, color="red", label="Зона переобучения")
    ax.set_xlabel("Глубина дерева")
    ax.set_ylabel("Accuracy")
    ax.set_title("Переобучение дерева решений")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "overfitting_curve.png")
    print("Done: overfitting_curve.png")


def fig_impurity_functions() -> None:
    apply_matplotlib_slide_style()
    p = np.linspace(0, 1, 500)
    entropy = -p * np.log2(p + 1e-10) - (1 - p) * np.log2(1 - p + 1e-10)
    gini = 2 * p * (1 - p)
    misclass = 1 - np.maximum(p, 1 - p)

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ax.plot(p, entropy, label="Entropy", linewidth=2)
    ax.plot(p, gini, label="Gini", linewidth=2)
    ax.plot(p, misclass, label="Misclassification", linewidth=2, linestyle="--")
    ax.set_xlabel("p (доля класса 1)")
    ax.set_ylabel("Impurity")
    ax.set_title("Функции impurity для бинарного случая")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "impurity_functions.png")
    print("Done: impurity_functions.png")


def main() -> None:
    fig_guess_number_tree()
    fig_akinator_tree()
    fig_binary_classification_rectangles()
    fig_decision_boundary()
    fig_feature_importance()
    fig_overfitting_curve()
    fig_impurity_functions()
    print("All derevo_resheniy visuals generated.")


if __name__ == "__main__":
    main()
