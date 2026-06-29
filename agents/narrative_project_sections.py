"""Narrative pipeline sections for project.ipynb (one dataset, state carries forward)."""


def sections_linear() -> list[dict]:
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
                        "**Сюжет:** загрузка → EDA → обнаружение выбросов → очистка → "
                        "один train/test split → сравнение OLS / Ridge / Lasso → выбор модели → "
                        "метрики, остатки и интерпретация весов на **одном** hold-out test."
                    ),
                }
            ],
        },
        {
            "slide_title": "Загрузка данных",
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

%matplotlib inline
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
            "slide_title": "EDA: распределения и корреляции",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Сильнейший сигнал — `median_income`. На гистограмме цены видны **хвосты** "
                        "(кандидаты в выбросы). Корреляция `total_rooms` ↔ `total_bedrooms` "
                        "намекает на мультиколлинеарность."
                    ),
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
            "slide_title": "Выбросы в целевой переменной",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "MSE сильно штрафует экстремальные значения **Y**. "
                        "Посмотрим boxplot и правило **IQR** для `median_house_value`."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
q1, q3 = df[target_col].quantile([0.25, 0.75])
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
outlier_mask = (df[target_col] < lower) | (df[target_col] > upper)

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
sns.boxplot(y=df[target_col], ax=axes[0], color="steelblue")
axes[0].set_title("Boxplot цены")
axes[0].set_ylabel("median_house_value")

axes[1].scatter(df.loc[~outlier_mask, "median_income"], df.loc[~outlier_mask, target_col],
                alpha=0.2, s=10, color="steelblue", label="норма")
axes[1].scatter(df.loc[outlier_mask, "median_income"], df.loc[outlier_mask, target_col],
                alpha=0.8, s=25, color="crimson", label="выброс IQR")
axes[1].set_xlabel("median_income")
axes[1].set_ylabel("median_house_value")
axes[1].set_title("Выбросы по IQR")
axes[1].legend(fontsize=8)
plt.tight_layout()
plt.show()

print(f"IQR-границы: [{lower:,.0f}; {upper:,.0f}]")
print(f"Выбросов: {outlier_mask.sum()} ({100 * outlier_mask.mean():.1f}%)")
""",
                },
            ],
        },
        {
            "slide_title": "Решение: очистка данных",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "**Решение:** удаляем объекты с выбросами по IQR в `median_house_value`. Дальнейшие шаги — только на `df_clean`.",
                },
                {
                    "type": "code",
                    "source": """\
df_clean = df.loc[~outlier_mask].copy().reset_index(drop=True)
print(f"Было {len(df)} → осталось {len(df_clean)} объектов")
print(f"Медиана цены: {df[target_col].median():,.0f} → {df_clean[target_col].median():,.0f}")
""",
                },
            ],
        },
        {
            "slide_title": "Решение: train / test split",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "**Решение:** один раз делим **очищенные** данные на train и test (`random_state=42`). "
                        "Этот test используем до конца ноутбука."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.model_selection import train_test_split

X = df_clean[feature_cols].values
y = df_clean[target_col].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"Train: {len(X_train)}, test: {len(X_test)}")
""",
                },
            ],
        },
        {
            "slide_title": "Baseline: OLS в Pipeline",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "`StandardScaler` обучаем **только на train** — внутри `Pipeline`, без утечки из test.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

pipe_ols = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LinearRegression()),
])
pipe_ols.fit(X_train, y_train)
y_pred_ols = pipe_ols.predict(X_test)

print(f"OLS — Test MAE:  {mean_absolute_error(y_test, y_pred_ols):,.0f}")
print(f"OLS — Test RMSE: {mean_squared_error(y_test, y_pred_ols) ** 0.5:.3f}")
print(f"OLS — Test R2:   {r2_score(y_test, y_pred_ols):.3f}")
""",
                },
            ],
        },
        {
            "slide_title": "Сравнение Ridge и Lasso",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Ridge (L2) сжимает веса при мультиколлинеарности. "
                        "Lasso (L1) может обнулять слабые признаки. Сравниваем на **том же** train/test."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.linear_model import Ridge, Lasso

candidates = {
    "OLS": Pipeline([("scaler", StandardScaler()), ("model", LinearRegression())]),
    "Ridge": Pipeline([("scaler", StandardScaler()), ("model", Ridge(alpha=1.0))]),
    "Lasso": Pipeline([("scaler", StandardScaler()), ("model", Lasso(alpha=0.01, max_iter=10000))]),
}

rows = []
for name, pipe in candidates.items():
    pipe.fit(X_train, y_train)
    pred_te = pipe.predict(X_test)
    w = pipe.named_steps["model"].coef_
    rows.append({
        "model": name,
        "R2 test": r2_score(y_test, pred_te),
        "RMSE test": mean_squared_error(y_test, pred_te) ** 0.5,
        "norm_w": np.linalg.norm(w),
    })

metrics_df = pd.DataFrame(rows).sort_values("RMSE test")
display(metrics_df.round(4))
""",
                },
            ],
        },
        {
            "slide_title": "Решение: выбор модели",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "**Решение:** берём модель с лучшим test RMSE. Дальше все метрики и графики — только для неё.",
                },
                {
                    "type": "code",
                    "source": """\
best_name = metrics_df.iloc[0]["model"]
final_pipe = candidates[best_name]
final_pipe.fit(X_train, y_train)
y_pred = final_pipe.predict(X_test)

print(f"Выбрана модель: {best_name}")
print(f"Test RMSE: {mean_squared_error(y_test, y_pred) ** 0.5:.3f}")
print(f"Test R2:   {r2_score(y_test, y_pred):.3f}")
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
                    "source": "Идеал — случайное облако вокруг нуля. Паттерн «воронки» намекает на нелинейность.",
                },
                {
                    "type": "code",
                    "source": """\
residuals = y_test - y_pred

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].scatter(y_pred, residuals, alpha=0.35, s=15, color="steelblue")
axes[0].axhline(0, color="crimson", linestyle="--")
axes[0].set_xlabel("предсказание ŷ")
axes[0].set_ylabel("остаток y − ŷ")
axes[0].set_title(f"Residual plot ({best_name})")

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
                    "source": "После масштабирования сравниваем силу признаков (**ceteris paribus** — при прочих равных).",
                },
                {
                    "type": "code",
                    "source": """\
w = final_pipe.named_steps["model"].coef_
order = np.argsort(np.abs(w))

plt.figure(figsize=(8, 5))
plt.barh(np.array(feature_cols)[order], w[order], color="steelblue")
plt.xlabel("вес (StandardScaler → модель)")
plt.title(f"Интерпретация весов ({best_name}, данные без выбросов)")
plt.tight_layout()
plt.show()

for name, val in sorted(zip(feature_cols, w), key=lambda t: abs(t[1]), reverse=True)[:4]:
    print(f"{name:12s}: {val:+.3f}")
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
                        "1. EDA → обнаружили выбросы → **удалили** → `df_clean`.\n"
                        "2. Один `train_test_split` до любых трансформаций.\n"
                        "3. `Pipeline` + `StandardScaler` — без утечки из test.\n"
                        "4. Сравнили OLS / Ridge / Lasso → **выбрали** `final_pipe`.\n"
                        "5. Residual plot и веса — на **финальной** модели и **том же** test.\n"
                        "6. Если R2 train >> R2 test — переобучение; паттерн в остатках — нелинейность."
                    ),
                }
            ],
        },
    ]


def sections_logistic() -> list[dict]:
    return [
        {
            "slide_title": "Постановка задачи",
            "kind": "intro",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Классифицируем **кредитных клиентов** (OpenML `credit-g`): "
                        "«хороший» vs «плохой» заёмщик.\n\n"
                        "**Сюжет:** EDA → дисбаланс классов → ловушка Accuracy → "
                        "`class_weight` → подбор `C` → Pipeline со scaling → "
                        "ROC/PR/калибровка → порог → интерпретация — **один** датасет и **один** test."
                    ),
                }
            ],
        },
        {
            "slide_title": "Загрузка и EDA",
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

%matplotlib inline
np.random.seed(42)
sns.set_theme(style="whitegrid", font_scale=1.05)

credit = fetch_openml("credit-g", version=1, as_frame=True, parser="auto")
df = credit.frame.copy()
y = (df["class"] == "bad").astype(int)
X = pd.get_dummies(df.drop(columns=["class"]), drop_first=True)

print(f"Объектов: {len(df)}, признаков после OHE: {X.shape[1]}")
print(f"Доля класса 'bad': {y.mean():.3f}")

fig, ax = plt.subplots(figsize=(4, 3))
y.value_counts().sort_index().plot(kind="bar", ax=ax, color=["steelblue", "crimson"])
ax.set_xticklabels(["good (0)", "bad (1)"], rotation=0)
ax.set_title("Дисбаланс классов")
ax.set_ylabel("число объектов")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Решение: train / test split",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "**Решение:** стратифицированный split (`random_state=42`). Этот test — до конца ноутбука.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)
print(f"Train: {len(X_train)}, test: {len(X_test)}")
print("Доля bad в train:", y_train.mean().round(3), "| test:", y_test.mean().round(3))
""",
                },
            ],
        },
        {
            "slide_title": "Ловушка Accuracy",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Модель «всегда good» даёт высокий accuracy, но бесполезна для поиска «плохих» клиентов.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.dummy import DummyClassifier
from sklearn.metrics import classification_report

dummy = DummyClassifier(strategy="most_frequent")
dummy.fit(X_train, y_train)
print(f"Dummy accuracy: {dummy.score(X_test, y_test):.3f}\\n")

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

pipe_baseline = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=2000, random_state=42),
)
pipe_baseline.fit(X_train, y_train)
print("LogReg без class_weight:")
print(classification_report(y_test, pipe_baseline.predict(X_test), target_names=["good", "bad"], digits=3))
""",
                },
            ],
        },
        {
            "slide_title": "Решение: class_weight='balanced'",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "**Решение:** включаем `class_weight='balanced'` — усиливаем штраф за ошибки на минорном классе «bad».",
                },
                {
                    "type": "code",
                    "source": """\
USE_CLASS_WEIGHT = "balanced"

pipe_balanced = make_pipeline(
    StandardScaler(),
    LogisticRegression(class_weight=USE_CLASS_WEIGHT, max_iter=2000, random_state=42),
)
pipe_balanced.fit(X_train, y_train)
print("LogReg с class_weight='balanced':")
print(classification_report(y_test, pipe_balanced.predict(X_test), target_names=["good", "bad"], digits=3))
""",
                },
            ],
        },
        {
            "slide_title": "Подбор регуляризации C",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Сравниваем `C` на **том же** train/test с уже выбранным `class_weight`.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.metrics import average_precision_score

C_values = [0.01, 0.1, 1.0, 10.0, 100.0]
rows = []
for C in C_values:
    m = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=C, class_weight=USE_CLASS_WEIGHT, max_iter=2000, random_state=42),
    )
    m.fit(X_train, y_train)
    proba = m.predict_proba(X_test)[:, 1]
    rows.append({
        "C": C,
        "accuracy": m.score(X_test, y_test),
        "PR-AUC": average_precision_score(y_test, proba),
        "norm_w": float(np.linalg.norm(m.named_steps["logisticregression"].coef_)),
    })

c_df = pd.DataFrame(rows).sort_values("PR-AUC", ascending=False)
display(c_df.round(4))
""",
                },
            ],
        },
        {
            "slide_title": "Решение: финальная модель",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "**Решение:** берём `C` с лучшим PR-AUC на test. Обучаем `final_pipe` — дальше только она.",
                },
                {
                    "type": "code",
                    "source": """\
BEST_C = float(c_df.iloc[0]["C"])

final_pipe = make_pipeline(
    StandardScaler(),
    LogisticRegression(C=BEST_C, class_weight=USE_CLASS_WEIGHT, max_iter=2000, random_state=42),
)
final_pipe.fit(X_train, y_train)
proba = final_pipe.predict_proba(X_test)[:, 1]
pred = final_pipe.predict(X_test)

print(f"Финальная модель: C={BEST_C}, class_weight={USE_CLASS_WEIGHT!r}")
print(classification_report(y_test, pred, target_names=["good", "bad"], digits=3))
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
                    "source": "При дисбалансе смотрим **PR-кривую**. Reliability diagram проверяет калибровку вероятностей.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.metrics import RocCurveDisplay, PrecisionRecallDisplay
from sklearn.calibration import calibration_curve

fig, axes = plt.subplots(1, 3, figsize=(14, 4))

RocCurveDisplay.from_predictions(y_test, proba, ax=axes[0])
axes[0].set_title("ROC")

PrecisionRecallDisplay.from_predictions(y_test, proba, ax=axes[1])
axes[1].set_title("PR (дисбаланс)")

frac_pos, mean_pred = calibration_curve(y_test, proba, n_bins=8, strategy="uniform")
axes[2].plot([0, 1], [0, 1], "k--", label="идеал")
axes[2].plot(mean_pred, frac_pos, "o-", color="crimson", label="final_pipe")
axes[2].set_xlabel("средняя P(bad)")
axes[2].set_ylabel("доля bad")
axes[2].set_title("Калибровка")
axes[2].legend()
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Выбор порога",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Порог 0.5 не обязан быть оптимальным. Сравним precision/recall при разных порогах.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.metrics import precision_score, recall_score

rows_thr = []
for thr in [0.5, 0.35, 0.25]:
    y_p = (proba >= thr).astype(int)
    rows_thr.append({
        "threshold": thr,
        "precision": precision_score(y_test, y_p, zero_division=0),
        "recall": recall_score(y_test, y_p, zero_division=0),
    })
thr_df = pd.DataFrame(rows_thr)
display(thr_df.round(3))

CHOSEN_THRESHOLD = 0.35
print(f"\\n**Решение:** для баланса recall/precision берём порог {CHOSEN_THRESHOLD}")
""",
                },
            ],
        },
        {
            "slide_title": "Интерпретация: log-odds",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Вес $w_j$ — изменение log-odds при +1 sigma признака после scaler (при прочих равных).",
                },
                {
                    "type": "code",
                    "source": """\
lr = final_pipe.named_steps["logisticregression"]
w = lr.coef_.ravel()
feat_names = X.columns
top_idx = np.argsort(np.abs(w))[-8:]

plt.figure(figsize=(8, 4))
plt.barh(np.array(feat_names)[top_idx], w[top_idx], color="steelblue")
plt.xlabel("вес (log-odds)")
plt.title("Топ-8 признаков |w| (финальная модель)")
plt.tight_layout()
plt.show()

j = top_idx[-1]
print(f"Признак: {feat_names[j]}")
print(f"  w = {w[j]:+.3f} → odds × {np.exp(w[j]):.2f} при +1 sigma")
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
                        "1. Один датасет `credit-g`, один stratified split.\n"
                        "2. При дисбалансе — не верить Accuracy; `class_weight='balanced'`.\n"
                        "3. Подбор `C` → **фиксируем** `final_pipe`.\n"
                        "4. PR-кривая важнее ROC; калибровка на hold-out.\n"
                        "5. Порог — бизнес-решение, не обязательно 0.5.\n"
                        "6. Интерпретация через log-odds на **финальной** модели."
                    ),
                }
            ],
        },
    ]


def sections_derevo() -> list[dict]:
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
                        "**Сюжет:** EDA → split → Gini vs entropy → sweep `max_depth` → "
                        "**ограничение глубины** → визуализация и importance → "
                        "confusion matrix на **финальном** дереве."
                    ),
                }
            ],
        },
        {
            "slide_title": "Загрузка и EDA",
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

from sklearn.datasets import load_wine

%matplotlib inline
np.random.seed(42)
sns.set_theme(style="whitegrid", font_scale=1.05)

wine = load_wine(as_frame=True)
df = wine.frame.copy()
target_col = "target"
feature_cols = list(wine.feature_names)
class_names = list(wine.target_names)

print(f"Объектов: {len(df)}, признаков: {len(feature_cols)}, классов: {df[target_col].nunique()}")
display(df.head())

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
counts = df[target_col].value_counts().sort_index()
axes[0].bar(class_names, counts.values, color="steelblue", edgecolor="white")
axes[0].set_title("Баланс классов")

for cls in sorted(df[target_col].unique()):
    sub = df[df[target_col] == cls]
    axes[1].scatter(sub["alcohol"], sub["color_intensity"], alpha=0.7, s=35, label=class_names[cls])
axes[1].set_xlabel("alcohol")
axes[1].set_ylabel("color_intensity")
axes[1].set_title("Два разделяющих признака")
axes[1].legend(fontsize=8)
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Решение: train / test split",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "**Решение:** стратифицированный split. Деревья не требуют масштабирования.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.model_selection import train_test_split

X = df[feature_cols].values
y = df[target_col].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)
print(f"Train: {len(X_train)}, test: {len(X_test)}")
""",
                },
            ],
        },
        {
            "slide_title": "Критерий: Gini vs entropy",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": "Сравниваем критерии при одинаковой глубине `max_depth=5`.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.tree import DecisionTreeClassifier

crit_rows = []
for crit in ("gini", "entropy"):
    m = DecisionTreeClassifier(criterion=crit, max_depth=5, random_state=42)
    m.fit(X_train, y_train)
    crit_rows.append({
        "criterion": crit,
        "accuracy train": m.score(X_train, y_train),
        "accuracy test": m.score(X_test, y_test),
    })

crit_df = pd.DataFrame(crit_rows).sort_values("accuracy test", ascending=False)
display(crit_df.round(4))
""",
                },
            ],
        },
        {
            "slide_title": "Решение: выбор criterion",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "**Решение:** берём критерий с лучшим test accuracy — дальше подбираем глубину только для него.",
                },
                {
                    "type": "code",
                    "source": """\
CHOSEN_CRITERION = crit_df.iloc[0]["criterion"]
print(f"Выбран criterion: {CHOSEN_CRITERION!r}")
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
                    "source": "Без ограничений дерево запоминает train. Ищем `max_depth` с лучшим test accuracy.",
                },
                {
                    "type": "code",
                    "source": """\
depths = list(range(1, 16))
train_acc, test_acc = [], []

for d in depths:
    m = DecisionTreeClassifier(criterion=CHOSEN_CRITERION, max_depth=d, random_state=42)
    m.fit(X_train, y_train)
    train_acc.append(m.score(X_train, y_train))
    test_acc.append(m.score(X_test, y_test))

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(depths, train_acc, "o-", label="train", color="steelblue")
ax.plot(depths, test_acc, "s-", label="test", color="crimson")
ax.set_xlabel("max_depth")
ax.set_ylabel("accuracy")
ax.set_title(f"Глубина vs accuracy (criterion={CHOSEN_CRITERION})")
ax.legend()
plt.tight_layout()
plt.show()

BEST_DEPTH = depths[int(np.argmax(test_acc))]
print(f"Лучший max_depth на test: {BEST_DEPTH} (acc={max(test_acc):.3f})")
""",
                },
            ],
        },
        {
            "slide_title": "Решение: финальное дерево",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": "**Решение:** обучаем `final_tree` с выбранными `criterion` и `max_depth`. Все диагностики — на нём.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.metrics import classification_report, accuracy_score

final_tree = DecisionTreeClassifier(
    criterion=CHOSEN_CRITERION, max_depth=BEST_DEPTH, random_state=42
)
final_tree.fit(X_train, y_train)
y_pred = final_tree.predict(X_test)

print(f"Финальное дерево: criterion={CHOSEN_CRITERION!r}, max_depth={BEST_DEPTH}")
print(classification_report(y_test, y_pred, target_names=class_names, digits=3))
print(f"Accuracy test: {accuracy_score(y_test, y_pred):.3f}")
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
                    "source": "`plot_tree` для `final_tree` — правила «признак < порог» в каждом узле.",
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.tree import plot_tree

fig, ax = plt.subplots(figsize=(16, 8))
plot_tree(
    final_tree,
    feature_names=feature_cols,
    class_names=class_names,
    filled=True,
    rounded=True,
    fontsize=9,
    ax=ax,
)
ax.set_title(f"final_tree (max_depth={BEST_DEPTH})")
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
                    "type": "code",
                    "source": """\
imp = final_tree.feature_importances_
order = np.argsort(imp)

plt.figure(figsize=(8, 5))
plt.barh(np.array(feature_cols)[order], imp[order], color="steelblue")
plt.xlabel("feature_importances_")
plt.title("Важность признаков (final_tree)")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Confusion matrix",
            "kind": "viz",
            "cells": [
                {
                    "type": "code",
                    "source": """\
from sklearn.metrics import ConfusionMatrixDisplay

fig, ax = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay.from_predictions(
    y_test, y_pred, display_labels=class_names, cmap="Blues", ax=ax
)
ax.set_title(f"Confusion matrix (final_tree)")
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
                        "1. EDA → один stratified split.\n"
                        "2. Сравнили Gini/entropy → **выбрали** `CHOSEN_CRITERION`.\n"
                        "3. Sweep depth → **ограничили** `BEST_DEPTH` → `final_tree`.\n"
                        "4. `plot_tree`, importance, confusion — на **одном** финальном дереве.\n"
                        "5. График train vs test — признак переобучения без ограничений.\n"
                        "6. Помнить: оси-параллельные границы, нестабильность одного дерева."
                    ),
                }
            ],
        },
    ]
