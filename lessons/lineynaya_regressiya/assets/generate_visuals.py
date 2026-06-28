"""Генерация всех иллюстраций lineynaya_regressiya.

Данные подобраны педагогически: эффект на графике должен быть виден сразу
(см. docs/visuals.md «Педагогический подбор данных»).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch
from PIL import Image
from sklearn.datasets import make_regression
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

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


def fig_mse_vs_mae():
    apply_matplotlib_slide_style()
    e = np.linspace(-3, 3, 300)
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.plot(e, e**2, label="MSE: $e^2$", color="#1f77b4", lw=2)
    ax.plot(e, np.abs(e), label="MAE: $|e|$", color="#ff7f0e", lw=2)
    ax.axvline(0, color="#444444", lw=0.5)
    ax.axhline(0, color="#444444", lw=0.5)
    ax.set_xlabel("ошибка $e = y - \\hat{y}$")
    ax.set_ylabel("вклад в потери")
    ax.set_title("MSE гладкая; MAE — «угол» в нуле")
    ax.legend()
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "mse_vs_mae_loss.png")


def fig_gradient_descent():
    apply_matplotlib_slide_style()
    w0 = np.linspace(-1, 3, 120)
    w1 = np.linspace(-1, 3, 120)
    W0, W1 = np.meshgrid(w0, w1)
    Z = (W0 - 1.2) ** 2 + 2 * (W1 - 0.8) ** 2
    path = np.array([[2.5, 2.5], [2.0, 1.9], [1.6, 1.5], [1.35, 1.1], [1.2, 0.8]])

    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.contour(W0, W1, Z, levels=12, colors="#aaaaaa", linewidths=0.8)
    ax.plot(path[:, 0], path[:, 1], "o-", color="#d62728", lw=2, markersize=6, label="градиентный спуск")
    ax.scatter([1.2], [0.8], c="#2ca02c", s=70, zorder=5, label="минимум MSE")
    ax.set_xlabel("$w_0$")
    ax.set_ylabel("$w_1$")
    ax.set_title("Итеративный поиск минимума")
    ax.legend()
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "gradient_descent_contour.png")


def fig_hyperplane():
    apply_matplotlib_slide_style()
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    x1 = RNG.uniform(0, 5, 40)
    x2 = RNG.uniform(0, 5, 40)
    y = 2 * x1 + 0.5 * x2 + 1 + RNG.normal(0, 0.4, 40)
    g1, g2 = np.meshgrid(np.linspace(0, 5, 10), np.linspace(0, 5, 10))
    gy = 2.0 * g1 + 0.5 * g2 + 1.0

    fig = plt.figure(figsize=(5, 3.8), facecolor="white")
    ax = fig.add_subplot(111, projection="3d", facecolor="white")
    ax.scatter(x1, x2, y, c="#1f77b4", s=22, alpha=0.9)
    ax.plot_surface(g1, g2, gy, alpha=0.35, color="#ff7f0e", edgecolor="none")
    ax.set_xlabel("$x_1$", color=TEXT_DARK)
    ax.set_ylabel("$x_2$", color=TEXT_DARK)
    ax.set_zlabel("$y$", color=TEXT_DARK)
    ax.set_title("$\\hat{y}=w_1 x_1 + w_2 x_2 + b$", color=TEXT_DARK)
    ax.tick_params(colors=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "hyperplane_3d.png")


def fig_scaling():
    apply_matplotlib_slide_style(compact=True)
    area = RNG.uniform(30, 120, 80)
    floor = RNG.integers(1, 25, 80)
    price = 0.8 * area + 15 * floor + RNG.normal(0, 50, 80)
    X = np.column_stack([area, floor])
    lr_raw = LinearRegression().fit(X, price)
    lr_scaled = LinearRegression().fit(StandardScaler().fit_transform(X), price)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, coefs, title in [
        (axes[0], lr_raw.coef_, "без масштабирования"),
        (axes[1], lr_scaled.coef_, "после StandardScaler"),
    ]:
        style_axes(ax)
        ax.bar(["площадь", "этаж"], coefs, color=["#1f77b4", "#ff7f0e"])
        ax.axhline(0, color="#444444", lw=0.6)
        ax.set_ylabel("вес")
        ax.set_title(title)
    fig.suptitle("Масштаб влияет на сравнимость весов", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "scaling_weights_compare.png")


def fig_multicollinearity():
    apply_matplotlib_slide_style(compact=True)
    n = 100
    x1 = RNG.normal(0, 1, n)
    x2 = x1 + RNG.normal(0, 0.05, n)
    y = 3 * x1 + RNG.normal(0, 0.5, n)
    X = np.column_stack([x1, x2])
    coefs = []
    for _ in range(30):
        idx = RNG.choice(n, n, replace=True)
        coefs.append(LinearRegression().fit(X[idx], y[idx]).coef_)
    coefs = np.array(coefs)
    corr = np.corrcoef(x1, x2)[0, 1]

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    im = axes[0].imshow([[1, corr], [corr, 1]], cmap="Blues", vmin=0, vmax=1)
    style_axes(axes[0])
    axes[0].set_xticks([0, 1], labels=["$x_1$", "$x_2$"])
    axes[0].set_yticks([0, 1], labels=["$x_1$", "$x_2$"])
    axes[0].set_title("корреляция ≈ 1")
    for (i, j), val in [((0, 1), corr), ((1, 0), corr), ((0, 0), 1.0), ((1, 1), 1.0)]:
        axes[0].text(j, i, f"{val:.2f}", ha="center", va="center", color=heatmap_text_color(val))
    fig.colorbar(im, ax=axes[0], fraction=0.046)

    style_axes(axes[1])
    bp = axes[1].boxplot([coefs[:, 0], coefs[:, 1]], tick_labels=["$w_1$", "$w_2$"], patch_artist=True)
    for patch, c in zip(bp["boxes"], ["#1f77b4", "#ff7f0e"]):
        patch.set_facecolor(c)
    axes[1].axhline(0, color="#444444", lw=0.6)
    axes[1].set_ylabel("вес (bootstrap)")
    axes[1].set_title("веса нестабильны")
    fig.suptitle("Мультиколлинеарность", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "multicollinearity.png")


def fig_train_test():
    apply_matplotlib_slide_style(compact=True)
    # train: почти идеальная линия; test: участок с систематическим промахом → R²_train >> R²_test
    x_train = np.linspace(0, 10, 55)
    y_train = 2 * x_train + 3 + RNG.normal(0, 0.4, 55)
    x_test = np.linspace(0, 10, 25)
    y_test = 2 * x_test + 3 + RNG.normal(0, 0.4, 25)
    y_test[12:] += np.linspace(0, 9, len(y_test[12:]))  # модель «не видела» рост шума

    m = LinearRegression().fit(x_train.reshape(-1, 1), y_train)

    def r2(yt, yp):
        return 1 - np.sum((yt - yp) ** 2) / np.sum((yt - np.mean(yt)) ** 2)

    r2_tr = r2(y_train, m.predict(x_train.reshape(-1, 1)))
    r2_te = r2(y_test, m.predict(x_test.reshape(-1, 1)))

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, xs, ys, title in [(axes[0], x_train, y_train, "train"), (axes[1], x_test, y_test, "test")]:
        style_axes(ax)
        ax.scatter(xs, ys, c="#1f77b4", s=28)
        lx = np.array([xs.min(), xs.max()])
        ax.plot(lx, m.predict(lx.reshape(-1, 1)), "r-", lw=2)
        ax.set_title(title)
        ax.set_xlabel("$x$")
        ax.set_ylabel("$y$")
    fig.suptitle(f"$R^2$: train={r2_tr:.2f}, test={r2_te:.2f}", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "train_test_split.png")


def fig_metrics():
    apply_matplotlib_slide_style()
    # один крупный промах → RMSE заметно выше MAE
    y_true = np.array([10.0, 12.0, 8.0, 15.0, 11.0])
    y_pred = np.array([10.0, 12.0, 8.0, 7.0, 11.0])
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    r2 = 1 - np.sum((y_true - y_pred) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2)

    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    bars = ax.bar(["MAE", "RMSE", "$R^2$"], [mae, rmse, r2], color=["#1f77b4", "#ff7f0e", "#2ca02c"])
    ax.set_ylabel("значение")
    ax.set_title("Метрики на одной выборке")
    for bar, v in zip(bars, [mae, rmse, r2]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, f"{v:.2f}", ha="center", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "regression_metrics_bar.png")


def fig_weights_interpretation():
    apply_matplotlib_slide_style()
    features = ["площадь", "этаж", "район_A", "район_B"]
    weights = [0.85, 0.42, -0.15, 0.10]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.barh(features, weights, color=["#2ca02c" if w >= 0 else "#d62728" for w in weights])
    ax.axvline(0, color="#444444", lw=0.8)
    ax.set_xlabel("вес (после StandardScaler)")
    ax.set_title("Сравнимое влияние признаков")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "standardized_weights.png")


def fig_pipeline():
    apply_matplotlib_slide_style(compact=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2), facecolor="white")
    for ax, title, steps, bad in [
        (axes[0], "утечка (плохо)", ["scale\n(все данные)", "split", "fit"], True),
        (axes[1], "Pipeline (хорошо)", ["split", "Pipeline:\nscale+fit", "predict test"], False),
    ]:
        ax.set_facecolor("white")
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 3)
        ax.axis("off")
        ax.set_title(title, color="#d62728" if bad else "#2ca02c")
        xs = [1.5, 5, 8.5]
        for i, (x, label) in enumerate(zip(xs, steps)):
            ax.add_patch(FancyBboxPatch((x - 1.1, 1.0), 2.2, 1.0, boxstyle="round,pad=0.05", fc=BG_BOX, ec="#333333"))
            ax.text(x, 1.5, label, ha="center", va="center", color=TEXT_DARK)
            if i < len(steps) - 1:
                ax.add_patch(FancyArrowPatch((x + 1.1, 1.5), (xs[i + 1] - 1.1, 1.5), arrowstyle="->", mutation_scale=12, color="#444444"))
    fig.suptitle("Data leakage vs Pipeline", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "pipeline_leakage.png")


def fig_leverage_x():
    apply_matplotlib_slide_style(compact=True)
    x = np.concatenate([np.linspace(1, 9, 24), [15.0]])
    y = 1.8 * x + 2 + RNG.normal(0, 0.8, 25)
    y[-1] = 1.8 * x[-1] + 2 + 0.3  # нормальный y, но x далеко → сильный leverage
    m_clean = LinearRegression().fit(x[:-1].reshape(-1, 1), y[:-1])
    m_all = LinearRegression().fit(x.reshape(-1, 1), y)
    xx = np.linspace(0, 15, 100).reshape(-1, 1)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, model, title, highlight in [
        (axes[0], m_clean, "без leverage-точки", False),
        (axes[1], m_all, "leverage по $x$", True),
    ]:
        style_axes(ax)
        ax.scatter(x, y, c="#1f77b4", s=40)
        if highlight:
            ax.scatter([x[-1]], [y[-1]], c="#ff7f0e", s=140, zorder=5, label="далеко по $x$")
            ax.legend()
        ax.plot(xx, model.predict(xx), "r-", lw=2)
        ax.set_xlim(0, 15)
        ax.set_title(title)
        ax.set_xlabel("$x$")
        ax.set_ylabel("$y$")
    fig.suptitle("Выброс в $x$ меняет наклон", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "outlier_leverage_x.png")


def fig_residuals_hist():
    apply_matplotlib_slide_style()
    x = RNG.uniform(0, 10, 50)
    y = 1.5 * x + 2 + RNG.normal(0, 1.5, 50)
    resid = y - LinearRegression().fit(x.reshape(-1, 1), y).predict(x.reshape(-1, 1))

    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.hist(resid, bins=12, color="#1f77b4", edgecolor="white")
    ax.axvline(0, color="#d62728", lw=1.5, label="среднее ≈ 0")
    ax.set_xlabel("остаток $\\varepsilon$")
    ax.set_ylabel("частота")
    ax.set_title("Остатки вокруг нуля")
    ax.legend()
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "residuals_histogram.png")


def fig_regularization():
    apply_matplotlib_slide_style(compact=True)
    X, y = make_regression(n_samples=120, n_features=6, n_informative=3, noise=8.0, random_state=42)
    X[:, 2] = X[:, 1] + RNG.normal(0, 0.04, 120)
    X[:, 4] = X[:, 3] + RNG.normal(0, 0.04, 120)
    models = {
        "OLS": make_pipeline(StandardScaler(), LinearRegression()),
        "Ridge": make_pipeline(StandardScaler(), Ridge(alpha=2.0)),
        "Lasso": make_pipeline(StandardScaler(), Lasso(alpha=0.35, max_iter=20000)),
    }
    coefs = {}
    for name, pipe in models.items():
        pipe.fit(X, y)
        coefs[name] = list(pipe.named_steps.values())[-1].coef_

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    ax = axes[0]
    style_axes(ax)
    t = np.linspace(0, 2 * np.pi, 300)
    ax.plot(np.cos(t), np.sin(t), color="#1f77b4", lw=2.2, label="L2 (Ridge)")
    d = np.array([[1, 0], [0, 1], [-1, 0], [0, -1], [1, 0]])
    ax.plot(d[:, 0], d[:, 1], color="#ff7f0e", lw=2.2, label="L1 (Lasso)")
    for w, h, a in [(2.6, 1.0, 0.2), (1.9, 0.75, 0.35), (1.2, 0.5, 0.55)]:
        ax.add_patch(Ellipse((0.75, 0.35), width=w, height=h, angle=35, fill=False, edgecolor="#666666", linestyle="--", lw=1, alpha=a))
    ax.scatter([0.75], [0.35], c="#d62728", s=45, zorder=5)
    ax.scatter([0.62], [0.18], c="#1f77b4", s=110, marker="*", zorder=6, label="Ridge")
    ax.scatter([1.0], [0.0], c="#ff7f0e", s=110, marker="*", zorder=6, label="Lasso → $w_2=0$")
    ax.axhline(0, color="#444444", lw=0.4)
    ax.axvline(0, color="#444444", lw=0.4)
    ax.set_aspect("equal")
    ax.set_xlabel("$w_1$")
    ax.set_ylabel("$w_2$")
    ax.set_title("Штраф сжимает веса")
    ax.legend(fontsize=11)

    ax = axes[1]
    style_axes(ax)
    n_feat = len(coefs["OLS"])
    x = np.arange(n_feat)
    width = 0.25
    for i, (name, color) in enumerate(zip(models, ["#1f77b4", "#ff7f0e", "#2ca02c"])):
        vals = coefs[name]
        bars = ax.bar(x + (i - 1) * width, vals, width, label=name, color=color, edgecolor="white")
        for bar, val in zip(bars, vals):
            if name == "Lasso" and abs(val) < 0.05:
                ax.annotate("0", xy=(bar.get_x() + bar.get_width() / 2, 0), xytext=(0, 10), textcoords="offset points", ha="center", color="#2ca02c", fontweight="bold")
    ax.axhline(0, color="#444444", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"$w_{j+1}$" for j in range(n_feat)])
    ax.set_ylabel("вес")
    ax.set_title("OLS vs Ridge vs Lasso")
    ax.legend()
    fig.suptitle("Ridge сжимает, Lasso обнуляет", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "regularization_weights.png")


def fig_intro_scatter():
    apply_matplotlib_slide_style()
    x = RNG.uniform(0, 10, 40)
    y = 2.5 * x + 3 + RNG.normal(0, 3, 40)
    m = LinearRegression().fit(x.reshape(-1, 1), y)
    xx = np.linspace(0, 10, 100)

    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.scatter(x, y, c="#1f77b4", s=35)
    ax.plot(xx, m.predict(xx.reshape(-1, 1)), "r-", lw=2, label="$\\hat{y}=kx+b$")
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_title("Линейная регрессия")
    ax.legend()
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "intro_scatter_line.png")


def fig_residuals_vertical():
    apply_matplotlib_slide_style()
    x = RNG.uniform(1, 9, 20)
    y = 2 * x + 1 + RNG.normal(0, 1, 20)
    m = LinearRegression().fit(x.reshape(-1, 1), y)
    y_hat = m.predict(x.reshape(-1, 1))

    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.scatter(x, y, c="#1f77b4", s=40)
    xx = np.linspace(0, 10, 100)
    ax.plot(xx, m.predict(xx.reshape(-1, 1)), "r-", lw=2)
    for i in range(0, len(x), 3):
        ax.vlines(x[i], y_hat[i], y[i], colors="#888888", linestyles="dashed", lw=1.5)
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_title("Вертикальные остатки")
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "residuals_vertical.png")


def fig_outlier_y():
    apply_matplotlib_slide_style(compact=True)
    x = np.linspace(1, 10, 22)
    y = 2 * x + 1 + RNG.normal(0, 0.6, 22)
    x_all = np.append(x, 11.0)
    y_all = np.append(y, 32.0)  # сильный выброс в y
    m0 = LinearRegression().fit(x.reshape(-1, 1), y)
    m1 = LinearRegression().fit(x_all.reshape(-1, 1), y_all)
    xx = np.linspace(0, 12, 100).reshape(-1, 1)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, xs, ys, model, title in [
        (axes[0], x, y, m0, "без выброса"),
        (axes[1], x_all, y_all, m1, "с выбросом в $y$"),
    ]:
        style_axes(ax)
        ax.scatter(xs, ys, c="#1f77b4", s=35)
        if title.startswith("с"):
            ax.scatter([11], [32], c="#ff7f0e", s=120, zorder=5)
        ax.plot(xx, model.predict(xx), "r-", lw=2)
        ax.set_title(title)
        ax.set_xlabel("$x$")
        ax.set_ylabel("$y$")
    fig.suptitle("MSE чувствительна к выбросу в $y$", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "outlier_y_effect.png")


def fig_residual_diagnostics():
    apply_matplotlib_slide_style(compact=True)
    n = 80
    # плохо: гетероскедастичность — «воронка»
    x_bad = np.linspace(0.5, 10, n)
    y_bad = x_bad + RNG.normal(0, 1, n) * (0.3 + 0.25 * x_bad)
    pred_bad = LinearRegression().fit(x_bad.reshape(-1, 1), y_bad).predict(x_bad.reshape(-1, 1))
    resid_bad = y_bad - pred_bad

    # хорошо: гомоскедастичные остатки
    x_good = np.linspace(0, 10, n)
    y_good = 2 * x_good + 1 + RNG.normal(0, 1.2, n)
    pred_good = LinearRegression().fit(x_good.reshape(-1, 1), y_good).predict(x_good.reshape(-1, 1))
    resid_good = y_good - pred_good

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    style_axes(axes[0])
    axes[0].scatter(pred_bad, resid_bad, c="#1f77b4", s=28, alpha=0.75)
    axes[0].axhline(0, color="#444444", lw=0.8)
    axes[0].set_xlabel("$\\hat{y}$")
    axes[0].set_ylabel("остаток")
    axes[0].set_title("«воронка» — плохо")

    style_axes(axes[1])
    axes[1].scatter(pred_good, resid_good, c="#1f77b4", s=28, alpha=0.75)
    axes[1].axhline(0, color="#444444", lw=0.8)
    axes[1].set_xlabel("$\\hat{y}$")
    axes[1].set_ylabel("остаток")
    axes[1].set_title("облако — хорошо")
    fig.suptitle("Диагностика остатков", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "residual_diagnostics.png")


def fig_nonlinear():
    apply_matplotlib_slide_style(compact=True)
    x = np.linspace(-3, 3, 80)
    y = x**2 + RNG.normal(0, 0.8, 80)
    m = LinearRegression().fit(x.reshape(-1, 1), y)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    style_axes(axes[0])
    axes[0].scatter(x, y, c="#1f77b4", s=25)
    axes[0].plot(x, m.predict(x.reshape(-1, 1)), "r-", lw=2)
    axes[0].set_title("линейная модель")
    axes[0].set_xlabel("$x$")
    axes[0].set_ylabel("$y$")

    style_axes(axes[1])
    axes[1].scatter(x, y, c="#1f77b4", s=25)
    axes[1].plot(x, x**2, "g-", lw=2, label="парабола")
    axes[1].set_title("нелинейная зависимость")
    axes[1].set_xlabel("$x$")
    axes[1].legend()
    fig.suptitle("Когда линейная модель не подходит", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "nonlinear_vs_linear.png")


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
    fig_leverage_x()
    fig_residuals_hist()
    fig_regularization()
    fig_intro_scatter()
    fig_residuals_vertical()
    fig_outlier_y()
    fig_residual_diagnostics()
    fig_nonlinear()
    print(f"Generated {len(list(ASSETS.glob('*.png')))} PNG in {ASSETS}")


if __name__ == "__main__":
    main()
