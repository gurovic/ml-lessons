"""Сборка project.ipynb для уроков с готовым материалом."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents"))
from notebook_utils import build_ipynb, save_ipynb  # noqa: E402


def _sections_linear() -> list[dict]:
    return [
        {
            "slide_title": "Постановка задачи",
            "kind": "intro",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Предскажем **медианную стоимость жилья** в Калифорнии "
                        "(OpenML `california_housing`) по демографическим и географическим признакам.\n\n"
                        "В одном сценарии пройдём: EDA → выбросы → train/test → Pipeline → "
                        "регуляризация → метрики → диагностика остатков → интерпретация весов."
                    ),
                }
            ],
        },
        {
            "slide_title": "Загрузка данных и первичный осмотр",
            "kind": "eda",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Целевая переменная — `median_house_value` ($). Числовые признаки: доход, возраст домов, комнаты, население, координаты.",
                },
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

np.random.seed(42)
sns.set_theme(style="whitegrid", font_scale=1.05)

raw = fetch_openml(name="california_housing", version=1, as_frame=True, parser="auto")
df = raw.frame.copy()
target_col = "median_house_value"
feature_cols = [c for c in df.columns if c not in (target_col, "ocean_proximity")]
df[feature_cols] = df[feature_cols].fillna(df[feature_cols].median())

print(f"Объектов: {len(df)}, признаков: {len(feature_cols)}")
display(df.head())
display(df.describe().round(2))
""",
                },
            ],
        },
        {
            "slide_title": "Разведочный анализ",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Сильнейший линейный сигнал — `median_income`. Корреляции подскажут мультиколлинеарность (`total_rooms` ↔ `total_bedrooms`).",
                },
                {
                    "type": "code",
                    "source": """\
fig, axes = plt.subplots(1, 3, figsize=(14, 4))

axes[0].hist(df[target_col], bins=40, color="steelblue", edgecolor="white")
axes[0].set_xlabel("median_house_value")
axes[0].set_title("Распределение цены")

axes[1].scatter(df["median_income"], df[target_col], alpha=0.25, s=12, color="steelblue")
axes[1].set_xlabel("median_income")
axes[1].set_ylabel("median_house_value")
axes[1].set_title("Цена vs доход")

corr = df[feature_cols + [target_col]].corr()
sns.heatmap(corr, ax=axes[2], cmap="RdBu_r", center=0, vmin=-1, vmax=1)
axes[2].set_title("Корреляции")
plt.tight_layout()
plt.show()

print("Корр. total_rooms–total_bedrooms:", corr.loc["total_rooms", "total_bedrooms"].round(3))
print("Корр. median_income–цена:", corr.loc["median_income", target_col].round(3))
""",
                },
            ],
        },
        {
            "slide_title": "Выбросы и рычаг",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": "MSE сильно тянется к выбросам в **Y**. Точки с экстремальным **X** (leverage) меняют наклон даже при нормальном Y.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.linear_model import LinearRegression, HuberRegressor

X1 = df[["median_income"]].values
y = df[target_col].values

# выброс в Y
y_out = y.copy()
out_y_idx = int(np.argmax(y))
y_out[out_y_idx] = y.max() * 1.8

ols_clean = LinearRegression().fit(X1, y)
ols_out = LinearRegression().fit(X1, y_out)
huber_out = HuberRegressor().fit(X1, y_out)

x_plot = np.linspace(X1.min(), X1.max(), 200).reshape(-1, 1)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].scatter(X1, y, alpha=0.3, s=10, label="данные")
axes[0].scatter(X1[out_y_idx], y_out[out_y_idx], color="orange", s=80, label="выброс Y", zorder=5)
axes[0].plot(x_plot, ols_clean.predict(x_plot), "g--", label="OLS без выброса")
axes[0].plot(x_plot, ols_out.predict(x_plot), "r-", label="OLS с выбросом")
axes[0].plot(x_plot, huber_out.predict(x_plot), "b:", linewidth=2, label="Huber")
axes[0].set_xlabel("median_income")
axes[0].set_ylabel("median_house_value")
axes[0].set_title("Выброс в целевой переменной")
axes[0].legend(fontsize=8)

# leverage: экстремальный median_income при типичном Y
X_lev = np.vstack([X1, [[X1.max() * 1.15]]])
y_lev = np.append(y, np.median(y))
ols_lev = LinearRegression().fit(X_lev, y_lev)
x_plot2 = np.linspace(X1.min(), X_lev.max(), 200).reshape(-1, 1)
axes[1].scatter(X1, y, alpha=0.3, s=10)
axes[1].scatter(X_lev[-1], y_lev[-1], color="purple", s=80, label="leverage X", zorder=5)
axes[1].plot(x_plot, ols_clean.predict(x_plot), "g--", label="OLS исходные")
axes[1].plot(x_plot2, ols_lev.predict(x_plot2), "r-", label="OLS + leverage")
axes[1].set_xlabel("MedInc")
axes[1].set_title("Выброс по оси X (рычаг)")
axes[1].legend(fontsize=8)
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Train / test и Pipeline без утечки",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "`StandardScaler` обучаем **только на train**. Иначе статистики test «протекают» в обучение.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

X = df[feature_cols].values
y = df[target_col].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

pipe_ols = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LinearRegression()),
])
pipe_ols.fit(X_train, y_train)
y_pred = pipe_ols.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)

print(f"Test MAE:  {mae:,.0f} ($)")
print(f"Test RMSE: {rmse:.3f}")
print(f"Test R2:   {r2:.3f}")
""",
                },
            ],
        },
        {
            "slide_title": "Регуляризация: Ridge и Lasso",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Ridge (L2) сжимает веса при мультиколлинеарности. Lasso (L1) может обнулять слабые признаки.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.linear_model import Ridge, Lasso

models = {
    "OLS": Pipeline([("scaler", StandardScaler()), ("model", LinearRegression())]),
    "Ridge": Pipeline([("scaler", StandardScaler()), ("model", Ridge(alpha=1.0))]),
    "Lasso": Pipeline([("scaler", StandardScaler()), ("model", Lasso(alpha=0.01, max_iter=10000))]),
}

rows = []
coef_rows = []
for name, pipe in models.items():
    pipe.fit(X_train, y_train)
    pred_tr = pipe.predict(X_train)
    pred_te = pipe.predict(X_test)
    reg = pipe.named_steps["model"]
    w = reg.coef_
    rows.append({
        "model": name,
        "R2 train": r2_score(y_train, pred_tr),
        "R2 test": r2_score(y_test, pred_te),
        "RMSE test": mean_squared_error(y_test, pred_te) ** 0.5,
        "norm_w": np.linalg.norm(w),
    })
    for fname, wi in zip(feature_cols, w):
        coef_rows.append({"model": name, "feature": fname, "weight": wi})

metrics_df = pd.DataFrame(rows)
display(metrics_df.round(4))

coef_df = pd.DataFrame(coef_rows)
fig, ax = plt.subplots(figsize=(10, 5))
for i, name in enumerate(models):
    sub = coef_df[coef_df["model"] == name]
    ax.bar(np.arange(len(feature_cols)) + i * 0.25, sub["weight"], width=0.25, label=name)
ax.set_xticks(np.arange(len(feature_cols)) + 0.25)
ax.set_xticklabels(feature_cols, rotation=45, ha="right")
ax.axhline(0, color="k", linewidth=0.5)
ax.set_ylabel("вес (после StandardScaler)")
ax.set_title("Сравнение весов OLS / Ridge / Lasso")
ax.legend()
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Диагностика остатков",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Идеал — случайное облако вокруг нуля. «Воронка» или U-образный паттерн намекают на нелинейность или пропущенные признаки.",
                },
                {
                    "type": "code",
                    "source": """\
pipe_ols.fit(X_train, y_train)
y_hat = pipe_ols.predict(X_test)
residuals = y_test - y_hat

fig, axes = plt.subplots(1, 2, figsize=(11, 4))

axes[0].scatter(y_hat, residuals, alpha=0.35, s=15, color="steelblue")
axes[0].axhline(0, color="crimson", linestyle="--")
axes[0].set_xlabel("предсказание ŷ")
axes[0].set_ylabel("остаток y − ŷ")
axes[0].set_title("Residual plot")

axes[1].hist(residuals, bins=35, color="steelblue", edgecolor="white")
axes[1].set_xlabel("остаток")
axes[1].set_title("Гистограмма остатков")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Интерпретация весов",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": "После масштабирования сравниваем силу признаков. Помним **ceteris paribus**: вес — не причинно-следственный эффект при коррелированных фичах.",
                },
                {
                    "type": "code",
                    "source": """\
w = pipe_ols.named_steps["model"].coef_
order = np.argsort(np.abs(w))

plt.figure(figsize=(8, 5))
plt.barh(np.array(feature_cols)[order], w[order], color="steelblue")
plt.xlabel("вес (StandardScaler → LinearRegression)")
plt.title("Интерпретация: влияние признаков на median_house_value")
plt.tight_layout()
plt.show()

for name, val in sorted(zip(feature_cols, w), key=lambda t: abs(t[1]), reverse=True)[:4]:
    print(f"{name:12s}: {val:+.3f}")
""",
                },
            ],
        },
        {
            "slide_title": "Когда линейная модель не хватает",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Зависимость `median_income` → цена слегка нелинейна на хвостах. Полиномиальный признак может улучшить fit — ценой интерпретируемости.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.preprocessing import PolynomialFeatures
from sklearn.compose import ColumnTransformer

inc_idx = feature_cols.index("median_income")
poly_pipe = Pipeline([
    ("prep", ColumnTransformer([
        ("poly_inc", PolynomialFeatures(degree=2, include_bias=False), [inc_idx]),
        ("rest", "passthrough", [i for i in range(len(feature_cols)) if i != inc_idx]),
    ])),
    ("scaler", StandardScaler()),
    ("model", LinearRegression()),
])

for name, pipe in [("Linear", pipe_ols), ("Poly income^2", poly_pipe)]:
    pipe.fit(X_train, y_train)
    r2_tr = r2_score(y_train, pipe.predict(X_train))
    r2_te = r2_score(y_test, pipe.predict(X_test))
    print(f"{name:14s} R2 train={r2_tr:.3f}  test={r2_te:.3f}  delta={r2_tr - r2_te:.3f}")
""",
                },
            ],
        },
        {
            "slide_title": "Чек-лист мини-проекта",
            "kind": "summary",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "1. EDA и scatter до обучения.\n"
                        "2. `train_test_split` до любой трансформации.\n"
                        "3. `Pipeline` + `StandardScaler` для интерпретации и регуляризации.\n"
                        "4. Сравнить OLS / Ridge / Lasso по test RMSE и норме весов.\n"
                        "5. Residual plot — адекватность модели.\n"
                        "6. Интерпретация весов только на масштабированных признаках.\n"
                        "7. Если R2 train >> R2 test — переобучение; если паттерн в остатках — нелинейность."
                    ),
                }
            ],
        },
    ]


def _sections_logistic() -> list[dict]:
    return [
        {
            "slide_title": "Постановка задачи",
            "kind": "intro",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Два реальных сценария:\n\n"
                        "1. **Breast Cancer Wisconsin** — сбалансированная бинарная классификация: "
                        "Pipeline, регуляризация `C`, ROC/PR, калибровка.\n"
                        "2. **German Credit (OpenML)** — дисбаланс классов: ловушка Accuracy, "
                        "`class_weight`, PR-кривая и порог."
                    ),
                }
            ],
        },
        {
            "slide_title": "Часть 1 — данные Breast Cancer",
            "kind": "eda",
            "cells": [
                {
                    "type": "markdown",
                    "source": "30 числовых признаков измерений опухоли. Класс 0 — злокачественная, 1 — доброкачественная (sklearn encoding).",
                },
                {
                    "type": "code",
                    "source": """\
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    RocCurveDisplay, PrecisionRecallDisplay,
    classification_report, ConfusionMatrixDisplay,
)

np.random.seed(42)
sns.set_theme(style="whitegrid", font_scale=1.05)

bc = load_breast_cancer(as_frame=True)
X_bc = bc.data
y_bc = bc.target
feature_names_bc = bc.feature_names

print("Размер:", X_bc.shape)
print("Баланс классов:\\n", y_bc.value_counts(normalize=True).round(3))
display(X_bc.describe().iloc[:4].round(2))
""",
                },
            ],
        },
        {
            "slide_title": "Baseline: Pipeline и predict_proba",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "LogReg чувствительна к масштабу из-за L2-штрафа. Главный выход — **вероятности**, не только метки.",
                },
                {
                    "type": "code",
                    "source": """\
X_train, X_test, y_train, y_test = train_test_split(
    X_bc, y_bc, test_size=0.25, random_state=42, stratify=y_bc
)

pipe = make_pipeline(
    StandardScaler(),
    LogisticRegression(C=1.0, max_iter=2000, random_state=42),
)
pipe.fit(X_train, y_train)

proba = pipe.predict_proba(X_test)[:, 1]
pred = pipe.predict(X_test)

print(classification_report(y_test, pred, target_names=bc.target_names, digits=3))

fig, ax = plt.subplots(figsize=(4, 4))
ConfusionMatrixDisplay.from_predictions(y_test, pred, ax=ax, cmap="Blues")
ax.set_title("Confusion matrix (порог 0.5)")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Регуляризация: параметр C",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Большое `C` — слабая регуляризация (крупные веса). Малое `C` — сильное сжатие.",
                },
                {
                    "type": "code",
                    "source": """\
C_values = [0.01, 0.1, 1.0, 10.0, 100.0]
rows = []
for C in C_values:
    m = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=2000, random_state=42))
    m.fit(X_train, y_train)
    lr = m.named_steps["logisticregression"]
    rows.append({
        "C": C,
        "accuracy test": m.score(X_test, y_test),
        "norm_w": float(np.linalg.norm(lr.coef_)),
        "max_abs_w": float(np.max(np.abs(lr.coef_))),
    })

display(pd.DataFrame(rows).round(4))
""",
                },
            ],
        },
        {
            "slide_title": "ROC, PR и калибровка",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": "На сбалансированных данных ROC информативна. Reliability diagram проверяет, совпадают ли вероятности с частотами.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.calibration import calibration_curve

pipe.fit(X_train, y_train)
proba = pipe.predict_proba(X_test)[:, 1]

fig, axes = plt.subplots(1, 3, figsize=(14, 4))

RocCurveDisplay.from_predictions(y_test, proba, ax=axes[0])
axes[0].set_title("ROC")

PrecisionRecallDisplay.from_predictions(y_test, proba, ax=axes[1])
axes[1].set_title("PR (сбалансировано)")

frac_pos, mean_pred = calibration_curve(y_test, proba, n_bins=8, strategy="uniform")
axes[2].plot([0, 1], [0, 1], "k--", label="идеал")
axes[2].plot(mean_pred, frac_pos, "o-", color="crimson", label="LogReg")
axes[2].set_xlabel("средняя P(y=1)")
axes[2].set_ylabel("доля класса 1")
axes[2].set_title("Калибровка")
axes[2].legend()
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Интерпретация: odds и log-odds",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Линейная комбинация $z = w·x + b$ — log-odds. Увеличение признака на 1 умножает odds на $e^{w_j}$ (при прочих равных).",
                },
                {
                    "type": "code",
                    "source": """\
lr = pipe.named_steps["logisticregression"]
w = lr.coef_.ravel()
top_idx = np.argsort(np.abs(w))[-8:]

plt.figure(figsize=(8, 4))
plt.barh(np.array(feature_names_bc)[top_idx], w[top_idx], color="steelblue")
plt.xlabel("вес (log-odds, после scaler)")
plt.title("Топ-8 признаков по |w|")
plt.tight_layout()
plt.show()

j = top_idx[-1]
print(f"Признак: {feature_names_bc[j]}")
print(f"  w = {w[j]:+.3f} -> odds x {np.exp(w[j]):.2f} при +1 sigma после scaler")
""",
                },
            ],
        },
        {
            "slide_title": "Часть 2 — German Credit: дисбаланс",
            "kind": "eda",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Кредитная история: класс «плохой» клиент встречается реже. Accuracy может обмануть.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.datasets import fetch_openml

credit = fetch_openml("credit-g", version=1, as_frame=True, parser="auto")
df_cr = credit.frame
y_cr = (df_cr["class"] == "bad").astype(int)
X_cr = pd.get_dummies(df_cr.drop(columns=["class"]), drop_first=True)

print("Размер:", X_cr.shape)
print("Доля 'bad':", y_cr.mean().round(3))

fig, ax = plt.subplots(figsize=(4, 3))
y_cr.value_counts().plot(kind="bar", ax=ax, color=["steelblue", "crimson"])
ax.set_xticklabels(["good (0)", "bad (1)"], rotation=0)
ax.set_title("Несбалансированные классы")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Ловушка Accuracy и class_weight",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Модель «всегда good» даёт высокий accuracy. `class_weight='balanced'` усиливает штраф за ошибки на минорном классе.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.dummy import DummyClassifier

X_tr, X_te, y_tr, y_te = train_test_split(
    X_cr, y_cr, test_size=0.3, random_state=42, stratify=y_cr
)

dummy = DummyClassifier(strategy="most_frequent")
dummy.fit(X_tr, y_tr)
print(f"Dummy accuracy: {dummy.score(X_te, y_te):.3f}\\n")

for cw, label in [(None, "без весов"), ("balanced", "balanced")]:
    m = make_pipeline(
        StandardScaler(),
        LogisticRegression(class_weight=cw, max_iter=2000, random_state=42),
    )
    m.fit(X_tr, y_tr)
    y_pred = m.predict(X_te)
    print(f"--- {label} ---")
    print(classification_report(y_te, y_pred, target_names=["good", "bad"], digits=3))
""",
                },
            ],
        },
        {
            "slide_title": "PR-кривая и выбор порога",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": "При дисбалансе смотрим **PR-AUC**. Порог 0.5 не обязан быть оптимальным — сдвигаем по PR-кривой.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.metrics import precision_recall_curve, average_precision_score

m = make_pipeline(
    StandardScaler(),
    LogisticRegression(class_weight="balanced", max_iter=2000, random_state=42),
)
m.fit(X_tr, y_tr)
proba_cr = m.predict_proba(X_te)[:, 1]

prec, rec, thresholds = precision_recall_curve(y_te, proba_cr)
ap = average_precision_score(y_te, proba_cr)

from sklearn.metrics import precision_score, recall_score

fig, axes = plt.subplots(1, 2, figsize=(11, 4))

PrecisionRecallDisplay.from_predictions(y_te, proba_cr, ax=axes[0])
axes[0].set_title(f"PR-кривая (AP={ap:.3f})")

rows_thr = []
for thr in [0.5, 0.35, 0.25]:
    y_p = (proba_cr >= thr).astype(int)
    rows_thr.append({
        "threshold": thr,
        "precision": precision_score(y_te, y_p, zero_division=0),
        "recall": recall_score(y_te, y_p, zero_division=0),
    })
thr_df = pd.DataFrame(rows_thr)
x = np.arange(len(thr_df))
w = 0.35
axes[1].bar(x - w / 2, thr_df["precision"], width=w, label="precision")
axes[1].bar(x + w / 2, thr_df["recall"], width=w, label="recall")
axes[1].set_xticks(x)
axes[1].set_xticklabels([str(t) for t in thr_df["threshold"]])
axes[1].set_xlabel("порог")
axes[1].set_title("Precision / Recall vs порог")
axes[1].legend()
plt.tight_layout()
plt.show()
display(thr_df.round(3))
""",
                },
            ],
        },
        {
            "slide_title": "Ограничение: линейная граница",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": "LogReg — один нейрон с сигмоидой. На XOR-подобных данных линейная граница не справляется.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.datasets import make_classification

X_xor, _ = make_classification(
    n_samples=200, n_features=2, n_redundant=0, n_informative=2,
    n_clusters_per_class=1, class_sep=1.0, random_state=42,
)
y_xor = ((X_xor[:, 0] > 0) ^ (X_xor[:, 1] > 0)).astype(int)

m_xor = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500, random_state=42))
m_xor.fit(X_xor, y_xor)

xx, yy = np.meshgrid(
    np.linspace(X_xor[:, 0].min() - 0.5, X_xor[:, 0].max() + 0.5, 200),
    np.linspace(X_xor[:, 1].min() - 0.5, X_xor[:, 1].max() + 0.5, 200),
)
Z = m_xor.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1].reshape(xx.shape)

plt.figure(figsize=(5, 4))
plt.contourf(xx, yy, Z, levels=20, cmap="RdBu", alpha=0.7)
plt.colorbar(label="P(y=1)")
plt.scatter(X_xor[y_xor == 0, 0], X_xor[y_xor == 0, 1], c="blue", edgecolors="k", s=40)
plt.scatter(X_xor[y_xor == 1, 0], X_xor[y_xor == 1, 1], c="red", edgecolors="k", s=40)
plt.title(f"XOR: accuracy={m_xor.score(X_xor, y_xor):.2f}")
plt.xlabel("x₁")
plt.ylabel("x₂")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Чек-лист мини-проекта",
            "kind": "summary",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "1. LogReg — базлайн для табличной классификации.\n"
                        "2. Всегда `Pipeline` + `StandardScaler`.\n"
                        "3. Смотреть `predict_proba`, не только accuracy.\n"
                        "4. При дисбалансе — PR-кривая, `class_weight`, подбор порога.\n"
                        "5. Калибровка: reliability diagram на hold-out.\n"
                        "6. Интерпретация через log-odds / odds.\n"
                        "7. Линейная граница — ограничение; для XOR нужны признаки или другие модели."
                    ),
                }
            ],
        },
    ]


def _sections_derevo() -> list[dict]:
    return [
        {
            "slide_title": "Постановка задачи",
            "kind": "intro",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Классифицируем **сорта вина** по химическому составу "
                        "(sklearn `load_wine`, 3 класса, 13 признаков).\n\n"
                        "Пройдём: EDA → train/test → `DecisionTreeClassifier` → "
                        "Gini vs entropy → глубина и переобучение → `plot_tree` → "
                        "важность признаков → confusion matrix → `class_weight` → "
                        "подбор гиперпараметров → ограничения оси-параллельных границ."
                    ),
                }
            ],
        },
        {
            "slide_title": "Загрузка данных и первичный осмотр",
            "kind": "eda",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "13 числовых признаков (кислотность, алкоголь, фенолы…). "
                        "Деревья **не требуют масштабирования**, но пропуски нужно заполнять."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import (
    classification_report, ConfusionMatrixDisplay, accuracy_score,
)

np.random.seed(42)
sns.set_theme(style="whitegrid", font_scale=1.05)

wine = load_wine(as_frame=True)
df = wine.frame.copy()
target_col = "target"
feature_cols = list(wine.feature_names)
class_names = list(wine.target_names)

print(f"Объектов: {len(df)}, признаков: {len(feature_cols)}, классов: {df[target_col].nunique()}")
display(df.head())
display(df.describe().round(2))
""",
                },
            ],
        },
        {
            "slide_title": "Разведочный анализ",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Классы умеренно сбалансированы. Пара признаков (`alcohol`, `color_intensity`) хорошо разделяет сорта — посмотрим распределения.",
                },
                {
                    "type": "code",
                    "source": """\
fig, axes = plt.subplots(1, 3, figsize=(14, 4))

counts = df[target_col].value_counts().sort_index()
axes[0].bar(class_names, counts.values, color="steelblue", edgecolor="white")
axes[0].set_title("Баланс классов")
axes[0].set_ylabel("число объектов")

for cls in sorted(df[target_col].unique()):
    sub = df[df[target_col] == cls]
    axes[1].scatter(sub["alcohol"], sub["color_intensity"], alpha=0.7, s=35, label=class_names[cls])
axes[1].set_xlabel("alcohol")
axes[1].set_ylabel("color_intensity")
axes[1].set_title("Два признака")
axes[1].legend(fontsize=8)

corr = df[feature_cols].corr()
sns.heatmap(corr.iloc[:6, :6], ax=axes[2], cmap="RdBu_r", center=0, vmin=-1, vmax=1)
axes[2].set_title("Корреляции (фрагмент)")
plt.tight_layout()
plt.show()

print("Доли классов:\\n", df[target_col].value_counts(normalize=True).round(3).rename(index=dict(enumerate(class_names))))
""",
                },
            ],
        },
        {
            "slide_title": "Train / test и базовое дерево",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Стратификация сохраняет доли классов. "
                        "`Pipeline` здесь — обёртка над моделью (без scaler: порядок признаков для дерева не важен)."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
X = df[feature_cols].values
y = df[target_col].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

pipe = Pipeline([
    ("tree", DecisionTreeClassifier(random_state=42)),
])
pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)

print(classification_report(y_test, y_pred, target_names=class_names, digits=3))
print(f"Accuracy test: {accuracy_score(y_test, y_pred):.3f}")
""",
                },
            ],
        },
        {
            "slide_title": "Критерий разбиения: Gini vs entropy",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Оба критерия строго вогнуты и учитывают все классы. На практике деревья почти совпадают.",
                },
                {
                    "type": "code",
                    "source": """\
rows = []
for crit in ("gini", "entropy"):
    m = Pipeline([("tree", DecisionTreeClassifier(criterion=crit, max_depth=5, random_state=42))])
    m.fit(X_train, y_train)
    rows.append({
        "criterion": crit,
        "accuracy train": m.score(X_train, y_train),
        "accuracy test": m.score(X_test, y_test),
        "depth": m.named_steps["tree"].get_depth(),
        "n_leaves": m.named_steps["tree"].get_n_leaves(),
    })

display(pd.DataFrame(rows).round(4))
""",
                },
            ],
        },
        {
            "slide_title": "Глубина и переобучение",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Без ограничений дерево запоминает train (accuracy → 1). На test качество сначала растёт, затем падает или стагнирует.",
                },
                {
                    "type": "code",
                    "source": """\
depths = list(range(1, 16))
train_acc, test_acc = [], []

for d in depths:
    m = DecisionTreeClassifier(max_depth=d, random_state=42)
    m.fit(X_train, y_train)
    train_acc.append(m.score(X_train, y_train))
    test_acc.append(m.score(X_test, y_test))

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(depths, train_acc, "o-", label="train", color="steelblue")
ax.plot(depths, test_acc, "s-", label="test", color="crimson")
ax.set_xlabel("max_depth")
ax.set_ylabel("accuracy")
ax.set_title("Глубина vs accuracy (переобучение)")
ax.legend()
plt.tight_layout()
plt.show()

best_d = depths[int(np.argmax(test_acc))]
print(f"Лучший max_depth на test: {best_d} (acc={max(test_acc):.3f})")

# полное дерево vs ограниченное
full = DecisionTreeClassifier(random_state=42).fit(X_train, y_train)
shallow = DecisionTreeClassifier(max_depth=best_d, random_state=42).fit(X_train, y_train)
print(f"Без ограничений: train={full.score(X_train, y_train):.3f}, test={full.score(X_test, y_test):.3f}")
print(f"max_depth={best_d}: train={shallow.score(X_train, y_train):.3f}, test={shallow.score(X_test, y_test):.3f}")
""",
                },
            ],
        },
        {
            "slide_title": "Визуализация дерева",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": "`plot_tree` показывает правила «x < порог» в каждом узле. Цвет листа — доминирующий класс.",
                },
                {
                    "type": "code",
                    "source": """\
tree_viz = DecisionTreeClassifier(max_depth=3, random_state=42)
tree_viz.fit(X_train, y_train)

fig, ax = plt.subplots(figsize=(16, 8))
plot_tree(
    tree_viz,
    feature_names=feature_cols,
    class_names=class_names,
    filled=True,
    rounded=True,
    fontsize=9,
    ax=ax,
)
ax.set_title("Decision tree (max_depth=3)")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Важность признаков",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Суммарное уменьшение неоднородности (Gini/entropy) по всем узлам, где использовался признак.",
                },
                {
                    "type": "code",
                    "source": """\
clf_imp = DecisionTreeClassifier(max_depth=5, random_state=42)
clf_imp.fit(X_train, y_train)
imp = clf_imp.feature_importances_
order = np.argsort(imp)

plt.figure(figsize=(8, 5))
plt.barh(np.array(feature_cols)[order], imp[order], color="steelblue")
plt.xlabel("feature_importances_")
plt.title("Важность признаков (max_depth=5)")
plt.tight_layout()
plt.show()

for name, val in sorted(zip(feature_cols, imp), key=lambda t: t[1], reverse=True)[:5]:
    print(f"{name:20s}: {val:.3f}")
""",
                },
            ],
        },
        {
            "slide_title": "Confusion matrix и метрики по классам",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Accuracy недостаточна при дисбалансе — смотрим precision/recall/F1 по каждому классу.",
                },
                {
                    "type": "code",
                    "source": """\
clf_best = DecisionTreeClassifier(max_depth=best_d, random_state=42)
clf_best.fit(X_train, y_train)
y_hat = clf_best.predict(X_test)

fig, ax = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay.from_predictions(
    y_test, y_hat, display_labels=class_names, cmap="Blues", ax=ax
)
ax.set_title(f"Confusion matrix (max_depth={best_d})")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "class_weight при дисбалансе",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Класс 2 (`class_2`) — минорный. `class_weight='balanced'` "
                        "увеличивает штраф за ошибки на редком классе **при построении дерева**."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
minority = int(np.argmin(np.bincount(y_train)))
minority_name = class_names[minority]
print(f"Минорный класс: {minority_name} (label={minority})\\n")

for cw, label in [(None, "без весов"), ("balanced", "balanced")]:
    m = DecisionTreeClassifier(max_depth=5, class_weight=cw, random_state=42)
    m.fit(X_train, y_train)
    rep = classification_report(y_test, m.predict(X_test), target_names=class_names, output_dict=True)
    print(f"--- {label} ---")
    print(f"  recall {minority_name}: {rep[minority_name]['recall']:.3f}")
    print(f"  macro F1: {rep['macro avg']['f1-score']:.3f}")
""",
                },
            ],
        },
        {
            "slide_title": "Подбор max_depth (GridSearchCV)",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Кросс-валидация на train подбирает глубину без «подглядывания» в test.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.model_selection import GridSearchCV

grid = GridSearchCV(
    Pipeline([("tree", DecisionTreeClassifier(random_state=42))]),
    param_grid={"tree__max_depth": [2, 3, 4, 5, 7, 10, None]},
    cv=5,
    scoring="accuracy",
    n_jobs=-1,
)
grid.fit(X_train, y_train)

print("Лучшие параметры:", grid.best_params_)
print(f"CV accuracy: {grid.best_score_:.3f}")
print(f"Test accuracy: {grid.score(X_test, y_test):.3f}")
""",
                },
            ],
        },
        {
            "slide_title": "Ограничение: оси-параллельные границы",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Дерево делит пространство прямоугольниками, параллельными осям. "
                        "Диагональную границу оно аппроксимирует «лестницей» — в отличие от линейной модели с комбинацией признаков."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

# два признака для 2D-визуализации
idx_a, idx_b = feature_cols.index("alcohol"), feature_cols.index("color_intensity")
X2 = X[:, [idx_a, idx_b]]
X2_tr, X2_te, y2_tr, y2_te = train_test_split(X2, y, test_size=0.25, random_state=42, stratify=y)

tree2 = DecisionTreeClassifier(max_depth=5, random_state=42).fit(X2_tr, y2_tr)
log2 = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=42)).fit(X2_tr, y2_tr)

xx, yy = np.meshgrid(
    np.linspace(X2[:, 0].min() - 0.5, X2[:, 0].max() + 0.5, 200),
    np.linspace(X2[:, 1].min() - 0.5, X2[:, 1].max() + 0.5, 200),
)
grid_pts = np.c_[xx.ravel(), yy.ravel()]

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, model, title in [
    (axes[0], tree2, f"Дерево (acc={tree2.score(X2_te, y2_te):.2f})"),
    (axes[1], log2, f"LogReg (acc={log2.score(X2_te, y2_te):.2f})"),
]:
    Z = model.predict(grid_pts).reshape(xx.shape)
    ax.contourf(xx, yy, Z, alpha=0.35, levels=np.arange(-0.5, 3.5, 1), cmap="tab10")
    for cls in np.unique(y):
        mask = y2_tr == cls
        ax.scatter(X2_tr[mask, 0], X2_tr[mask, 1], s=30, edgecolors="k", label=class_names[cls])
    ax.set_xlabel(feature_cols[idx_a])
    ax.set_ylabel(feature_cols[idx_b])
    ax.set_title(title)
    ax.legend(fontsize=7)
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Чек-лист мини-проекта",
            "kind": "summary",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "1. EDA и баланс классов до обучения.\n"
                        "2. `train_test_split(..., stratify=y)` для классификации.\n"
                        "3. Масштабирование дереву не нужно; пропуски — заполнить.\n"
                        "4. Сравнить `criterion='gini'` и `'entropy'`.\n"
                        "5. График depth vs accuracy — переобучение на train.\n"
                        "6. `plot_tree` + `feature_importances_` для интерпретации.\n"
                        "7. Confusion matrix и F1 по классам, не только accuracy.\n"
                        "8. При дисбалансе — `class_weight='balanced'`.\n"
                        "9. GridSearchCV / CV на train, финальная оценка на test.\n"
                        "10. Помнить про оси-параллельные границы и нестабильность одного дерева."
                    ),
                }
            ],
        },
    ]


def build_all() -> None:
    lessons = [
        (ROOT / "lessons" / "lineynaya_regressiya", "Линейная регрессия — мини-проект", _sections_linear()),
        (ROOT / "lessons" / "logisticheskaya_regressiya", "Логистическая регрессия — мини-проект", _sections_logistic()),
        (ROOT / "lessons" / "derevo_resheniy", "Дерево решений — мини-проект", _sections_derevo()),
    ]
    for lesson_dir, topic, sections in lessons:
        nb = build_ipynb(sections, topic=topic)
        # заменить заголовок первой ячейки на project-стиль
        nb["cells"][0]["source"] = [
            f"# {topic}\n",
            "\n",
            "Сквозной мини-проект на реальных данных. "
            "Повторяет ключевые темы урока в одном пайплайне.\n",
        ]
        out = lesson_dir / "project.ipynb"
        save_ipynb(out, nb)
        print(f"Saved {out} ({len(sections)} sections, {len(nb['cells'])} cells)")


if __name__ == "__main__":
    build_all()
