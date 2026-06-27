"""Генерация всех иллюстраций logisticheskaya_regressiya.

Данные подобраны педагогически: эффект на графике должен быть виден сразу.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import auc, precision_recall_curve, roc_curve
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "agents"))
from viz_style import (  # noqa: E402
    BG_BOX,
    TEXT_DARK,
    apply_matplotlib_slide_style,
    save_slide_figure,
    style_axes,
)

ASSETS = Path(__file__).resolve().parent
RNG = np.random.default_rng(42)


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def make_binary_data(n: int = 80) -> tuple[np.ndarray, np.ndarray]:
    """Два кластера, линейно разделимых."""
    n0 = n // 2
    n1 = n - n0
    x0 = RNG.normal([-1.5, -1.0], 0.55, (n0, 2))
    x1 = RNG.normal([1.5, 1.0], 0.55, (n1, 2))
    X = np.vstack([x0, x1])
    y = np.array([0] * n0 + [1] * n1)
    return X, y


def fig_binary_classification_boundary():
    apply_matplotlib_slide_style()
    X, y = make_binary_data(90)
    clf = LogisticRegression(C=1e6, max_iter=500).fit(X, y)
    w = clf.coef_[0]
    b = clf.intercept_[0]

    fig, ax = plt.subplots(figsize=(5, 3.8))
    style_axes(ax)
    ax.scatter(X[y == 0, 0], X[y == 0, 1], c="#1f77b4", s=35, label="класс 0", alpha=0.85)
    ax.scatter(X[y == 1, 0], X[y == 1, 1], c="#ff7f0e", s=35, label="класс 1", alpha=0.85)

    xlim = ax.get_xlim()
    xx = np.linspace(xlim[0], xlim[1], 100)
    yy = -(w[0] * xx + b) / w[1]
    ax.plot(xx, yy, "r-", lw=2.5, label="граница решения")

    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.set_title("Бинарная классификация")
    ax.legend()
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "binary_classification_boundary.png")


def fig_linear_reg_on_classification():
    apply_matplotlib_slide_style(compact=True)
    x = np.linspace(0, 10, 30)
    y = (x > 5).astype(float)
    y[12:14] = 0.5  # шум у границы
    x_out = np.append(x, 12.0)
    y_out = np.append(y, 1.0)

    from sklearn.linear_model import LinearRegression

    m_clean = LinearRegression().fit(x.reshape(-1, 1), y)
    m_out = LinearRegression().fit(x_out.reshape(-1, 1), y_out)
    xx = np.linspace(-1, 13, 200).reshape(-1, 1)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, xs, ys, model, title in [
        (axes[0], x, y, m_clean, "предсказания вне [0, 1]"),
        (axes[1], x_out, y_out, m_out, "выброс сдвигает линию"),
    ]:
        style_axes(ax)
        ax.scatter(xs, ys, c="#1f77b4", s=40)
        if title.startswith("выброс"):
            ax.scatter([12], [1], c="#ff7f0e", s=120, zorder=5)
        pred = model.predict(xx)
        ax.plot(xx, pred, "r-", lw=2)
        ax.axhline(0, color="#888888", lw=0.6, linestyle="--")
        ax.axhline(1, color="#888888", lw=0.6, linestyle="--")
        ax.set_ylim(-0.4, 1.5)
        ax.set_xlabel("$x$")
        ax.set_ylabel("код класса / $\\hat{y}$")
        ax.set_title(title)
    fig.suptitle("Линейная регрессия для классификации", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "linear_reg_on_classification.png")


def fig_sigmoid_curve():
    apply_matplotlib_slide_style()
    z = np.linspace(-6, 6, 300)
    p = sigmoid(z)

    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    ax.plot(z, p, color="#1f77b4", lw=2.5, label="$\\sigma(z)$")
    ax.axhline(0.5, color="#888888", lw=0.8, linestyle="--", label="0.5")
    ax.axvline(0, color="#888888", lw=0.8, linestyle="--")
    ax.fill_between(z, 0, p, where=(z < 0), alpha=0.12, color="#1f77b4")
    ax.fill_between(z, p, 1, where=(z > 0), alpha=0.12, color="#ff7f0e")
    ax.annotate("$z \\to -\\infty \\Rightarrow p \\to 0$", xy=(-5, 0.08), color=TEXT_DARK, fontsize=12)
    ax.annotate("$z \\to +\\infty \\Rightarrow p \\to 1$", xy=(1.5, 0.88), color=TEXT_DARK, fontsize=12)
    ax.set_xlabel("$z = \\vec{w}\\cdot\\vec{x} + b$")
    ax.set_ylabel("$P(y=1)$")
    ax.set_title("Сигмоида сжимает выход в [0, 1]")
    ax.legend()
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "sigmoid_curve.png")


def fig_decision_threshold_05():
    apply_matplotlib_slide_style(compact=True)
    X, y = make_binary_data(70)
    clf = LogisticRegression(C=1e6, max_iter=500).fit(X, y)
    w, b = clf.coef_[0], clf.intercept_[0]

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    ax = axes[0]
    style_axes(ax)
    x1 = np.linspace(X[:, 0].min() - 0.5, X[:, 0].max() + 0.5, 200)
    z_line = w[0] * x1 + b  # x2=0 срез
    ax.plot(x1, sigmoid(z_line), color="#1f77b4", lw=2)
    ax.axhline(0.5, color="#d62728", lw=1.5, linestyle="--", label="порог 0.5")
    ax.fill_between(x1, 0, sigmoid(z_line), where=(sigmoid(z_line) < 0.5), alpha=0.15, color="#1f77b4", label="класс 0")
    ax.fill_between(x1, sigmoid(z_line), 1, where=(sigmoid(z_line) >= 0.5), alpha=0.15, color="#ff7f0e", label="класс 1")
    ax.set_xlabel("$x_1$ (при $x_2=0$)")
    ax.set_ylabel("$P(y=1)$")
    ax.set_title("Порог 0.5 → решение")
    ax.legend(fontsize=11)

    ax = axes[1]
    style_axes(ax)
    ax.scatter(X[y == 0, 0], X[y == 0, 1], c="#1f77b4", s=30, alpha=0.8)
    ax.scatter(X[y == 1, 0], X[y == 1, 1], c="#ff7f0e", s=30, alpha=0.8)
    xx = np.linspace(X[:, 0].min() - 0.5, X[:, 0].max() + 0.5, 100)
    yy = -(w[0] * xx + b) / w[1]
    ax.plot(xx, yy, "r-", lw=2.5, label="$P=0.5$")
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.set_title("$\\vec{w}\\cdot\\vec{x}+b=0$")
    ax.legend()
    fig.suptitle("От вероятности к границе", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "decision_threshold_05.png")


def fig_vanishing_gradient_mse():
    apply_matplotlib_slide_style(compact=True)
    z = np.linspace(-8, 8, 400)
    p = sigmoid(z)
    y = 1.0
    # MSE grad magnitude ~ (p-y) * sigma'(z)
    mse_grad = np.abs((p - y) * p * (1 - p))
    # LogLoss grad magnitude ~ |p - y| (no sigma' factor)
    logloss_grad = np.abs(p - y)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    ax = axes[0]
    style_axes(ax)
    ax.plot(z, mse_grad, color="#d62728", lw=2.5)
    ax.axvline(-6, color="#888888", lw=0.8, linestyle=":")
    ax.annotate("уверена, но неправа\n$y=1$, $z \\ll 0$", xy=(-6, mse_grad[z <= -6][-1]), xytext=(-2, 0.08),
                arrowprops=dict(arrowstyle="->", color="#444444"), color=TEXT_DARK, fontsize=11)
    ax.set_xlabel("$z$")
    ax.set_ylabel("$|\\nabla|$ (MSE + сигмоида)")
    ax.set_title("градиент → 0")

    ax = axes[1]
    style_axes(ax)
    ax.plot(z, logloss_grad, color="#2ca02c", lw=2.5)
    ax.annotate("ошибка большая\n→ градиент большой", xy=(-6, logloss_grad[z <= -6][-1]), xytext=(-1, 0.85),
                arrowprops=dict(arrowstyle="->", color="#444444"), color=TEXT_DARK, fontsize=11)
    ax.set_xlabel("$z$")
    ax.set_ylabel("$|\\nabla|$ (LogLoss)")
    ax.set_title("градиент остаётся")
    fig.suptitle("Затухание градиента при MSE", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "vanishing_gradient_mse.png")


def fig_logloss_curves():
    apply_matplotlib_slide_style(compact=True)
    p = np.linspace(0.01, 0.99, 300)
    loss_y1 = -np.log(p)
    loss_y0 = -np.log(1 - p)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    ax = axes[0]
    style_axes(ax)
    ax.plot(p, loss_y1, color="#ff7f0e", lw=2, label="$y=1$: $-\\log(p)$")
    ax.plot(p, loss_y0, color="#1f77b4", lw=2, label="$y=0$: $-\\log(1-p)$")
    ax.axvline(0.5, color="#888888", lw=0.6, linestyle="--")
    ax.set_xlabel("предсказанная $p$")
    ax.set_ylabel("штраф")
    ax.set_ylim(0, 5)
    ax.legend()
    ax.set_title("LogLoss по классам")

    ax = axes[1]
    style_axes(ax)
    examples = [("p=0.99, y=1", 0.01), ("p=0.01, y=1", 4.6), ("p=0.99, y=0", 4.6), ("p=0.01, y=0", 0.01)]
    labels = [e[0] for e in examples]
    vals = [e[1] for e in examples]
    colors = ["#2ca02c", "#d62728", "#d62728", "#2ca02c"]
    bars = ax.barh(labels, vals, color=colors)
    ax.set_xlabel("штраф")
    ax.set_title("примеры")
    for bar, v in zip(bars, vals):
        ax.text(v + 0.08, bar.get_y() + bar.get_height() / 2, f"{v:.1f}", va="center", color=TEXT_DARK)
    fig.suptitle("LogLoss (бинарная кросс-энтропия)", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "logloss_curves.png")


def fig_logreg_gradient_descent():
    apply_matplotlib_slide_style()
    X, y = make_binary_data(60)
    w0 = np.linspace(-4, 4, 120)
    w1 = np.linspace(-4, 4, 120)
    W0, W1 = np.meshgrid(w0, w1)
    b_fixed = 0.0

    def logloss_surface(w0g, w1g):
        z = X[:, 0] * w0g + X[:, 1] * w1g + b_fixed
        p = sigmoid(z)
        eps = 1e-9
        return -np.mean(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))

    Z = np.vectorize(logloss_surface)(W0, W1)
    path = np.array([[3.5, 3.0], [2.4, 2.1], [1.5, 1.3], [0.9, 0.7], [0.55, 0.45]])

    fig, ax = plt.subplots(figsize=(5, 3.8))
    style_axes(ax)
    ax.contour(W0, W1, Z, levels=15, colors="#aaaaaa", linewidths=0.8)
    ax.plot(path[:, 0], path[:, 1], "o-", color="#d62728", lw=2, markersize=6, label="градиентный спуск")
    ax.scatter([path[-1, 0]], [path[-1, 1]], c="#2ca02c", s=70, zorder=5, label="минимум LogLoss")
    ax.set_xlabel("$w_0$")
    ax.set_ylabel("$w_1$")
    ax.set_title("$\\nabla_w L = \\frac{1}{N} X^T (p - y)$")
    ax.legend()
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "logreg_gradient_descent.png")


def fig_regularization_C_weights():
    apply_matplotlib_slide_style(compact=True)
    X, y = make_binary_data(100)
    X = np.column_stack([X, RNG.normal(0, 1, (len(y), 3))])  # лишние признаки
    C_vals = [0.01, 0.1, 1.0, 10.0, 1000.0]
    coefs = []
    for c in C_vals:
        m = make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=1000))
        m.fit(X, y)
        coefs.append(m.named_steps["logisticregression"].coef_.ravel())
    coefs = np.array(coefs)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    ax = axes[0]
    style_axes(ax)
    for j in range(coefs.shape[1]):
        ax.plot(np.log10(C_vals), coefs[:, j], "o-", lw=1.5, markersize=5, label=f"$w_{j+1}$" if j < 4 else None)
    ax.axhline(0, color="#444444", lw=0.6)
    ax.set_xlabel("$\\log_{10}(C)$")
    ax.set_ylabel("вес")
    ax.set_title("C ↑ → веса растут")
    ax.set_xticks(np.log10(C_vals))
    ax.set_xticklabels(["0.01", "0.1", "1", "10", "1000"])

    ax = axes[1]
    style_axes(ax)
    labels = ["мало C\n(сильная reg)", "много C\n(слабая reg)"]
    max_abs = [np.max(np.abs(coefs[0])), np.max(np.abs(coefs[-1]))]
    bars = ax.bar(labels, max_abs, color=["#2ca02c", "#d62728"])
    ax.set_ylabel("$\\max |w_j|$")
    ax.set_title("разделимые данные → риск")
    for bar, v in zip(bars, max_abs):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.05, f"{v:.2f}", ha="center", color=TEXT_DARK)
    fig.suptitle("Регуляризация: параметр C", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "regularization_C_weights.png")


def fig_accuracy_imbalance_trap():
    apply_matplotlib_slide_style(compact=True)
    n_pos, n_neg = 10, 990
    always_neg_acc = n_neg / (n_pos + n_neg)
    good_model_acc = 0.92

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    ax = axes[0]
    style_axes(ax)
    ax.bar(["легальные", "мошенничество"], [n_neg, n_pos], color=["#1f77b4", "#d62728"])
    ax.set_ylabel("число транзакций")
    ax.set_title("дисбаланс 99% / 1%")

    ax = axes[1]
    style_axes(ax)
    bars = ax.bar(["всегда «легально»", "реальная модель"], [always_neg_acc, good_model_acc],
                  color=["#d62728", "#2ca02c"])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("accuracy")
    ax.set_title("accuracy обманчива")
    for bar, v, lbl in zip(bars, [always_neg_acc, good_model_acc], ["99%", "92%"]):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.02, lbl, ha="center", color=TEXT_DARK, fontweight="bold")
    fig.suptitle("Ловушка Accuracy", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "accuracy_imbalance_trap.png")


def fig_roc_and_pr_curves():
    apply_matplotlib_slide_style(compact=True)
    n = 1000
    n_pos = 50
    y = np.array([0] * (n - n_pos) + [1] * n_pos)
    scores = RNG.uniform(0, 1, n)
    scores[y == 1] += RNG.uniform(0.3, 0.6, n_pos)
    scores = np.clip(scores, 0, 1)

    fpr, tpr, _ = roc_curve(y, scores)
    prec, rec, _ = precision_recall_curve(y, scores)
    roc_auc = auc(fpr, tpr)
    pr_auc = auc(rec, prec)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    ax = axes[0]
    style_axes(ax)
    ax.plot(fpr, tpr, color="#1f77b4", lw=2, label=f"AUC={roc_auc:.2f}")
    ax.plot([0, 1], [0, 1], "--", color="#888888", lw=1)
    ax.set_xlabel("FPR")
    ax.set_ylabel("TPR (Recall)")
    ax.set_title("ROC-кривая")
    ax.legend()

    ax = axes[1]
    style_axes(ax)
    ax.plot(rec, prec, color="#ff7f0e", lw=2, label=f"PR-AUC={pr_auc:.2f}")
    baseline = n_pos / n
    ax.axhline(baseline, color="#888888", lw=1, linestyle="--", label=f"baseline={baseline:.2f}")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("PR-кривая (редкий класс)")
    ax.legend(fontsize=11)
    fig.suptitle("ROC vs PR при дисбалансе", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "roc_and_pr_curves.png")


def fig_softmax_three_classes():
    apply_matplotlib_slide_style()
    z = np.array([2.0, 0.5, -1.0])
    exp_z = np.exp(z - z.max())
    p = exp_z / exp_z.sum()
    classes = ["класс A", "класс B", "класс C"]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    fig, ax = plt.subplots(figsize=(5, 3.5))
    style_axes(ax)
    bars = ax.bar(classes, p, color=colors, edgecolor="white")
    ax.set_ylabel("вероятность $p_k$")
    ax.set_ylim(0, 1.05)
    ax.set_title("Softmax: $\\sum_k p_k = 1$")
    for bar, val in zip(bars, p):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.03, f"{val:.2f}", ha="center", color=TEXT_DARK)
    ax.axhline(1.0, color="#888888", lw=0.6, linestyle="--", alpha=0.5)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "softmax_three_classes.png")


def fig_odds_logodds_scale():
    apply_matplotlib_slide_style(compact=True)
    p = np.linspace(0.05, 0.95, 200)
    odds = p / (1 - p)
    log_odds = np.log(odds)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    ax = axes[0]
    style_axes(ax)
    ax.plot(p, odds, color="#1f77b4", lw=2)
    ax.axvline(0.5, color="#888888", lw=0.8, linestyle="--")
    ax.axhline(1, color="#888888", lw=0.8, linestyle="--")
    ax.scatter([0.5], [1], c="#d62728", s=60, zorder=5)
    ax.set_xlabel("$P$")
    ax.set_ylabel("Odds = $P/(1-P)$")
    ax.set_title("шансы")

    ax = axes[1]
    style_axes(ax)
    ax.plot(p, log_odds, color="#ff7f0e", lw=2)
    ax.axvline(0.5, color="#888888", lw=0.8, linestyle="--")
    ax.axhline(0, color="#888888", lw=0.8, linestyle="--")
    ax.scatter([0.5], [0], c="#d62728", s=60, zorder=5)
    ax.set_xlabel("$P$")
    ax.set_ylabel("log-odds = $z$")
    ax.set_title("$z = \\vec{w}\\cdot\\vec{x}+b$")
    fig.suptitle("Odds и log-odds", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "odds_logodds_scale.png")


def fig_logreg_pipeline():
    apply_matplotlib_slide_style(compact=True)
    fig, ax = plt.subplots(figsize=(10, 3.2), facecolor="white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3)
    ax.axis("off")
    ax.set_title("LogReg чувствительна к масштабу", color=TEXT_DARK, pad=12)

    steps = [
        ("$X_{train}$", 1.2),
        ("Standard\nScaler", 3.6),
        ("Logistic\nRegression", 6.2),
        ("$\\hat{y}$, proba", 9.0),
    ]
    for label, x in steps:
        ax.add_patch(FancyBboxPatch((x - 0.9, 1.0), 1.8, 1.0, boxstyle="round,pad=0.05", fc=BG_BOX, ec="#333333"))
        ax.text(x, 1.5, label, ha="center", va="center", color=TEXT_DARK, fontsize=12)
    for i in range(len(steps) - 1):
        x0 = steps[i][1] + 0.9
        x1 = steps[i + 1][1] - 0.9
        ax.add_patch(FancyArrowPatch((x0, 1.5), (x1, 1.5), arrowstyle="->", mutation_scale=12, color="#444444"))

    ax.text(4.9, 0.35, "make_pipeline(StandardScaler(), LogisticRegression(C=1.0))", ha="center", color="#666666", fontsize=11)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "logreg_pipeline.png")


def fig_class_weight_balanced():
    apply_matplotlib_slide_style(compact=True)
    n = 400
    n_pos = 40
    X = RNG.normal(0, 1, (n, 2))
    X[n_pos:, 0] += 1.5
    y = np.array([1] * n_pos + [0] * (n - n_pos))

    m_plain = LogisticRegression(max_iter=500).fit(X, y)
    m_bal = LogisticRegression(class_weight="balanced", max_iter=500).fit(X, y)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, model, title in [
        (axes[0], m_plain, "без class_weight"),
        (axes[1], m_bal, "class_weight='balanced'"),
    ]:
        style_axes(ax)
        ax.scatter(X[y == 0, 0], X[y == 0, 1], c="#1f77b4", s=22, alpha=0.6, label="класс 0")
        ax.scatter(X[y == 1, 0], X[y == 1, 1], c="#ff7f0e", s=40, alpha=0.9, label="класс 1 (редкий)")
        w, b = model.coef_[0], model.intercept_[0]
        xx = np.linspace(X[:, 0].min() - 0.5, X[:, 0].max() + 0.5, 100)
        yy = -(w[0] * xx + b) / w[1]
        ax.plot(xx, yy, "r-", lw=2)
        rec_pos = np.mean(model.predict(X[y == 1]) == 1)
        ax.set_title(f"{title}\nRecall(minor)={rec_pos:.0%}")
        ax.set_xlabel("$x_1$")
        ax.set_ylabel("$x_2$")
        ax.legend(fontsize=10)
    fig.suptitle("Несбалансированные данные", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "class_weight_balanced.png")


def fig_calibration_reliability():
    apply_matplotlib_slide_style(compact=True)
    n = 2000
    X = RNG.normal(0, 1, (n, 3))
    y = (X[:, 0] + 0.5 * X[:, 1] + RNG.normal(0, 0.8, n) > 0).astype(int)
    proba = LogisticRegression(max_iter=500).fit(X, y).predict_proba(X)[:, 1]

    bins = np.linspace(0, 1, 11)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    frac_pos = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        mask = (proba >= lo) & (proba < hi)
        frac_pos.append(np.mean(y[mask]) if mask.sum() > 5 else np.nan)
    frac_pos = np.array(frac_pos)

    # «переуверенная» модель для сравнения
    overconf = np.clip(proba * 1.4 - 0.15, 0.01, 0.99)
    frac_over = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        mask = (overconf >= lo) & (overconf < hi)
        frac_over.append(np.mean(y[mask]) if mask.sum() > 5 else np.nan)
    frac_over = np.array(frac_over)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, frac, title, color in [
        (axes[0], frac_pos, "LogReg (хорошо)", "#2ca02c"),
        (axes[1], frac_over, "переуверенная модель", "#d62728"),
    ]:
        style_axes(ax)
        ax.plot([0, 1], [0, 1], "--", color="#888888", lw=1, label="идеал")
        valid = ~np.isnan(frac)
        ax.plot(bin_centers[valid], frac[valid], "o-", color=color, lw=2, markersize=6, label="наблюдаемая частота")
        ax.set_xlabel("предсказанная вероятность")
        ax.set_ylabel("доля класса 1")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title(title)
        ax.legend(fontsize=10)
    fig.suptitle("Калибровка вероятностей", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "calibration_reliability.png")


def fig_nonlinear_decision_boundary():
    apply_matplotlib_slide_style(compact=True)
    n = 40
    X = np.vstack([
        RNG.normal([-1, -1], 0.35, (n, 2)),
        RNG.normal([1, -1], 0.35, (n, 2)),
        RNG.normal([-1, 1], 0.35, (n, 2)),
        RNG.normal([1, 1], 0.35, (n, 2)),
    ])
    y = np.array([0] * n + [1] * n + [1] * n + [0] * n)  # XOR

    clf = LogisticRegression(max_iter=500).fit(X, y)
    w, b = clf.coef_[0], clf.intercept_[0]

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    ax = axes[0]
    style_axes(ax)
    ax.scatter(X[y == 0, 0], X[y == 0, 1], c="#1f77b4", s=35, label="класс 0")
    ax.scatter(X[y == 1, 0], X[y == 1, 1], c="#ff7f0e", s=35, label="класс 1")
    xx = np.linspace(-2, 2, 100)
    yy = -(w[0] * xx + b) / w[1]
    ax.plot(xx, yy, "r-", lw=2, label="линейная граница")
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_title("XOR: линия не разделяет")
    ax.legend(fontsize=10)

    ax = axes[1]
    style_axes(ax)
    ax.scatter(X[y == 0, 0], X[y == 0, 1], c="#1f77b4", s=35)
    ax.scatter(X[y == 1, 0], X[y == 1, 1], c="#ff7f0e", s=35)
    circle = plt.Circle((0, 0), 1.0, fill=False, color="#2ca02c", lw=2.5, linestyle="--")
    ax.add_patch(circle)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_title("нужна нелинейность")
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    fig.suptitle("Когда LogReg не справляется", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "nonlinear_decision_boundary.png")


def fig_linear_vs_logistic_summary():
    apply_matplotlib_slide_style(compact=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))

    ax = axes[0]
    style_axes(ax)
    x = np.linspace(0, 10, 25)
    y_reg = 2 * x + 3 + RNG.normal(0, 2, 25)
    from sklearn.linear_model import LinearRegression

    m = LinearRegression().fit(x.reshape(-1, 1), y_reg)
    xx = np.linspace(0, 10, 100)
    ax.scatter(x, y_reg, c="#1f77b4", s=30)
    ax.plot(xx, m.predict(xx.reshape(-1, 1)), "r-", lw=2)
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y \\in \\mathbb{R}$")
    ax.set_title("линейная регрессия")

    ax = axes[1]
    style_axes(ax)
    X, y = make_binary_data(60)
    clf = LogisticRegression(C=1e6, max_iter=500).fit(X, y)
    w, b = clf.coef_[0], clf.intercept_[0]
    ax.scatter(X[y == 0, 0], X[y == 0, 1], c="#1f77b4", s=30, label="класс 0")
    ax.scatter(X[y == 1, 0], X[y == 1, 1], c="#ff7f0e", s=30, label="класс 1")
    xline = np.linspace(X[:, 0].min() - 0.5, X[:, 0].max() + 0.5, 100)
    yline = -(w[0] * xline + b) / w[1]
    ax.plot(xline, yline, "r-", lw=2)
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.set_title("логистическая регрессия")
    ax.legend(fontsize=10)
    fig.suptitle("Регрессия vs классификация", color=TEXT_DARK)
    plt.tight_layout()
    save_slide_figure(fig, ASSETS / "linear_vs_logistic_summary.png")


def main():
    fig_binary_classification_boundary()
    fig_linear_reg_on_classification()
    fig_sigmoid_curve()
    fig_decision_threshold_05()
    fig_vanishing_gradient_mse()
    fig_logloss_curves()
    fig_logreg_gradient_descent()
    fig_regularization_C_weights()
    fig_accuracy_imbalance_trap()
    fig_roc_and_pr_curves()
    fig_softmax_three_classes()
    fig_odds_logodds_scale()
    fig_logreg_pipeline()
    fig_class_weight_balanced()
    fig_calibration_reliability()
    fig_nonlinear_decision_boundary()
    fig_linear_vs_logistic_summary()
    names = sorted(p.name for p in ASSETS.glob("*.png"))
    print(f"Generated {len(names)} PNG in {ASSETS}")
    for name in names:
        print(f"  {name}")


if __name__ == "__main__":
    main()
