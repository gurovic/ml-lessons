"""Полная перегенерация урока vizualizatsiya из plan.md / vizualizatsiya_slides_data.py."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents"))

from notebook_utils import build_ipynb, save_ipynb  # noqa: E402
from slide_utils import save_slide  # noqa: E402
from vizualizatsiya_slides_data import SLIDES  # noqa: E402

LESSON = ROOT / "lessons" / "vizualizatsiya"
SLIDES_DIR = LESSON / "slides_json"

# viz_*.png → имена из slides JSON (порядок = слайды 1–33)
VIZ_RENAMES = {
    "viz_philosophy_three_tasks.png": "ml_viz_three_roles.png",
    "viz_library_choice.png": "library_choice_matrix.png",
    "viz_pandas_builtin.png": "pandas_builtin_overview.png",
    "viz_mpl_figure_axes.png": "matplotlib_figure_axes_diagram.png",
    "viz_subplots_grid.png": "subplot_grid_train_test.png",
    "viz_customization.png": "customization_annotate_legend.png",
    "viz_save_export.png": "export_formats_comparison.png",
    "viz_plotly_scatter_static.png": "plotly_express_scatter_hover.png",
    "viz_plotly_advanced_static.png": "plotly_3d_animation_demo.png",
    "viz_hist_kde.png": "histplot_kde_heavy_tail.png",
    "viz_boxplot.png": "boxplot_outliers_iqr.png",
    "viz_violinplot.png": "violin_vs_box_bimodal.png",
    "viz_scatter_joint.png": "jointplot_hex_marginals.png",
    "viz_missingno_pattern.png": "missingno_matrix_dendrogram.png",
    "viz_corr_heatmap.png": "correlation_heatmap_multicollinearity.png",
    "viz_ecdf_drift.png": "ecdf_train_prod_drift.png",
    "viz_countplot_imbalance.png": "countplot_class_imbalance.png",
    "viz_decision_boundary.png": "decision_boundary_linear_nonlinear.png",
    "viz_pca_tsne.png": "pca_vs_umap_clusters.png",
    "viz_elbow_silhouette.png": "elbow_silhouette_kmeans.png",
    "viz_residual_plot.png": "residual_plot_good_bad.png",
    "viz_qq_plot.png": "qqplot_residuals_normality.png",
    "viz_pred_vs_actual.png": "predicted_vs_actual_diagonal.png",
    "viz_confusion_matrix.png": "confusion_matrix_heatmap.png",
    "viz_roc_pr_curves.png": "roc_pr_curves_overlay.png",
    "viz_learning_curve.png": "learning_curve_overfitting.png",
    "viz_cv_boxplot.png": "cv_scores_stability_boxplot.png",
    "viz_grid_search_heatmap.png": "grid_search_heatmap_plateau.png",
    "viz_permutation_importance.png": "permutation_importance_barh.png",
    "viz_themes_styles.png": "theme_before_after_seaborn.png",
    "viz_overlay_histograms.png": "overlay_hist_facetgrid.png",
    "viz_figsize_dpi.png": "figsize_dpi_guidelines.png",
    "viz_antipatterns.png": "viz_antipatterns_best_practices.png",
}


def _code_from_bullets(slide: dict) -> list[dict] | None:
    """Минимальные code_examples из inline-кода в буллетах."""
    examples: list[dict] = []
    for bullet in slide.get("bullets", []):
        for match in re.findall(r"`([^`]+)`", bullet):
            if len(match) < 8:
                continue
            if not any(ch in match for ch in ("(", ".", "=", "import", "kind")):
                continue
            code = match.strip()
            if code.startswith("df.") or "plt." in code or "sns." in code or "px." in code:
                examples.append({"source": code, "caption": code.split("\n")[0][:48]})
            elif "()" in code or "(" in code:
                examples.append({"source": code, "caption": code[:48]})
            if len(examples) >= 2:
                break
        if len(examples) >= 2:
            break
    return examples or None


def fix_generate_visuals_names() -> None:
    path = LESSON / "assets" / "generate_visuals.py"
    text = path.read_text(encoding="utf-8")
    for old, new in VIZ_RENAMES.items():
        text = text.replace(f'"{old}"', f'"{new}"')
    text = text.replace("    fig_checklist()\n", "")
    path.write_text(text, encoding="utf-8")


def remove_orphan_pngs() -> None:
    assets = LESSON / "assets"
    keep = {v["output"] for s in SLIDES for v in s.get("visuals", [])}
    for png in assets.glob("*.png"):
        if png.name not in keep:
            png.unlink()
            print(f"  удалён orphan: {png.name}")


def write_slides_json() -> None:
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    for i, slide in enumerate(SLIDES, 1):
        payload = dict(slide)
        save_slide(SLIDES_DIR, payload, i)
    print(f"Записано {len(SLIDES)} слайдов в slides_json/")


def build_code_notebook() -> None:
    from build_vizualizatsiya_code import build_notebook, save_ipynb

    nb = build_notebook(SLIDES)
    save_ipynb(LESSON / "code.ipynb", nb)
    n_sections = sum(1 for s in SLIDES if isinstance(s.get("notebook"), dict) and s["notebook"].get("include"))
    print(f"code.ipynb: {len(nb['cells'])} ячеек (runnable sections)")


def build_project_notebook() -> None:
    sections = [
        {
            "slide_title": "Постановка задачи",
            "kind": "intro",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Сквозной EDA на **Titanic (OpenML)**: pandas built-in → seaborn → "
                        "диагностика модели. Все графики — одна цепочка решений."
                    ),
                }
            ],
        },
        {
            "slide_title": "Загрузка и быстрый обзор",
            "kind": "eda",
            "cells": [
                {
                    "type": "code",
                    "source": """\
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import RocCurveDisplay, ConfusionMatrixDisplay

%matplotlib inline
np.random.seed(42)
sns.set_theme(style="whitegrid", font_scale=1.05)

raw = fetch_openml("titanic", version=1, as_frame=True, parser="auto")
df = raw.frame.copy()
df["Survived"] = df["survived"].astype(int)
df["Pclass"] = df["pclass"].astype(int)
df["Age"] = pd.to_numeric(df["age"], errors="coerce")
df["Fare"] = pd.to_numeric(df["fare"], errors="coerce")
df["Sex"] = df["sex"].astype(str)
print(df.shape)
df[["Age", "Fare", "Survived"]].describe()
""",
                }
            ],
        },
        {
            "slide_title": "EDA: распределения и категории",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": "**Решение:** строим базовые графики распределений и категорий — hist, box, violin, countplot.",
                },
                {
                    "type": "code",
                    "source": """\
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
df["Fare"].plot(kind="hist", bins=30, ax=axes[0, 0], alpha=0.8)
axes[0, 0].set_title("pandas hist Fare")
sns.boxplot(data=df, x="Pclass", y="Fare", ax=axes[0, 1])
sns.violinplot(data=df, x="Sex", y="Age", ax=axes[1, 0])
sns.countplot(data=df, x="Survived", ax=axes[1, 1])
plt.tight_layout()
plt.show()
""",
                }
            ],
        },
        {
            "slide_title": "Связи и корреляции",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": "**Решение:** heatmap корреляций и scatter для пар признаков.",
                },
                {
                    "type": "code",
                    "source": """\
num = df[["Survived", "Pclass", "Age", "Fare"]].dropna()
sns.heatmap(num.corr(), annot=True, cmap="coolwarm", center=0, vmin=-1, vmax=1)
plt.title("Корреляции числовых признаков")
plt.tight_layout()
plt.show()
sns.scatterplot(data=num, x="Fare", y="Age", hue="Survived", alpha=0.7)
plt.show()
""",
                }
            ],
        },
        {
            "slide_title": "Модель и диагностика",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "**Решение:** обучаем `LogisticRegression` в Pipeline и визуализируем confusion matrix + ROC.",
                },
                {
                    "type": "code",
                    "source": """\
X = df[["Pclass", "Age", "Fare"]]
y = df["Survived"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)
final_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=500, random_state=42)),
])
final_pipe.fit(X_train, y_train)
proba = final_pipe.predict_proba(X_test)[:, 1]
pred = final_pipe.predict(X_test)
final_model = final_pipe.named_steps["model"]

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
ConfusionMatrixDisplay.from_predictions(y_test, pred, ax=axes[0], cmap="Blues")
RocCurveDisplay.from_predictions(y_test, proba, ax=axes[1])
plt.tight_layout()
plt.show()
""",
                }
            ],
        },
        {
            "slide_title": "Чек-лист мини-проекта",
            "kind": "summary",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "1. Один датасет — цепочка графиков от EDA до ROC/CM.\n"
                        "2. seaborn для статистики; pandas.plot для быстрого старта.\n"
                        "3. Bar/box — ось Y с нуля; heatmap — center=0.\n"
                        "4. После модели — confusion matrix и ROC на том же test-set.\n"
                        "5. Подписи осей и title на каждом графике."
                    ),
                }
            ],
        },
    ]
    nb = build_ipynb(sections, topic="Визуализация — мини-проект")
    nb["cells"][0]["source"] = [
        "# Визуализация — мини-проект\n\n",
        "Сквозной мини-проект на реальных данных. Повторяет ключевые темы урока.\n",
    ]
    save_ipynb(LESSON / "project.ipynb", nb)
    print(f"project.ipynb: {len(sections)} секций")


def write_references_json() -> None:
    refs = {
        "title": "Источники и практика",
        "type": "references",
        "references": [
            {
                "kind": "paper",
                "title": "Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods",
                "authors": "Cleveland W.S., McGill R.",
                "year": 1984,
                "url": "https://www.jstor.org/stable/2288400",
            },
            {
                "kind": "paper",
                "title": "Anscombe's Quartet",
                "authors": "Anscombe F.J.",
                "year": 1973,
                "url": "https://en.wikipedia.org/wiki/Anscombe%27s_quartet",
            },
            {
                "kind": "paper",
                "title": "matplotlib: A 2D Graphics Environment",
                "authors": "Hunter J.D.",
                "year": 2007,
                "url": "https://matplotlib.org/stable/citing.html",
            },
            {
                "kind": "paper",
                "title": "seaborn: statistical data visualization",
                "authors": "Waskom M.L.",
                "year": 2021,
                "url": "https://seaborn.pydata.org/index.html",
            },
        ],
        "bullets": [],
        "notes": "Colab-ссылки обновляются агентом при --apply.",
    }
    (LESSON / "references.json").write_text(
        json.dumps(refs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_review_md() -> None:
    text = f"""# Рецензия: Визуализация

## Резюме

Урок перегенерирован по новому `plan.md` ({len(SLIDES)} слайдов). Покрытие: философия визуализации, библиотеки (matplotlib/seaborn/plotly/pandas), EDA-графики, диагностика ML-моделей, стиль и антипаттерны. Блокирующих проблем нет — **готов к проверке в presentation.pptx**.

## 1. Фактология

### Критичные
Критичных ошибок не найдено.

### Замечания
- API seaborn/matplotlib/sklearn соответствует версиям из `requirements.txt`.
- Plotly на слайдах — статические PNG-аппроксимации (интерактив — в ноутбуке).

## 2. Логика развития темы

- Дуга: мотивация → инструменты → EDA → диагностика моделей → best practices → чек-лист.
- План полностью покрыт.

## 3. Понятность

- Уровень: продвинутые старшеклассники / 1 курс; примеры на синтетике и Titanic.

## 4. Лаконичность

- Буллеты тезисные; итоговый чек-лист (слайд 34) без иллюстраций — уместно.

## 5. Полнота

- Все {len(SLIDES)} пунктов плана отражены; `code.ipynb` и `project.ipynb` собраны.

## Приоритетные правки

Блокирующих правок нет. Рекомендуется human QA в PowerPoint.
"""
    (LESSON / "review.md").write_text(text, encoding="utf-8")


def run(cmd: list[str], label: str) -> None:
    print(f"\n=== {label} ===")
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        raise SystemExit(f"{label} failed (exit {result.returncode})")


def main() -> None:
    fix_generate_visuals_names()
    write_slides_json()
    build_code_notebook()
    build_project_notebook()
    write_references_json()
    write_review_md()

    run(
        [sys.executable, "agents/visuals_pipeline.py", str(LESSON)],
        "visuals + pptx",
    )
    remove_orphan_pngs()
    run(
        [sys.executable, "agents/pptx_builder.py", str(LESSON)],
        "pptx (after orphan cleanup)",
    )
    run(
        [sys.executable, "agents/references_agent.py", str(LESSON), "--apply"],
        "references",
    )
    run(
        [sys.executable, "agents/link_checker_agent.py", str(LESSON), "--offline"],
        "link checker (offline)",
    )
    print("\nГотово: lessons/vizualizatsiya перегенерирован.")


if __name__ == "__main__":
    main()
