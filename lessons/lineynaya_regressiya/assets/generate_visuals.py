"""Генерация иллюстраций для урока lineynaya_regressiya. Запуск из корня репо."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from PIL import Image
from sklearn.datasets import make_regression
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler

ASSETS = Path(__file__).resolve().parent
RNG = np.random.default_rng(42)


def save_rgb(path: Path) -> None:
    Image.open(path).convert("RGB").save(path)


def fig_mse_vs_mae():
    e = np.linspace(-3, 3, 300)
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.plot(e, e**2, label="MSE: $e^2$", color="#1f77b4", lw=2)
    ax.plot(e, np.abs(e), label="MAE: $|e|$", color="#ff7f0e", lw=2)
    ax.axvline(0, color="k", lw=0.4)
    ax.axhline(0, color="k", lw=0.4)
    ax.set_xlabel("ошибка $e = y - \\hat{y}$")
    ax.set_ylabel("вклад в потери")
    ax.set_title("MSE гладкая; MAE — «угол» в нуле")
    ax.legend()
    plt.tight_layout()
    out = ASSETS / "mse_vs_mae_loss.png"
    plt.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close()
    save_rgb(out)


def fig_gradient_descent():
    w0 = np.linspace(-1, 3, 120)
    w1 = np.linspace(-1, 3, 120)
    W0, W1 = np.meshgrid(w0, w1)
    Z = (W0 - 1.2) ** 2 + 2 * (W1 - 0.8) ** 2
    path = np.array([[2.5, 2.5], [2.0, 1.9], [1.6, 1.5], [1.35, 1.1], [1.2, 0.8]])

    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.contour(W0, W1, Z, levels=12, colors="#aaaaaa", linewidths=0.8)
    ax.plot(path[:, 0], path[:, 1], "o-", color="#d62728", lw=2, markersize=5, label="градиентный спуск")
    ax.scatter([1.2], [0.8], c="#2ca02c", s=60, zorder=5, label="минимум MSE")
    ax.set_xlabel("$w_0$")
    ax.set_ylabel("$w_1$")
    ax.set_title("Итеративный поиск минимума")
    ax.legend(fontsize=8)
    plt.tight_layout()
    out = ASSETS / "gradient_descent_contour.png"
    plt.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close()
    save_rgb(out)


def fig_hyperplane():
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    x1 = RNG.uniform(0, 5, 40)
    x2 = RNG.uniform(0, 5, 40)
    y = 2 * x1 + 0.5 * x2 + 1 + RNG.normal(0, 0.4, 40)
    w1, w2, b = 2.0, 0.5, 1.0
    g1, g2 = np.meshgrid(np.linspace(0, 5, 10), np.linspace(0, 5, 10))
    gy = w1 * g1 + w2 * g2 + b

    fig = plt.figure(figsize=(5, 3.8))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(x1, x2, y, c="#1f77b4", s=18, alpha=0.85)
    ax.plot_surface(g1, g2, gy, alpha=0.35, color="#ff7f0e", edgecolor="none")
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.set_zlabel("$y$")
    ax.set_title("$\\hat{y}=w_1 x_1 + w_2 x_2 + b$")
    plt.tight_layout()
    out = ASSETS / "hyperplane_3d.png"
    plt.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close()
    save_rgb(out)


def fig_scaling():
    np.random.seed(42)
    area = RNG.uniform(30, 120, 80)
    floor = RNG.integers(1, 25, 80)
    price = 0.8 * area + 15 * floor + RNG.normal(0, 50, 80)

    X = np.column_stack([area, floor])
    lr_raw = LinearRegression().fit(X, price)
    Xs = StandardScaler().fit_transform(X)
    lr_scaled = LinearRegression().fit(Xs, price)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, coefs, title in [
        (axes[0], lr_raw.coef_, "без масштабирования"),
        (axes[1], lr_scaled.coef_, "после StandardScaler"),
    ]:
        labels = ["площадь", "этаж"]
        ax.bar(labels, coefs, color=["#1f77b4", "#ff7f0e"])
        ax.axhline(0, color="k", lw=0.5)
        ax.set_ylabel("вес")
        ax.set_title(title)
    fig.suptitle("Масштаб влияет на сравнимость весов", fontsize=11)
    plt.tight_layout()
    out = ASSETS / "scaling_weights_compare.png"
    plt.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close()
    save_rgb(out)


def fig_multicollinearity():
    np.random.seed(42)
    n = 100
    x1 = RNG.normal(0, 1, n)
    x2 = x1 + RNG.normal(0, 0.05, n)
    y = 3 * x1 + RNG.normal(0, 0.5, n)
    X = np.column_stack([x1, x2])

    coefs = []
    for _ in range(30):
        idx = RNG.choice(n, n, replace=True)
        m = LinearRegression().fit(X[idx], y[idx])
        coefs.append(m.coef_)
    coefs = np.array(coefs)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    im = axes[0].imshow(np.corrcoef(x1, x2).reshape(2, 2), cmap="Blues", vmin=0, vmax=1)
    axes[0].set_xticks([0, 1], labels=["$x_1$", "$x_2$"])
    axes[0].set_yticks([0, 1], labels=["$x_1$", "$x_2$"])
    axes[0].set_title("корреляция ≈ 1")
    for i in range(2):
        for j in range(2):
            axes[0].text(j, i, f"{np.corrcoef(x1, x2)[0,1]:.2f}", ha="center", va="center", color="k")
    fig.colorbar(im, ax=axes[0], fraction=0.046)

    bp = axes[1].boxplot([coefs[:, 0], coefs[:, 1]], tick_labels=["$w_1$", "$w_2$"], patch_artist=True)
    for patch, c in zip(bp["boxes"], ["#1f77b4", "#ff7f0e"]):
        patch.set_facecolor(c)
    axes[1].axhline(0, color="k", lw=0.5)
    axes[1].set_ylabel("вес (bootstrap)")
    axes[1].set_title("веса нестабильны")
    fig.suptitle("Мультиколлинеарность", fontsize=11)
    plt.tight_layout()
    out = ASSETS / "multicollinearity.png"
    plt.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close()
    save_rgb(out)


def fig_train_test():
    np.random.seed(42)
    x = np.linspace(0, 10, 80)
    y = 2 * x + 3 + RNG.normal(0, 2, 80)
    x_train, y_train = x[:60], y[:60]
    x_test, y_test = x[60:], y[60:]
    m = LinearRegression().fit(x_train.reshape(-1, 1), y_train)

    def r2(y_true, y_pred):
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return 1 - ss_res / ss_tot

    r2_train = r2(y_train, m.predict(x_train.reshape(-1, 1)))
    r2_test = r2(y_test, m.predict(x_test.reshape(-1, 1)))

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, xs, ys, title in [
        (axes[0], x_train, y_train, "train"),
        (axes[1], x_test, y_test, "test"),
    ]:
        ax.scatter(xs, ys, c="#1f77b4", s=22)
        line_x = np.array([xs.min(), xs.max()])
        ax.plot(line_x, m.predict(line_x.reshape(-1, 1)), "r-", lw=2)
        ax.set_title(title)
        ax.set_xlabel("$x$")
        ax.set_ylabel("$y$")
    fig.suptitle(f"$R^2$: train={r2_train:.2f}, test={r2_test:.2f}", fontsize=11)
    plt.tight_layout()
    out = ASSETS / "train_test_split.png"
    plt.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close()
    save_rgb(out)


def fig_metrics():
    y_true = np.array([10, 12, 8, 15, 11])
    y_pred = np.array([9.5, 13.0, 9.0, 13.5, 10.5])
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - ss_res / ss_tot

    fig, ax = plt.subplots(figsize=(5, 3.5))
    names = ["MAE", "RMSE", f"$R^2$"]
    vals = [mae, rmse, r2]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    bars = ax.bar(names, vals, color=colors)
    ax.set_ylabel("значение")
    ax.set_title("Метрики на одной выборке")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, f"{v:.2f}", ha="center", fontsize=9)
    plt.tight_layout()
    out = ASSETS / "regression_metrics_bar.png"
    plt.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close()
    save_rgb(out)


def fig_weights_interpretation():
    features = ["площадь", "этаж", "район_A", "район_B"]
    weights = [0.85, 0.42, -0.15, 0.10]
    fig, ax = plt.subplots(figsize=(5, 3.5))
    colors = ["#2ca02c" if w >= 0 else "#d62728" for w in weights]
    ax.barh(features, weights, color=colors)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("вес (после StandardScaler)")
    ax.set_title("Сравнимое влияние признаков")
    plt.tight_layout()
    out = ASSETS / "standardized_weights.png"
    plt.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close()
    save_rgb(out)


def fig_pipeline():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
    for ax, title, steps, leak in [
        (axes[0], "утечка (плохо)", ["scale\n(все данные)", "split", "fit"], True),
        (axes[1], "Pipeline (хорошо)", ["split", "Pipeline:\nscale+fit", "predict test"], False),
    ]:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 3)
        ax.axis("off")
        ax.set_title(title, color="#d62728" if leak else "#2ca02c")
        xs = [1.5, 5, 8.5]
        for i, (x, label) in enumerate(zip(xs, steps)):
            box = FancyBboxPatch(
                (x - 1.1, 1.0), 2.2, 1.0, boxstyle="round,pad=0.05", fc="#eef2ff", ec="#333"
            )
            ax.add_patch(box)
            ax.text(x, 1.5, label, ha="center", va="center", fontsize=8)
            if i < len(steps) - 1:
                ax.add_patch(
                    FancyArrowPatch((x + 1.1, 1.5), (xs[i + 1] - 1.1, 1.5), arrowstyle="->", mutation_scale=12)
                )
    fig.suptitle("Data leakage vs Pipeline", fontsize=11)
    plt.tight_layout()
    out = ASSETS / "pipeline_leakage.png"
    plt.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close()
    save_rgb(out)


def fig_leverage_x():
    np.random.seed(42)
    x = np.concatenate([RNG.uniform(1, 9, 25), [14.0]])
    y = 2 * x + 1 + RNG.normal(0, 1.2, 26)
    y[-1] = 2 * x[-1] + 1 + 0.5

    m_clean = LinearRegression().fit(x[:-1].reshape(-1, 1), y[:-1])
    m_all = LinearRegression().fit(x.reshape(-1, 1), y)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    xx = np.linspace(0, 15, 100).reshape(-1, 1)
    for ax, mask, model, title in [
        (axes[0], np.ones(len(x), dtype=bool), m_clean, "без leverage-точки"),
        (axes[1], np.ones(len(x), dtype=bool), m_all, "leverage по $x$"),
    ]:
        ax.scatter(x[mask], y[mask], c="#1f77b4", s=35)
        if not mask.all():
            pass
        if title.startswith("leverage"):
            ax.scatter([x[-1]], [y[-1]], c="#ff7f0e", s=120, zorder=5, label="далеко по $x$")
            ax.legend(fontsize=8)
        ax.plot(xx, model.predict(xx), "r-", lw=2)
        ax.set_xlim(0, 15)
        ax.set_title(title)
        ax.set_xlabel("$x$")
        ax.set_ylabel("$y$")
    fig.suptitle("Выброс в $x$ меняет наклон", fontsize=11)
    plt.tight_layout()
    out = ASSETS / "outlier_leverage_x.png"
    plt.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close()
    save_rgb(out)


def fig_residuals_hist():
    np.random.seed(42)
    x = RNG.uniform(0, 10, 50)
    y = 1.5 * x + 2 + RNG.normal(0, 1.5, 50)
    pred = LinearRegression().fit(x.reshape(-1, 1), y).predict(x.reshape(-1, 1))
    resid = y - pred

    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.hist(resid, bins=12, color="#1f77b4", edgecolor="white")
    ax.axvline(0, color="#d62728", lw=1.5, label="среднее ≈ 0")
    ax.set_xlabel("остаток $\\varepsilon$")
    ax.set_ylabel("частота")
    ax.set_title("Остатки вокруг нуля")
    ax.legend(fontsize=8)
    plt.tight_layout()
    out = ASSETS / "residuals_histogram.png"
    plt.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close()
    save_rgb(out)


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
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
