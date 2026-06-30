"""Сборка и проверка lessons/vizualizatsiya/code.ipynb — runnable секции по слайдам."""
from __future__ import annotations

import json
import re
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents"))

from notebook_utils import build_ipynb, save_ipynb, select_slides_for_notebook  # noqa: E402
from slide_utils import read_slides  # noqa: E402

LESSON = ROOT / "lessons" / "vizualizatsiya"

SETUP_BOOTSTRAP = """\
import sys
from pathlib import Path

# Jupyter обычно открывает ноутбук из каталога урока; если cwd = корень репо — добавим путь один раз.
_lesson = Path.cwd()
if not (_lesson / "viz_demo_data.py").exists():
    _lesson = Path.cwd() / "lessons" / "vizualizatsiya"
if (_lesson / "viz_demo_data.py").exists() and str(_lesson) not in sys.path:
    sys.path.insert(0, str(_lesson))
from viz_demo_data import ensure_viz_context

ensure_viz_context(globals())
"""

# В секциях — только код примера; df и импорты задаёт Setup.

SETUP_CELL = f"""\
# Setup
%matplotlib inline

{SETUP_BOOTSTRAP}
print("Готово: df", df.shape, "| clf обучен | каталог экспорта:", _OUT)
"""

SECTION_CODE: dict[str, str] = {
    "Быстрый старт: pandas built-in визуализация": """\
df[["area", "price"]].plot(kind="hist", alpha=0.6, bins=20, figsize=(8, 3))
plt.tight_layout()
plt.show()
df[["area", "price"]].plot(kind="box", figsize=(6, 4))
plt.show()
""",
    "Matplotlib: архитектура Figure и Axes": """\
fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(df["area"], df["price"], alpha=0.6, c=df["target"], cmap="coolwarm")
ax.set_xlabel("площадь")
ax.set_ylabel("цена")
ax.set_title("fig, ax = plt.subplots()")
plt.tight_layout()
plt.show()
""",
    "Несколько графиков на одной фигуре: subplot": """\
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
axes[0, 0].hist(train["area"], bins=20, color="steelblue", alpha=0.85)
axes[0, 1].hist(test["area"], bins=20, color="darkorange", alpha=0.85)
axes[1, 0].scatter(train["area"], train["price"], s=12, alpha=0.5)
axes[1, 1].scatter(test["area"], test["price"], s=12, alpha=0.5)
fig.suptitle("train vs test")
plt.tight_layout()
plt.show()
""",
    "Кастомизация: цвета, стили, аннотации": """\
fig, ax = plt.subplots(figsize=(6, 4))
x = df["area"].to_numpy()
y = df["price"].to_numpy()
ax.scatter(x, y, alpha=0.5, c="steelblue")
idx = int(np.argmax(y))
ax.annotate(
    "Outlier",
    xy=(x[idx], y[idx]),
    xytext=(x[idx] + 15, y[idx] + 80),
    arrowprops=dict(arrowstyle="->", color="crimson"),
)
ax.legend(["точки"], loc="best", frameon=False)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
""",
    "Сохранение и экспорт графиков": """\
fig, ax = plt.subplots(figsize=(5, 3))
ax.plot([1, 2, 3], [1, 4, 2])
png_path = _OUT / "plot.png"
fig.savefig(png_path, dpi=150, bbox_inches="tight")
print("PNG:", png_path, "exists:", png_path.exists())
if px is not None:
    fig_px = px.scatter(df.head(40), x="area", y="price", color="city")
    html_path = _OUT / "plot.html"
    fig_px.write_html(html_path)
    print("HTML:", html_path, "exists:", html_path.exists())
else:
    print("plotly не установлен — пропуск write_html")
plt.close(fig)
""",
    "Plotly: интерактивные графики одной строкой": """\
if px is None:
    print("plotly не установлен")
else:
    fig1 = px.scatter(df, x="area", y="price", color="city", hover_data=["id"])
    fig2 = px.histogram(df, x="income", color="segment", marginal="box")
    print("Plotly figures:", type(fig1).__name__, type(fig2).__name__)
""",
    "Plotly: продвинутые возможности": """\
if px is None:
    print("plotly не установлен")
else:
    fig3d = px.scatter_3d(df.head(80), x="x", y="y", z="z", color="target")
    fig_anim = px.scatter(df.head(80), x="x", y="y", animation_frame="year", color="city")
    print("3D + animation:", fig3d.data[0].type, len(fig_anim.frames), "frames")
""",
    "Распределение одной переменной: гистограмма и KDE": """\
plt.figure(figsize=(7, 4))
sns.histplot(df["income"].dropna(), kde=True, color="steelblue")
plt.title("income: hist + KDE")
plt.tight_layout()
plt.show()
if px is not None:
    px.histogram(df, x="income", color="segment", marginal="box")
""",
    "Быстрый поиск выбросов: Box plot": """\
plt.figure(figsize=(7, 4))
sns.boxplot(data=df, x="category", y="price", hue="category", palette="Set2", legend=False)
plt.tight_layout()
plt.show()
if px is not None:
    px.box(df, x="category", y="price", points="all")
""",
    "Сравнение распределений: Violin plot": """\
plt.figure(figsize=(7, 4))
sns.violinplot(data=df, x="city", y="income", hue="city", palette="muted", legend=False)
plt.tight_layout()
plt.show()
if px is not None:
    px.violin(df, x="city", y="income", box=True, points="outliers")
""",
    "Связь двух непрерывных признаков: Scatter и marginal distributions": """\
plt.figure(figsize=(6, 4))
sns.scatterplot(data=df, x="area", y="price", hue="city")
plt.tight_layout()
plt.show()
sns.jointplot(data=df, x="area", y="price", kind="scatter", height=5)
plt.show()
""",
    "Пропуски в данных: missingno": """\
df_miss = df.copy()
if msno is None:
    print("missingno не установлен — матрица через pandas:")
    print(df_miss.isna().sum())
else:
    msno.matrix(df_miss)
    plt.show()
""",
    "Мультиколлинеарность: Heatmap корреляций": """\
num = df[["area", "price", "income"]].dropna()
plt.figure(figsize=(4, 3))
sns.heatmap(num.corr(), annot=True, cmap="coolwarm", center=0)
plt.tight_layout()
plt.show()
if px is not None:
    px.imshow(num.corr(), text_auto=".2f", color_continuous_scale="RdBu_r")
""",
    "Детектирование дрейфа данных: ECDF и overlay": """\
plt.figure(figsize=(7, 4))
sns.ecdfplot(data=train_df, x="area", hue="dataset")
plt.title("ECDF train vs test")
plt.tight_layout()
plt.show()
if px is not None:
    px.ecdf(train_df, x="area", color="dataset")
""",
    "Дисбаланс классов: Count plot": """\
plt.figure(figsize=(5, 4))
sns.countplot(data=df, x="target", hue="target", palette="Set1", legend=False)
plt.tight_layout()
plt.show()
df["target"].value_counts().plot(kind="bar")
plt.show()
""",
    "Границы решений: Decision Boundaries": """\
fig, ax = plt.subplots(figsize=(6, 5))
DecisionBoundaryDisplay.from_estimator(clf, X_clf, ax=ax, alpha=0.35)
ax.scatter(X_clf[:, 0], X_clf[:, 1], c=y_clf, cmap="coolwarm", s=18, edgecolor="white", linewidths=0.3)
plt.tight_layout()
plt.show()
""",
    "Многомерные данные: PCA, t-SNE, UMAP": """\
X_high = np.c_[X_clf, rng.normal(0, 0.5, (len(X_clf), 3))]
pca2 = PCA(n_components=2, random_state=42).fit_transform(X_high)
tsne2 = TSNE(n_components=2, random_state=42, perplexity=30).fit_transform(X_high)
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].scatter(pca2[:, 0], pca2[:, 1], c=y_clf, cmap="coolwarm", s=20)
axes[0].set_title("PCA")
axes[1].scatter(tsne2[:, 0], tsne2[:, 1], c=y_clf, cmap="coolwarm", s=20)
axes[1].set_title("t-SNE")
plt.tight_layout()
plt.show()
if px is not None:
    px.scatter_3d(x=pca[:, 0], y=pca[:, 1], z=pca[:, 2], color=y_clf)
""",
    "Кластеризация: Silhouette plot и Elbow method": """\
X_blob, _ = make_blobs(n_samples=180, centers=3, random_state=42)
inertias, silhouettes = [], []
K_range = range(2, 7)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_blob)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_blob, labels))
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.plot(list(K_range), inertias, "o-")
ax1.set_title("Elbow (WCSS)")
ax2.plot(list(K_range), silhouettes, "o-")
ax2.set_title("Silhouette score")
plt.tight_layout()
plt.show()
""",
    "Диагностика регрессии: Residual plot": """\
plt.figure(figsize=(6, 4))
sns.residplot(x=y_pred, y=residuals, lowess=True, line_kws={"color": "crimson"})
plt.xlabel("предсказание")
plt.ylabel("остаток")
plt.tight_layout()
plt.show()
if px is not None:
    px.scatter(x=y_pred, y=residuals, trendline="lowess")
""",
    "Нормальность остатков: Q-Q plot": """\
fig, ax = plt.subplots(figsize=(5, 4))
stats.probplot(residuals, dist="norm", plot=ax)
ax.set_title("Q-Q plot остатков")
plt.tight_layout()
plt.show()
""",
    "Предсказание vs реальность": """\
fig, ax = plt.subplots(figsize=(6, 4))
sns.scatterplot(x=y_true, y=y_pred, ax=ax)
lims = [min(y_true.min(), y_pred.min()), max(y_true.max(), y_pred.max())]
ax.plot(lims, lims, "r--", lw=1)
ax.set_title(f"R2={r2:.2f}, RMSE={rmse:.2f}")
plt.tight_layout()
plt.show()
""",
    "Диагностика классификации: Confusion Matrix": """\
fig, ax = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay.from_estimator(clf, X_test, y_test, ax=ax, cmap="Blues")
plt.tight_layout()
plt.show()
""",
    "Качество при разных порогах: ROC и PR кривые": """\
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
RocCurveDisplay.from_estimator(clf, X_test, y_test, ax=axes[0])
PrecisionRecallDisplay.from_estimator(clf, X_test, y_test, ax=axes[1])
plt.tight_layout()
plt.show()
if px is not None:
    px.line(x=fpr, y=tpr, labels={"x": "FPR", "y": "TPR"}, title="ROC (plotly)")
""",
    "Переобучение vs недообучение: Learning Curve": """\
fig, ax = plt.subplots(figsize=(6, 4))
LearningCurveDisplay.from_estimator(
    DecisionTreeClassifier(max_depth=6, random_state=42),
    X_clf,
    y_clf,
    cv=3,
    ax=ax,
)
plt.tight_layout()
plt.show()
""",
    "Кросс-валидация: стабильность модели": """\
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
sns.boxplot(data=cv_scores, x="fold", y="score", hue="fold", ax=axes[0], legend=False)
axes[1].plot(cv_scores["score"].to_numpy(), marker="o")
axes[1].set_title("CV scores по фолдам")
plt.tight_layout()
plt.show()
""",
    "Подбор гиперпараметров: Grid Search visualization": """\
plt.figure(figsize=(5, 4))
sns.heatmap(grid_results, annot=True, fmt=".2f", cmap="viridis")
plt.title("GridSearchCV heatmap")
plt.tight_layout()
plt.show()
if px is not None:
    px.imshow(grid_results, text_auto=".2f")
""",
    "Важность признаков: Permutation Importance": """\
fig, ax = plt.subplots(figsize=(6, 3))
ax.barh(perm_y, perm_x, xerr=perm_std, color="steelblue", alpha=0.85)
ax.set_yticks(perm_y)
ax.set_yticklabels(feature_names)
ax.set_xlabel("permutation importance")
plt.tight_layout()
plt.show()
""",
    "Стили и темы: единый дизайн для проекта": """\
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_theme(style="whitegrid", palette="husl")
fig, ax = plt.subplots(figsize=(5, 3))
sns.scatterplot(data=df.head(60), x="area", y="price", hue="city", ax=ax)
plt.tight_layout()
plt.show()
""",
    "Общие техники: overlay и комбинирование графиков": """\
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].hist(train_arr, alpha=0.5, label="train", bins=20, color="steelblue")
axes[0].hist(test_arr, alpha=0.5, label="test", bins=20, color="darkorange")
axes[0].legend()
axes[1].plot(train_scores, label="train")
axes[1].plot(val_scores, label="val")
axes[1].legend()
plt.tight_layout()
plt.show()
""",
    "Размер и DPI: подготовка для разных целей": """\
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot([1, 2, 3], [1, 3, 2])
out = _OUT / "export_dpi300.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
print("saved", out, "size_kb", round(out.stat().st_size / 1024, 1))
plt.close(fig)
""",
    "Антипаттерны и best practices": """\
vals = [40, 25, 20, 15]
labels = ["A", "B", "C", "D"]
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].pie(vals, labels=labels, autopct="%1.0f%%")
axes[0].set_title("pie (антипаттерн)")
axes[1].bar(labels, vals, color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
axes[1].set_title("bar (лучше)")
plt.tight_layout()
plt.show()
""",
    "Итоговый чек-лист: какой график для какой задачи": """\
checklist = [
    ("распределение", "hist + KDE"),
    ("выбросы", "box plot"),
    ("дрейф", "overlay / ECDF"),
    ("регрессия", "residuals, Q-Q"),
    ("классификация", "confusion matrix, ROC"),
    ("важность", "permutation importance"),
]
for task, chart in checklist:
    print(f"{task:20s} -> {chart}")
""",
}


def _strip_magic(source: str) -> str:
    lines = []
    for line in source.splitlines():
        s = line.strip()
        if s.startswith("%") or s.startswith("!"):
            continue
        lines.append(line)
    return "\n".join(lines)


def build_sections(slides: list[dict]) -> list[dict]:
    selected = select_slides_for_notebook(slides)
    sections: list[dict] = []
    missing: list[str] = []
    for _idx, slide, cfg in selected:
        title = slide["title"]
        code = SECTION_CODE.get(title)
        if not code:
            missing.append(title)
            continue
        sections.append(
            {
                "slide_title": title,
                "kind": cfg.get("kinds", ["example"])[0],
                "cells": [{"type": "code", "source": code}],
            }
        )
    if missing:
        raise KeyError(f"Нет кода для секций: {missing}")
    return sections


def build_notebook(slides: list[dict]) -> dict:
    sections = build_sections(slides)
    nb = build_ipynb(sections, topic="Визуализация", consolidate=False)
    intro = (
        "# Визуализация\n\n"
        "Практические ячейки к слайдам презентации. Заголовки секций совпадают с заголовками слайдов.\n\n"
        "**Сначала выполните ячейку Setup**, затем секции по порядку (или **Kernel → Restart & Run All**).\n"
    )
    for cell in nb["cells"]:
        if cell.get("cell_type") == "markdown" and cell["source"][0].startswith("# Визуализация"):
            cell["source"] = [intro]
            break
    for cell in nb["cells"]:
        if cell.get("cell_type") == "code" and "".join(cell.get("source", [])).lstrip().startswith("# Setup"):
            cell["source"] = [line + "\n" for line in SETUP_CELL.split("\n")]
            break
    return nb


def execute_notebook(nb: dict) -> list[str]:
    import matplotlib
    import matplotlib.pyplot as plt
    import os

    matplotlib.use("Agg")
    os.chdir(LESSON)
    errors: list[str] = []
    ns: dict = {"__name__": "__main__"}
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        src = _strip_magic("".join(cell.get("source", [])))
        if not src.strip():
            continue
        try:
            exec(compile(src, f"<code.ipynb:{i}>", "exec"), ns)  # noqa: S102
            plt.close("all")
        except Exception:
            errors.append(f"cell {i}:\n{traceback.format_exc()}")
    return errors


def main() -> None:
    slides = read_slides(LESSON / "slides_json")
    nb = build_notebook(slides)
    out = LESSON / "code.ipynb"
    save_ipynb(out, nb)
    print(f"Saved {out}: {len(nb['cells'])} cells")

    errors = execute_notebook(nb)
    if errors:
        print("EXECUTION ERRORS:")
        for e in errors:
            print(e)
        sys.exit(1)
    print("All code cells executed OK")


if __name__ == "__main__":
    main()
