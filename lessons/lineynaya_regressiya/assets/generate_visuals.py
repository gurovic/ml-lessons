"""Генерация всех иллюстраций lineynaya_regressiya.

Данные подобраны педагогически: эффект на графике должен быть виден сразу
(см. docs/visuals.md «Педагогический подбор данных»).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from sklearn.datasets import make_regression
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "agents"))
from viz_style import (  # noqa: E402
    BG_BOX,
    FIGSIZE_DUAL_COL,
    FIGSIZE_SINGLE,
    FIGSIZE_TRIPLE_COL,
    TEXT_DARK,
    FONT_ANNOT,
    FONT_DIAGRAM,
    FONT_LABEL,
    FONT_TITLE,
    apply_matplotlib_slide_style,
    legend_kwargs,
    save_dual_col_figure,
    save_single_panel_figure,
    save_slide_figure,
    style_axes,
    style_panel_title,
)

ASSETS = Path(__file__).resolve().parent
RNG = np.random.default_rng(42)

ORPHAN_PNG = (
    "outlier_y_effect.png",
    "outlier_leverage_x.png",
    "outlier_scatter_boxplot.png",
    "ridge_alpha_cv.png",
)


def _grid(ax, *, alpha: float = 0.35) -> None:
    ax.grid(True, alpha=alpha, linestyle=":", linewidth=0.7)


def fig_mse_vs_mae():
    apply_matplotlib_slide_style()
    e = np.linspace(-3, 3, 300)
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ax.plot(e, e**2, label="MSE: $e^2$", color="#1f77b4", lw=2.4)
    ax.plot(e, np.abs(e), label="MAE: $|e|$", color="#ff7f0e", lw=2.4)
    ax.axvline(0, color="#444444", lw=0.6)
    ax.axhline(0, color="#444444", lw=0.6)
    ax.scatter([2, -2], [4, 4], c="#1f77b4", s=50, zorder=5)
    ax.scatter([2, -2], [2, 2], c="#ff7f0e", s=50, zorder=5)
    ax.text(-2.6, 5.8, "«угол» MAE", fontsize=FONT_ANNOT, color="#ff7f0e", va="top")
    ax.text(2.2, 6.8, "$|e|=2$ → MSE=4", fontsize=FONT_ANNOT, color="#1f77b4", va="top")
    ax.set_xlabel("ошибка $e = y - \\hat{y}$")
    ax.set_ylabel("вклад в потери")
    style_panel_title(ax, "MSE гладкая; MAE — «угол» в нуле")
    _grid(ax)
    save_single_panel_figure(fig, ax, ASSETS / "mse_vs_mae_loss.png", legend_ncol=2)


def fig_gradient_descent():
    apply_matplotlib_slide_style()
    w0 = np.linspace(-1, 3, 120)
    w1 = np.linspace(-1, 3, 120)
    W0, W1 = np.meshgrid(w0, w1)
    Z = (W0 - 1.2) ** 2 + 2 * (W1 - 0.8) ** 2
    path = np.array([[2.5, 2.5], [2.0, 1.9], [1.6, 1.5], [1.35, 1.1], [1.2, 0.8]])

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ax.contour(W0, W1, Z, levels=12, colors="#888888", linewidths=0.9)
    ax.plot(path[:, 0], path[:, 1], "o-", color="#d62728", lw=2.2, markersize=7, label="градиентный спуск")
    for i, (a, b) in enumerate(path[:-1], start=1):
        ax.annotate(str(i), (a, b), textcoords="offset points", xytext=(6, 6), fontsize=FONT_ANNOT, color="#d62728")
    ax.scatter([1.2], [0.8], c="#2ca02c", s=80, zorder=5, label="минимум MSE")
    ax.set_xlabel("$w_0$")
    ax.set_ylabel("$w_1$")
    style_panel_title(ax, "Итеративный поиск минимума")
    save_single_panel_figure(fig, ax, ASSETS / "gradient_descent_contour.png", legend_ncol=2)


def fig_hyperplane():
    """Два признака → одно y (вместо нечитаемого 3D на слайде)."""
    apply_matplotlib_slide_style()
    n = 50
    x1 = RNG.uniform(20, 120, n)
    x2 = RNG.integers(1, 20, n)
    y = 0.6 * x1 + 8 * x2 + 50 + RNG.normal(0, 30, n)
    m1 = LinearRegression().fit(x1.reshape(-1, 1), y)
    m2 = LinearRegression().fit(x2.reshape(-1, 1), y)

    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)
    for ax, xs, m, xlabel, title in [
        (axes[0], x1, m1, "площадь, м²", "$y$ vs площадь"),
        (axes[1], x2, m2, "этаж", "$y$ vs этаж"),
    ]:
        style_axes(ax)
        ax.scatter(xs, y, c="#1f77b4", s=28, alpha=0.85)
        xx = np.linspace(xs.min(), xs.max(), 100)
        ax.plot(xx, m.predict(xx.reshape(-1, 1)), "r-", lw=2.2)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("цена")
        style_panel_title(ax, title)
        _grid(ax)
    fig.suptitle("$\\hat{y} = w_1 x_1 + w_2 x_2 + b$", color=TEXT_DARK, fontsize=FONT_TITLE, y=0.98)
    save_dual_col_figure(fig, axes, ASSETS / "hyperplane_3d.png")


def fig_scaling():
    apply_matplotlib_slide_style()
    area = RNG.uniform(30, 120, 80)
    floor = RNG.integers(1, 25, 80)
    price = 0.8 * area + 15 * floor + RNG.normal(0, 50, 80)
    X = np.column_stack([area, floor])
    lr_raw = LinearRegression().fit(X, price)
    lr_scaled = LinearRegression().fit(StandardScaler().fit_transform(X), price)

    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)
    raw = lr_raw.coef_
    scaled = lr_scaled.coef_
    for ax, coefs, title, note in [
        (axes[0], raw, "без масштабирования", f"этаж {raw[1]:.1f} ≫ площадь {raw[0]:.1f}"),
        (axes[1], scaled, "после StandardScaler", "веса сопоставимы"),
    ]:
        style_axes(ax)
        bars = ax.bar(["площадь", "этаж"], coefs, color=["#1f77b4", "#ff7f0e"])
        ax.axhline(0, color="#444444", lw=0.6)
        ax.set_ylabel("вес")
        style_panel_title(ax, title)
        for bar, v in zip(bars, coefs):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                v + (0.02 if v >= 0 else -0.08) * max(abs(coefs)),
                f"{v:.1f}",
                ha="center",
                va="bottom",
                color=TEXT_DARK,
                fontsize=FONT_ANNOT,
            )
        ax.text(0.98, 0.92, note, transform=ax.transAxes, ha="right", va="top", fontsize=FONT_ANNOT, color=TEXT_DARK)
    save_dual_col_figure(fig, axes, ASSETS / "scaling_weights_compare.png")


def fig_multicollinearity():
    apply_matplotlib_slide_style()
    n = 100
    x1 = RNG.normal(0, 1, n)
    x2 = 3.0 * x1 + RNG.normal(0, 0.06, n)
    y = 2.5 * x1 + RNG.normal(0, 0.4, n)
    X = np.column_stack([x1, x2])
    coefs = []
    for _ in range(40):
        idx = RNG.choice(n, n, replace=True)
        coefs.append(LinearRegression().fit(X[idx], y[idx]).coef_)
    coefs = np.array(coefs)

    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)
    style_axes(axes[0])
    axes[0].scatter(x1, x2, c="#1f77b4", s=28, alpha=0.75)
    axes[0].plot([-3, 3], [-9, 9], "r--", lw=1.5, alpha=0.7)
    axes[0].set_xlabel("$x_1$ (площадь, м²)")
    axes[0].set_ylabel("$x_2$ (площадь, ft²)")
    style_panel_title(axes[0], "признаки почти дубли")
    axes[0].text(0.04, 0.92, "$r \\approx 0.99$", transform=axes[0].transAxes, fontsize=FONT_ANNOT, color=TEXT_DARK)

    style_axes(axes[1])
    bp = axes[1].boxplot([coefs[:, 0], coefs[:, 1]], tick_labels=["$w_1$", "$w_2$"], patch_artist=True)
    for patch, c in zip(bp["boxes"], ["#1f77b4", "#ff7f0e"]):
        patch.set_facecolor(c)
    axes[1].axhline(0, color="#444444", lw=0.8)
    axes[1].set_ylabel("вес (bootstrap)")
    style_panel_title(axes[1], "bootstrap: веса «прыгают», знак меняется")
    for j, col in enumerate(coefs.T):
        axes[1].text(
            j + 1,
            col.max() + 0.25,
            f"σ={col.std():.1f}",
            ha="center",
            color=TEXT_DARK,
            fontsize=FONT_ANNOT,
        )
    save_dual_col_figure(fig, axes, ASSETS / "multicollinearity.png")


def fig_train_test():
    apply_matplotlib_slide_style()
    x_train = np.linspace(0, 8, 48)
    y_train = 2.0 * x_train + 3 + RNG.normal(0, 0.45, 48)
    x_test = np.linspace(0, 10, 26)
    y_test = 2.0 * x_test + 3 + RNG.normal(0, 0.45, 26)
    y_test += 0.22 * (x_test - 4.5) ** 2

    m = LinearRegression().fit(x_train.reshape(-1, 1), y_train)

    def r2(yt, yp):
        return 1 - np.sum((yt - yp) ** 2) / np.sum((yt - np.mean(yt)) ** 2)

    r2_tr = r2(y_train, m.predict(x_train.reshape(-1, 1)))
    r2_te = r2(y_test, m.predict(x_test.reshape(-1, 1)))

    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)
    for ax, xs, ys, title, highlight in [
        (axes[0], x_train, y_train, f"train: $R^2$={r2_tr:.2f}", None),
        (axes[1], x_test, y_test, f"test: $R^2$={r2_te:.2f}", x_test > 6),
    ]:
        style_axes(ax)
        if highlight is not None:
            mask = highlight
            ax.scatter(xs[~mask], ys[~mask], c="#1f77b4", s=28)
            ax.scatter(xs[mask], ys[mask], c="#ff7f0e", s=40, label="хвост: модель не видела")
        else:
            ax.scatter(xs, ys, c="#1f77b4", s=28)
        lx = np.array([0, 10])
        ax.plot(lx, m.predict(lx.reshape(-1, 1)), "r-", lw=2.2, label="модель (train)")
        style_panel_title(ax, title)
        ax.set_xlabel("$x$")
        ax.set_ylabel("$y$")
        _grid(ax)
    save_dual_col_figure(fig, axes, ASSETS / "train_test_split.png")


def fig_metrics():
    apply_matplotlib_slide_style()
    y_true = np.array([10.0, 12.0, 8.0, 15.0, 11.0])
    y_pred = np.array([10.0, 12.0, 8.0, 7.0, 11.0])
    err = y_true - y_pred
    mae = np.mean(np.abs(err))
    rmse = np.sqrt(np.mean(err**2))

    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)
    ax = axes[0]
    style_axes(ax)
    x = np.arange(len(y_true))
    ax.bar(x - 0.15, y_true, 0.3, label="$y$ (факт)", color="#1f77b4")
    ax.bar(x + 0.15, y_pred, 0.3, label="$\\hat{y}$ (прогноз)", color="#ff7f0e")
    ax.set_xticks(x)
    ax.set_xticklabels([f"#{i+1}" for i in x])
    ax.set_ylabel("значение")
    style_panel_title(ax, "промах #4: $|e_4|=8$")

    ax = axes[1]
    style_axes(ax)
    labels = ["MAE", "RMSE"]
    vals = [mae, rmse]
    bars = ax.bar(labels, vals, color=["#1f77b4", "#d62728"])
    ax.set_ylabel("метрика")
    style_panel_title(ax, f"MAE={mae:.1f}  ·  RMSE={rmse:.1f} — RMSE выше")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.08, f"{v:.1f}", ha="center", color=TEXT_DARK, fontsize=FONT_ANNOT)
    save_dual_col_figure(fig, axes, ASSETS / "regression_metrics_bar.png")


def fig_weights_interpretation():
    apply_matplotlib_slide_style()
    features = ["площадь", "этаж", "район_A", "район_B"]
    weights = [0.85, 0.42, -0.15, 0.10]
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    bars = ax.barh(features, weights, color=["#2ca02c" if w >= 0 else "#d62728" for w in weights])
    ax.axvline(0, color="#444444", lw=0.8)
    ax.set_xlabel("вес (после StandardScaler)")
    style_panel_title(ax, "Сравнимое влияние признаков")
    for bar, w in zip(bars, weights):
        ax.text(w + (0.03 if w >= 0 else -0.03), bar.get_y() + bar.get_height() / 2, f"{w:+.2f}", va="center", ha="left" if w >= 0 else "right", fontsize=FONT_ANNOT, color=TEXT_DARK)
    save_single_panel_figure(fig, ax, ASSETS / "standardized_weights.png")


def fig_pipeline():
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)
    for ax, title, steps, bad in [
        (axes[0], "Плохо: масштаб до split", ["Scaler\nвсе данные", "split", "fit"], True),
        (axes[1], "Хорошо: Pipeline", ["split", "Pipeline\nfit train", "predict test"], False),
    ]:
        ax.set_facecolor("white")
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 2.8)
        ax.axis("off")
        style_panel_title(ax, title, color="#d62728" if bad else "#2ca02c", loc="left")
        xs = [1.4, 5.0, 8.6]
        bw, bh = 2.0, 1.25
        for i, (x, label) in enumerate(zip(xs, steps)):
            ax.add_patch(FancyBboxPatch((x - bw / 2, 0.55), bw, bh, boxstyle="round,pad=0.04", fc=BG_BOX, ec="#333333"))
            ax.text(x, 0.55 + bh / 2, label, ha="center", va="center", color=TEXT_DARK, fontsize=FONT_DIAGRAM)
            if i < len(steps) - 1:
                ax.add_patch(
                    FancyArrowPatch(
                        (x + bw / 2, 0.55 + bh / 2),
                        (xs[i + 1] - bw / 2, 0.55 + bh / 2),
                        arrowstyle="->",
                        mutation_scale=10,
                        color="#444444",
                    )
                )
        if bad:
            ax.annotate(
                "утечка: статистики test\nв Scaler",
                xy=(1.4, 0.55),
                xytext=(1.4, 2.35),
                fontsize=FONT_ANNOT,
                color="#d62728",
                ha="center",
                arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.5),
            )
    save_dual_col_figure(fig, axes, ASSETS / "pipeline_leakage.png", hspace=0.72 + 0.18)


def fig_outlier_effects():
    apply_matplotlib_slide_style()
    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)

    x = np.linspace(1, 10, 22)
    y = 2 * x + 1 + RNG.normal(0, 0.6, 22)
    x_all = np.append(x, 5.5)
    y_all = np.append(y, 32.0)
    m0 = LinearRegression().fit(x.reshape(-1, 1), y)
    m1 = LinearRegression().fit(x_all.reshape(-1, 1), y_all)
    xx = np.linspace(0, 11, 100).reshape(-1, 1)

    ax = axes[0]
    style_axes(ax)
    ax.scatter(x, y, c="#1f77b4", s=35)
    ax.scatter([5.5], [32.0], c="#ff7f0e", s=120, zorder=5, label="выброс в $y$")
    ax.plot(xx, m0.predict(xx), color="#2ca02c", lw=2.2, label=f"без: $b$={m0.intercept_:.1f}")
    ax.plot(xx, m1.predict(xx), color="#d62728", lw=2.2, linestyle="--", label=f"с выбросом: $b$={m1.intercept_:.1f}")
    ax.annotate(
        f"$\\Delta b$={m1.intercept_ - m0.intercept_:.1f}",
        xy=(0.3, (m0.intercept_ + m1.intercept_) / 2),
        xytext=(2.5, m0.intercept_ + 5),
        color=TEXT_DARK,
        fontsize=FONT_ANNOT,
        arrowprops=dict(arrowstyle="<->", color="#444444"),
    )
    ax.set_xlim(-0.2, 11)
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    style_panel_title(ax, "Выброс в $y$ → сдвиг intercept")

    x_l = np.concatenate([np.linspace(1, 9, 24), [15.0]])
    y_l = 1.8 * x_l + 2 + RNG.normal(0, 0.8, 25)
    y_l[-1] = 17.0
    m_clean = LinearRegression().fit(x_l[:-1].reshape(-1, 1), y_l[:-1])
    m_all = LinearRegression().fit(x_l.reshape(-1, 1), y_l)
    xx_l = np.linspace(0, 15, 100).reshape(-1, 1)
    k0, k1 = m_clean.coef_[0], m_all.coef_[0]

    ax = axes[1]
    style_axes(ax)
    ax.scatter(x_l[:-1], y_l[:-1], c="#1f77b4", s=35)
    ax.scatter([x_l[-1]], [y_l[-1]], c="#ff7f0e", s=120, zorder=5, label="высокий leverage ($x$)")
    ax.plot(xx_l, m_clean.predict(xx_l), color="#2ca02c", lw=2.2, label=f"без: $k$={k0:.2f}")
    ax.plot(xx_l, m_all.predict(xx_l), color="#d62728", lw=2.2, linestyle="--", label=f"с leverage: $k$={k1:.2f}")
    ax.annotate(
        f"$\\Delta k$={k1 - k0:.2f}",
        xy=(10, m_clean.predict([[10]])[0]),
        xytext=(8, 26),
        fontsize=FONT_ANNOT,
        color=TEXT_DARK,
        arrowprops=dict(arrowstyle="->", color="#d62728"),
    )
    ax.set_xlim(0, 15)
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    style_panel_title(ax, "Leverage по $x$ → меняется наклон")

    save_dual_col_figure(fig, axes, ASSETS / "outlier_effects.png")


def fig_residuals_geometry():
    """Остатки + гистограмма — один PNG для слайда 2."""
    apply_matplotlib_slide_style()
    x = RNG.uniform(1, 9, 20)
    y = 2 * x + 1 + RNG.normal(0, 1, 20)
    m = LinearRegression().fit(x.reshape(-1, 1), y)
    y_hat = m.predict(x.reshape(-1, 1))
    intercept = float(m.intercept_)
    resid = y - y_hat

    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)

    ax = axes[0]
    style_axes(ax)
    ax.scatter(x, y, c="#1f77b4", s=38)
    xx = np.linspace(0, 10, 100)
    ax.plot(xx, m.predict(xx.reshape(-1, 1)), "r-", lw=2.2)
    for xi, yi, yhi in zip(x, y, y_hat):
        ax.vlines(xi, yhi, yi, colors="#555555", linestyles=(0, (4, 3)), lw=2.2)
    ax.scatter([0], [intercept], c="#2ca02c", s=40, zorder=6)
    ax.text(
        0.03,
        0.97,
        f"intercept $b$={intercept:.1f}",
        transform=ax.transAxes,
        fontsize=FONT_ANNOT,
        color="#2ca02c",
        va="top",
        ha="left",
    )
    ax.set_xlabel("признак $x$")
    ax.set_ylabel("$y$")
    style_panel_title(ax, "Вертикальные остатки $\\varepsilon$")
    _grid(ax)

    ax = axes[1]
    style_axes(ax)
    ax.hist(resid, bins=10, color="#1f77b4", edgecolor="white")
    ax.axvline(0, color="#d62728", lw=1.8, label="среднее ≈ 0")
    ax.set_xlabel("остаток $\\varepsilon$")
    ax.set_ylabel("частота")
    style_panel_title(ax, "Симметрично вокруг нуля")

    save_dual_col_figure(fig, axes, ASSETS / "residuals_geometry.png")


def fig_regularization():
    apply_matplotlib_slide_style()
    X, y = make_regression(n_samples=120, n_features=6, n_informative=3, noise=8.0, random_state=42)
    X[:, 2] = X[:, 1] + RNG.normal(0, 0.04, 120)
    Xs = StandardScaler().fit_transform(X)
    models = {
        "OLS": LinearRegression(),
        "Ridge": Ridge(alpha=2.0),
        "Lasso": Lasso(alpha=0.35, max_iter=20000),
    }
    coefs = {}
    for name, est in models.items():
        est.fit(Xs, y)
        coefs[name] = est.coef_

    fig, axes = plt.subplots(2, 1, figsize=FIGSIZE_DUAL_COL)
    ax = axes[0]
    style_axes(ax)
    n_feat = len(coefs["OLS"])
    xpos = np.arange(n_feat)
    width = 0.25
    for i, (name, color) in enumerate(zip(models, ["#1f77b4", "#ff7f0e", "#2ca02c"])):
        vals = coefs[name]
        bars = ax.bar(xpos + (i - 1) * width, vals, width, label=name, color=color, edgecolor="white")
        if name == "Lasso":
            for bar, val in zip(bars, vals):
                if abs(val) < 0.05:
                    ax.annotate(
                        "0",
                        xy=(bar.get_x() + bar.get_width() / 2, 0),
                        xytext=(0, 8),
                        textcoords="offset points",
                        ha="center",
                        color="#2ca02c",
                        fontweight="bold",
                        fontsize=FONT_ANNOT,
                    )
    ax.axhline(0, color="#444444", lw=0.8)
    ax.set_xticks(xpos)
    ax.set_xticklabels([f"$w_{j+1}$" for j in range(n_feat)])
    ax.set_ylabel("вес")
    style_panel_title(ax, "Ridge сжимает, Lasso обнуляет")

    from sklearn.model_selection import cross_val_score

    alphas = np.logspace(-2, 2.5, 45)
    means = np.array(
        [
            -cross_val_score(Ridge(alpha=a), Xs, y, cv=5, scoring="neg_mean_squared_error").mean()
            for a in alphas
        ]
    )
    best_i = int(np.argmin(means))
    best_a, best_mse = float(alphas[best_i]), float(means[best_i])

    ax = axes[1]
    style_axes(ax)
    colors = np.where(np.arange(len(means)) == best_i, "#d62728", "#1f77b4")
    ax.semilogx(alphas, means, "-", color="#1f77b4", lw=2.4, zorder=3)
    ax.scatter(alphas, means, c=colors, s=40, zorder=4, edgecolors="white", linewidths=0.6)
    knee_i = min(len(alphas) - 1, best_i + 12)
    local_max = float(means[: knee_i + 1].max())
    y_span = local_max - best_mse
    ax.set_ylim(best_mse - y_span * 0.08, local_max + y_span * 0.15)
    ax.set_xlim(alphas[max(0, best_i - 8)] * 0.85, alphas[knee_i] * 1.1)
    ax.axvspan(alphas[max(0, best_i - 1)], alphas[min(len(alphas) - 1, best_i + 1)], color="#d62728", alpha=0.12)
    ax.scatter([best_a], [best_mse], s=280, c="#d62728", marker="*", zorder=7, edgecolors="white", linewidths=2)
    ax.axvline(best_a, color="#d62728", ls="-", lw=2.5, alpha=0.85)
    ax.annotate(
        f"$\\alpha^*$={best_a:.2g}",
        xy=(best_a, best_mse),
        xytext=(alphas[knee_i] * 0.92, best_mse + y_span * 0.45),
        fontsize=FONT_ANNOT,
        color=TEXT_DARK,
        ha="right",
        va="bottom",
        arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#d62728", alpha=0.9),
    )
    ax.set_xlabel("$\\alpha$ (Ridge)")
    ax.set_ylabel("CV-MSE")
    style_panel_title(ax, "Подбор $\\alpha$")
    save_dual_col_figure(fig, axes, ASSETS / "regularization_weights.png")


def fig_intro_scatter():
    apply_matplotlib_slide_style()
    area = RNG.uniform(30, 120, 40)
    price = 2.5 * area + 80 + RNG.normal(0, 35, 40)
    m = LinearRegression().fit(area.reshape(-1, 1), price)
    xx = np.linspace(30, 120, 100)

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ax.scatter(area, price, c="#1f77b4", s=35, label="данные")
    ax.plot(xx, m.predict(xx.reshape(-1, 1)), "r-", lw=2.2, label="модель")
    ax.set_xlabel("площадь, м²")
    ax.set_ylabel("цена")
    style_panel_title(ax, "Линейная регрессия")
    _grid(ax)
    save_single_panel_figure(fig, ax, ASSETS / "intro_scatter_line.png", legend_ncol=2)


def fig_residual_diagnostics():
    apply_matplotlib_slide_style()
    n = 80
    x_bad = np.linspace(0.5, 10, n)
    y_bad = x_bad + RNG.normal(0, 1, n) * (0.25 + 0.35 * x_bad)
    pred_bad = LinearRegression().fit(x_bad.reshape(-1, 1), y_bad).predict(x_bad.reshape(-1, 1))
    resid_bad = y_bad - pred_bad

    x_good = np.linspace(0, 10, n)
    y_good = 2 * x_good + 1 + RNG.normal(0, 1.2, n)
    pred_good = LinearRegression().fit(x_good.reshape(-1, 1), y_good).predict(x_good.reshape(-1, 1))
    resid_good = y_good - pred_good

    x_u = np.linspace(-3, 3, n)
    y_u = x_u**2 + RNG.normal(0, 0.6, n)
    pred_u = LinearRegression().fit(x_u.reshape(-1, 1), y_u).predict(x_u.reshape(-1, 1))
    resid_u = y_u - pred_u

    fig, axes = plt.subplots(3, 1, figsize=FIGSIZE_TRIPLE_COL)
    style_axes(axes[0])
    axes[0].scatter(pred_good, resid_good, c="#1f77b4", s=22, alpha=0.75)
    axes[0].axhline(0, color="#444444", lw=0.9)
    axes[0].set_xlabel("$\\hat{y}$")
    axes[0].set_ylabel("остаток")
    style_panel_title(axes[0], "✓ облако вокруг 0")

    style_axes(axes[1])
    axes[1].scatter(pred_bad, resid_bad, c="#1f77b4", s=22, alpha=0.75)
    axes[1].axhline(0, color="#444444", lw=0.9)
    axes[1].set_xlabel("$\\hat{y}$")
    axes[1].set_ylabel("остаток")
    style_panel_title(axes[1], "✗ «воронка» — дисперсия растёт")

    style_axes(axes[2])
    axes[2].scatter(pred_u, resid_u, c="#1f77b4", s=22, alpha=0.75)
    axes[2].axhline(0, color="#444444", lw=0.9)
    axes[2].set_xlabel("$\\hat{y}$")
    axes[2].set_ylabel("остаток")
    style_panel_title(axes[2], "✗ U-форма — нелинейность")
    save_dual_col_figure(fig, axes, ASSETS / "residual_diagnostics.png")


def fig_nonlinear():
    apply_matplotlib_slide_style()
    x = np.linspace(-3, 3, 80)
    y = x**2 + RNG.normal(0, 0.8, 80)
    m = LinearRegression().fit(x.reshape(-1, 1), y)
    y_poly = np.polyval(np.polyfit(x, y, 2), x)
    rmse_lin = np.sqrt(np.mean((y - m.predict(x.reshape(-1, 1))) ** 2))
    rmse_poly = np.sqrt(np.mean((y - y_poly) ** 2))

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    style_axes(ax)
    ax.scatter(x, y, c="#1f77b4", s=30, alpha=0.75, label="данные $y=x^2$")
    ax.plot(x, m.predict(x.reshape(-1, 1)), "r--", lw=2.2, label=f"линейная (RMSE={rmse_lin:.1f})")
    ax.plot(x, y_poly, color="#2ca02c", lw=2.2, label=f"полином 2° (RMSE={rmse_poly:.1f})")
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    style_panel_title(ax, "Нелинейность: прямая не описывает параболу")
    _grid(ax)
    save_single_panel_figure(fig, ax, ASSETS / "nonlinear_vs_linear.png", legend_ncol=2)


def _remove_orphan_png():
    for name in ORPHAN_PNG:
        path = ASSETS / name
        if path.exists():
            path.unlink()


def main():
    fig_mse_vs_mae()
    fig_gradient_descent()
    fig_hyperplane()
    fig_scaling()
    fig_multicollinearity()
    fig_train_test()
    fig_metrics()
    fig_weights_interpretation()
    fig_pipeline()
    fig_outlier_effects()
    fig_residuals_geometry()
    fig_regularization()
    fig_intro_scatter()
    fig_residual_diagnostics()
    fig_nonlinear()
    _remove_orphan_png()
    for old in ("residuals_vertical.png", "residuals_histogram.png"):
        p = ASSETS / old
        if p.exists():
            p.unlink()
    print(f"Generated {len(list(ASSETS.glob('*.png')))} PNG in {ASSETS}")


if __name__ == "__main__":
    main()
