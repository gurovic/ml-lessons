"""Генерация всех иллюстраций vizualizatsiya."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.datasets import make_classification
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import auc, precision_recall_curve, roc_curve
from sklearn.model_selection import learning_curve
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "agents"))
from viz_style import (  # noqa: E402
    TEXT_DARK,
    apply_matplotlib_slide_style,
    heatmap_text_color,
    save_slide_figure,
    style_axes,
)

ASSETS = Path(__file__).resolve().parent
RNG = np.random.default_rng(42)


def fig_anscombe_quartet():
    apply_matplotlib_slide_style(compact=True)
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    datasets = [
        ([10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5], [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]),
        ([10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5], [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]),
        ([10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5], [7.46, 6.77, 12.74, 7.11, 7.26, 7.81, 6.08, 5.39, 8.15, 6.42, 5.73]),
        ([8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8], [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]),
    ]
    for ax, (x, y) in zip(axes.ravel(), datasets):
        style_axes(ax)
        ax.scatter(x, y, c="#1f77b4", s=40)
        ax.set_title(f"mean≈9, std≈3.3")
    fig.suptitle("Anscombe: одинаковая статистика — разная форма", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "anscombe_quartet.png")


def fig_fig_axes_diagram():
    apply_matplotlib_slide_style()
    fig = plt.figure(figsize=(5, 3.8), facecolor="white")
    ax = fig.add_axes([0.15, 0.15, 0.75, 0.65])
    style_axes(ax)
    x = np.linspace(0, 2 * np.pi, 50)
    ax.plot(x, np.sin(x), color="#1f77b4")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("axes — область графика")
    fig.text(0.5, 0.92, "figure — весь холст", ha="center", fontsize=14, color=TEXT_DARK)
    rect = plt.Rectangle((0.02, 0.02), 0.96, 0.96, fill=False, edgecolor="#888888", lw=2, transform=fig.transFigure)
    fig.patches.append(rect)
    save_slide_figure(fig, ASSETS / "fig_axes_diagram.png")


def fig_line_learning_curve():
    apply_matplotlib_slide_style()
    X, y = make_classification(n_samples=400, n_features=10, random_state=42)
    sizes, train_s, test_s = learning_curve(
        LogisticRegression(max_iter=500, random_state=42), X, y, cv=3, train_sizes=np.linspace(0.2, 1.0, 6), random_state=42
    )
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.plot(sizes, train_s.mean(axis=1), "o-", label="train", color="#1f77b4")
    ax.plot(sizes, test_s.mean(axis=1), "s-", label="test", color="#d62728")
    ax.set_xlabel("число примеров")
    ax.set_ylabel("accuracy")
    ax.set_title("Разрыв train/test — переобучение")
    ax.legend()
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "line_learning_curve.png")


def fig_scatter_classes():
    apply_matplotlib_slide_style()
    X, y = make_classification(n_samples=120, n_features=2, n_redundant=0, n_clusters_per_class=1, class_sep=1.2, random_state=42)
    fig, ax = plt.subplots(figsize=(5, 3.8))
    style_axes(ax)
    ax.scatter(X[y == 0, 0], X[y == 0, 1], c="#1f77b4", alpha=0.7, s=35, label="класс 0")
    ax.scatter(X[y == 1, 0], X[y == 1, 1], c="#ff7f0e", alpha=0.7, s=35, label="класс 1")
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.legend()
    ax.set_title("Scatter: два кластера")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "scatter_classes.png")


def fig_bar_metrics_compare():
    apply_matplotlib_slide_style()
    models = ["OLS", "Ridge"]
    mae = [52000, 48500]
    rmse = [78000, 71000]
    x = np.arange(len(models))
    w = 0.35
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.bar(x - w / 2, mae, w, label="MAE", color="#1f77b4")
    ax.bar(x + w / 2, rmse, w, label="RMSE", color="#ff7f0e")
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_ylabel("ошибка ($)")
    ax.set_ylim(0, max(rmse) * 1.1)
    ax.legend()
    ax.set_title("Grouped bar: RMSE > MAE")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "bar_metrics_compare.png")


def fig_hist_box_combo():
    apply_matplotlib_slide_style(compact=True)
    from sklearn.datasets import fetch_openml

    raw = fetch_openml("titanic", version=1, as_frame=True, parser="auto")
    df = raw.frame.copy()
    df["Fare"] = pd.to_numeric(df["fare"], errors="coerce")
    df["Pclass"] = df["pclass"].astype(int)
    resid = RNG.normal(0, 1, 200)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    style_axes(axes[0])
    axes[0].hist(resid, bins=25, color="#1f77b4", edgecolor="white")
    axes[0].axvline(0, color="#d62728", ls="--")
    axes[0].set_xlabel("остаток")
    axes[0].set_title("Histogram остатков")
    style_axes(axes[1])
    data = [df.loc[df["Pclass"] == k, "Fare"].dropna() for k in [1, 2, 3]]
    axes[1].boxplot(data, tick_labels=["1", "2", "3"])
    axes[1].set_xlabel("Pclass")
    axes[1].set_ylabel("Fare")
    axes[1].set_title("Boxplot по классу")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "hist_box_combo.png")


def fig_seaborn_scatter_reg():
    apply_matplotlib_slide_style()
    x = np.linspace(0, 10, 60)
    y = 2 * x + 3 + RNG.normal(0, 2, 60)
    df = pd.DataFrame({"x": x, "y": y})
    fig, ax = plt.subplots(figsize=(5, 3.8))
    style_axes(ax)
    sns.regplot(data=df, x="x", y="y", scatter_kws={"alpha": 0.6, "s": 25}, line_kws={"color": "#d62728"}, ax=ax)
    ax.set_title("sns.regplot: тренд + scatter")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "seaborn_scatter_reg.png")


def fig_legend_color_marker():
    apply_matplotlib_slide_style()
    x = np.linspace(0, 5, 30)
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.plot(x, np.sin(x), "o-", color="#1f77b4", label="sin (круг)")
    ax.plot(x, np.cos(x), "s--", color="#ff7f0e", label="cos (квадрат)")
    ax.legend()
    ax.set_title("Цвет + маркер + linestyle")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "legend_color_marker.png")


def fig_subplots_grid_2x2():
    apply_matplotlib_slide_style(compact=True)
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    style_axes(axes[0, 0])
    axes[0, 0].hist(RNG.normal(0, 1, 200), bins=20, color="#1f77b4", edgecolor="white")
    axes[0, 0].set_title("hist")
    style_axes(axes[0, 1])
    axes[0, 1].scatter(RNG.normal(0, 1, 80), RNG.normal(0, 1, 80), alpha=0.5, s=20)
    axes[0, 1].set_title("scatter")
    style_axes(axes[1, 0])
    axes[1, 0].bar(["A", "B", "C"], [3, 7, 5], color="#ff7f0e")
    axes[1, 0].set_title("bar")
    style_axes(axes[1, 1])
    axes[1, 1].boxplot([RNG.normal(i, 1, 50) for i in range(3)])
    axes[1, 1].set_title("box")
    fig.suptitle("EDA 2×2 на одном экране", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "subplots_grid_2x2.png")


def fig_correlation_heatmap():
    apply_matplotlib_slide_style()
    from sklearn.datasets import fetch_california_housing

    data = fetch_california_housing(as_frame=True).frame
    corr = data.iloc[:, :6].corr()
    fig, ax = plt.subplots(figsize=(5, 4.2))
    style_axes(ax)
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)))
    ax.set_yticks(range(len(corr)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.columns)
    for i in range(len(corr)):
        for j in range(len(corr)):
            v = corr.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=9, color=heatmap_text_color(abs(v), 0, 1))
    ax.set_title("Heatmap корреляций")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "correlation_heatmap.png")


def fig_categorical_plots():
    apply_matplotlib_slide_style(compact=True)
    from sklearn.datasets import fetch_openml

    raw = fetch_openml("titanic", version=1, as_frame=True, parser="auto")
    df = raw.frame.copy()
    df["Sex"] = df["sex"]
    df["Pclass"] = df["pclass"].astype(int)
    df["Fare"] = pd.to_numeric(df["fare"], errors="coerce")
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    sns.countplot(data=df, x="Sex", hue="Sex", ax=axes[0], palette="Set2", legend=False)
    style_axes(axes[0])
    axes[0].set_title("countplot Sex")
    sns.barplot(data=df, x="Pclass", y="Fare", hue="Pclass", estimator="mean", ax=axes[1], palette="Blues", legend=False)
    style_axes(axes[1])
    axes[1].set_title("mean Fare by Pclass")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "categorical_plots.png")


def fig_pie_vs_bar():
    apply_matplotlib_slide_style(compact=True)
    labels = ["A", "B", "C", "D", "E"]
    sizes = [35, 25, 20, 12, 8]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    style_axes(axes[0])
    axes[0].pie(sizes, labels=labels, autopct="%1.0f%%")
    axes[0].set_title("pie — углы трудно сравнить")
    style_axes(axes[1])
    axes[1].bar(labels, sizes, color="#1f77b4")
    axes[1].set_ylim(0, max(sizes) * 1.15)
    axes[1].set_title("bar — доли читаются")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "pie_vs_bar.png")


def fig_style_clean_vs_clutter():
    apply_matplotlib_slide_style(compact=True)
    x = np.linspace(0, 5, 40)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    axes[0].set_facecolor("#eeeeee")
    axes[0].plot(x, np.sin(x), lw=4, color="magenta")
    axes[0].grid(True, color="cyan")
    axes[0].set_title("шум: 3D-стиль, лишняя сетка", color=TEXT_DARK)
    style_axes(axes[1])
    axes[1].plot(x, np.sin(x), color="#1f77b4", lw=2)
    axes[1].set_title("чисто: whitegrid, одна мысль")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "style_clean_vs_clutter.png")


def fig_residuals_good_vs_funnel():
    apply_matplotlib_slide_style(compact=True)
    n = 150
    x = RNG.uniform(0, 10, n)
    y_good = 2 * x + RNG.normal(0, 1.5, n)
    y_hat_g = 2 * x
    res_g = y_good - y_hat_g
    y_funnel = x + RNG.normal(0, 1, n) * (0.3 + 0.25 * x)
    y_hat_f = x
    res_f = y_funnel - y_hat_f
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, yhat, res, title in [
        (axes[0], y_hat_g, res_g, "равномерное облако"),
        (axes[1], y_hat_f, res_f, "воронка (heteroscedastic)"),
    ]:
        style_axes(ax)
        ax.scatter(yhat, res, alpha=0.5, s=20, color="#1f77b4")
        ax.axhline(0, color="#d62728", ls="--")
        ax.set_xlabel("ŷ")
        ax.set_ylabel("остаток")
        ax.set_title(title)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "residuals_good_vs_funnel.png")


def fig_roc_pr_curves():
    apply_matplotlib_slide_style(compact=True)
    X, y = make_classification(
        n_samples=300, n_features=2, n_informative=2, n_redundant=0, weights=[0.7, 0.3], random_state=42
    )
    X_tr, X_te, y_tr, y_te = X[:200], X[200:], y[:200], y[200:]
    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500, random_state=42))
    clf.fit(X_tr, y_tr)
    proba = clf.predict_proba(X_te)[:, 1]
    fpr, tpr, _ = roc_curve(y_te, proba)
    prec, rec, _ = precision_recall_curve(y_te, proba)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    style_axes(axes[0])
    axes[0].plot(fpr, tpr, color="#1f77b4", lw=2, label=f"AUC={auc(fpr, tpr):.2f}")
    axes[0].plot([0, 1], [0, 1], "k--", alpha=0.5)
    axes[0].set_xlabel("FPR")
    axes[0].set_ylabel("TPR")
    axes[0].legend()
    axes[0].set_title("ROC")
    style_axes(axes[1])
    axes[1].plot(rec, prec, color="#d62728", lw=2)
    axes[1].set_xlabel("recall")
    axes[1].set_ylabel("precision")
    axes[1].set_title("PR (дисбаланс)")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "roc_pr_curves.png")


def fig_truncated_axis_trap():
    apply_matplotlib_slide_style(compact=True)
    cats = ["M1", "M2"]
    vals = [0.92, 0.96]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, ylim, title in [(axes[0], (0, 1), "ylim с 0"), (axes[1], (0.9, 1.0), "ylim 0.9–1.0")]:
        style_axes(ax)
        ax.bar(cats, vals, color="#1f77b4")
        ax.set_ylim(*ylim)
        ax.set_ylabel("accuracy")
        ax.set_title(title)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "truncated_axis_trap.png")


def fig_ml_lessons_viz_collage():
    apply_matplotlib_slide_style(compact=True)
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    # scatter + line
    x = np.linspace(0, 5, 30)
    y = 1.5 * x + 2 + RNG.normal(0, 0.5, 30)
    style_axes(axes[0, 0])
    axes[0, 0].scatter(x, y, s=20, alpha=0.7)
    z = np.polyfit(x, y, 1)
    axes[0, 0].plot(x, np.poly1d(z)(x), "r-", lw=2)
    axes[0, 0].set_title("линейная регрессия")
    # mini ROC
    style_axes(axes[0, 1])
    fpr = np.linspace(0, 1, 50)
    tpr = np.sqrt(fpr)
    axes[0, 1].plot(fpr, tpr, color="#1f77b4")
    axes[0, 1].plot([0, 1], [0, 1], "k--", alpha=0.4)
    axes[0, 1].set_title("ROC")
    # decision regions stub
    style_axes(axes[1, 0])
    xx, yy = np.meshgrid(np.linspace(-2, 2, 40), np.linspace(-2, 2, 40))
    Z = (xx > 0) ^ (yy > 0)
    axes[1, 0].contourf(xx, yy, Z.astype(float), alpha=0.4, cmap="RdBu")
    axes[1, 0].set_title("граница (XOR)")
    # importance bar
    style_axes(axes[1, 1])
    feats = ["f1", "f2", "f3", "f4"]
    imp = [0.4, 0.25, 0.2, 0.15]
    axes[1, 1].barh(feats, imp, color="#2ca02c")
    axes[1, 1].set_title("feature importance")
    fig.suptitle("Паттерны визуализации ML-уроков", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "ml_lessons_viz_collage.png")


def main():
    fig_anscombe_quartet()
    fig_fig_axes_diagram()
    fig_line_learning_curve()
    fig_scatter_classes()
    fig_bar_metrics_compare()
    fig_hist_box_combo()
    fig_seaborn_scatter_reg()
    fig_legend_color_marker()
    fig_subplots_grid_2x2()
    fig_correlation_heatmap()
    fig_categorical_plots()
    fig_pie_vs_bar()
    fig_style_clean_vs_clutter()
    fig_residuals_good_vs_funnel()
    fig_roc_pr_curves()
    fig_truncated_axis_trap()
    fig_ml_lessons_viz_collage()
    print("vizualizatsiya visuals OK")


if __name__ == "__main__":
    main()
