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
                        "**Сюжет (как в продакшн):** загрузка → feature engineering → "
                        "**OHE `ocean_proximity`** → EDA → split → IQR на train → "
                        "подбор `alpha` → IQR vs **Huber** → метрики на полном test."
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
df = df.fillna(df.median(numeric_only=True))  # редкие NaN в OpenML; дальше — только train-статистики

print(f"Объектов: {len(df)}, столбцов: {len(df.columns)}")
display(df.head())
""",
                },
            ],
        },
        {
            "slide_title": "Feature engineering",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Сырые счётчики (`total_rooms`, `population`, …) сильно коррелируют. "
                        "Заменяем их **удельными метриками** — модель остаётся линейной, "
                        "но признаки информативнее."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
df["rooms_per_household"] = df["total_rooms"] / df["households"]
df["bedrooms_per_room"] = df["total_bedrooms"] / df["total_rooms"].replace(0, np.nan)
df["population_per_household"] = df["population"] / df["households"]

feature_cols = [
    "housing_median_age",
    "median_income",
    "latitude",
    "longitude",
    "rooms_per_household",
    "bedrooms_per_room",
    "population_per_household",
]
cat_col = "ocean_proximity"
model_cols = feature_cols + [cat_col]

print(f"Числовых: {len(feature_cols)}, категория: {cat_col}")
print(df[cat_col].value_counts())
display(df[feature_cols].describe().round(3))
""",
                },
            ],
        },
        {
            "slide_title": "Категория: ocean_proximity",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Расстояние до океана — **категориальный** признак. "
                        "В линейной модели — **One-Hot Encoding** внутри `ColumnTransformer`: "
                        "числовые столбцы масштабируем, категории кодируем (`drop='first'`)."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
ocean_price = df.groupby(cat_col)[target_col].median().sort_values(ascending=False)
print("Медиана цены по району:")
display(ocean_price.to_frame("median_house_value"))
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
                        "Сильнейший сигнал — `median_income`. На гистограмме цены — **хвосты** "
                        "(пороги IQR посчитаем после split, только на train). "
                        "Удельные признаки снижают корреляции между столбцами."
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

print("Корр. rooms_per_household–bedrooms_per_room:",
      corr.loc["rooms_per_household", "bedrooms_per_room"].round(3))
print("Корр. median_income–цена:", corr.loc["median_income", target_col].round(3))
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
                        "**Решение (продакшн):** сначала **один** split на сыром датасете (`random_state=42`). "
                        "Любые пороги, imputation и scaler — **только из train**, test не участвует."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.model_selection import train_test_split

idx_all = np.arange(len(df))
idx_train, idx_test = train_test_split(idx_all, test_size=0.2, random_state=42)

# imputation: медианы только по train
feat_median = df.iloc[idx_train][feature_cols].median()
df[feature_cols] = df[feature_cols].fillna(feat_median)

X_train_full = df.iloc[idx_train][model_cols]
y_train_full = df.iloc[idx_train][target_col].values
X_test = df.iloc[idx_test][model_cols]
y_test = df.iloc[idx_test][target_col].values

print(f"Train: {len(idx_train)}, test: {len(idx_test)}")
""",
                },
            ],
        },
        {
            "slide_title": "Выбросы: IQR только на train",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "MSE сильно штрафует экстремальные **Y**. Правило **IQR** считаем "
                        "по **`y_train`**, границы фиксируем и применяем к train/test — "
                        "без подглядывания в test."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
y_train_series = pd.Series(y_train_full)
q1, q3 = y_train_series.quantile([0.25, 0.75])
iqr = q3 - q1
lower, upper = float(q1 - 1.5 * iqr), float(q3 + 1.5 * iqr)

train_in_bounds = (y_train_full >= lower) & (y_train_full <= upper)
test_in_bounds = (y_test >= lower) & (y_test <= upper)

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
sns.boxplot(y=y_train_series, ax=axes[0], color="steelblue")
axes[0].axhline(lower, color="crimson", linestyle="--", lw=1, label="train IQR")
axes[0].axhline(upper, color="crimson", linestyle="--", lw=1)
axes[0].set_title("Boxplot y_train")
axes[0].set_ylabel("median_house_value")
axes[0].legend(fontsize=8)

income_tr = df.iloc[idx_train]["median_income"].values
axes[1].scatter(income_tr[train_in_bounds], y_train_full[train_in_bounds],
                alpha=0.2, s=10, color="steelblue", label="train, в границах")
axes[1].scatter(income_tr[~train_in_bounds], y_train_full[~train_in_bounds],
                alpha=0.8, s=25, color="crimson", label="train, выброс IQR")
axes[1].set_xlabel("median_income")
axes[1].set_ylabel("median_house_value")
axes[1].set_title("Выбросы train по IQR(train)")
axes[1].legend(fontsize=8)
plt.tight_layout()
plt.show()

print(f"IQR(train): [{lower:,.0f}; {upper:,.0f}]")
print(f"Выбросов в train: {(~train_in_bounds).sum()} ({100 * (~train_in_bounds).mean():.1f}%)")
print(f"Test вне границ train-IQR: {(~test_in_bounds).sum()} ({100 * (~test_in_bounds).mean():.1f}%)")
""",
                },
            ],
        },
        {
            "slide_title": "Решение: очистка train",
            "kind": "example",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "**Решение:** из **train** убираем объекты вне `[lower, upper]`. "
                        "**Test не фильтруем** — в продакшн модель должна отвечать на любой объект; "
                        "метрики считаем на **полном** hold-out."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
idx_train_clean = idx_train[train_in_bounds]
X_train = df.iloc[idx_train_clean][model_cols]
y_train = df.iloc[idx_train_clean][target_col].values

print(f"Train до IQR: {len(idx_train)} → после: {len(idx_train_clean)}")
print(f"Test без изменений: {len(idx_test)} объектов")
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
                    "source": (
                        "`ColumnTransformer`: числовые → `StandardScaler`, "
                        "`ocean_proximity` → `OneHotEncoder` — fit **только на train**."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def make_preprocessor():
    return ColumnTransformer([
        ("num", StandardScaler(), feature_cols),
        ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), [cat_col]),
    ])

def make_model_pipe(model):
    return Pipeline([
        ("prep", make_preprocessor()),
        ("model", model),
    ])

pipe_ols = make_model_pipe(LinearRegression())
pipe_ols.fit(X_train, y_train)
y_pred_ols = pipe_ols.predict(X_test)

print(f"OLS — Test MAE:  {mean_absolute_error(y_test, y_pred_ols):,.0f}")
print(f"OLS — Test RMSE: {mean_squared_error(y_test, y_pred_ols) ** 0.5:.3f}")
print(f"OLS — Test R2:   {r2_score(y_test, y_pred_ols):.3f}")
print("Признаков после OHE:", len(pipe_ols.named_steps["prep"].get_feature_names_out()))
""",
                },
            ],
        },
        {
            "slide_title": "Эксперимент: log1p(y)",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "На EDA видны **хвосты** цены — классический приём: обучать модель на "
                        "`log1p(y)`, предсказания возвращать через `expm1`. "
                        "Проверим, даёт ли `log1p(y)` выигрыш на **очищенном train** "
                        "(пороги IQR — только с train)."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.compose import TransformedTargetRegressor

def make_regressor(model, log_target=False):
    pipe = make_model_pipe(model)
    if log_target:
        return TransformedTargetRegressor(
            regressor=pipe,
            func=np.log1p,
            inverse_func=np.expm1,
        )
    return pipe

def model_coef(estimator):
    if isinstance(estimator, TransformedTargetRegressor):
        return estimator.regressor_.named_steps["model"].coef_
    return estimator.named_steps["model"].coef_

def fitted_preprocessor(estimator):
    if isinstance(estimator, TransformedTargetRegressor):
        return estimator.regressor_.named_steps["prep"]
    return estimator.named_steps["prep"]

log_compare = []
for log_y in (False, True):
    m = make_regressor(LinearRegression(), log_target=log_y)
    m.fit(X_train, y_train)
    pred = m.predict(X_test)
    log_compare.append({
        "log1p(y)": log_y,
        "R2 test (исходная шкала)": r2_score(y_test, pred),
        "RMSE test": mean_squared_error(y_test, pred) ** 0.5,
    })

log_df = pd.DataFrame(log_compare)
display(log_df.round({"R2 test (исходная шкала)": 4, "RMSE test": 1}))

USE_LOG_Y = log_df.loc[log_df["R2 test (исходная шкала)"].idxmax(), "log1p(y)"]
label = "log1p(y)" if USE_LOG_Y else "исходная y"
print(f"**Решение:** для дальнейших шагов оставляем {label}.")
""",
                },
            ],
        },
        {
            "slide_title": "Подбор alpha: Ridge, Lasso и ElasticNet",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "`alpha` (и для ElasticNet — `l1_ratio`) подбираем **только на IQR-train** "
                        "через `GridSearchCV` (5-fold). Test не участвует."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import Ridge, Lasso, ElasticNet

alphas = np.logspace(-2, 3, 25)
l1_ratios = [0.1, 0.3, 0.5, 0.7, 0.9]

if USE_LOG_Y:
    ridge_base = TransformedTargetRegressor(
        regressor=make_model_pipe(Ridge()),
        func=np.log1p,
        inverse_func=np.expm1,
    )
    lasso_base = TransformedTargetRegressor(
        regressor=make_model_pipe(Lasso(max_iter=10000)),
        func=np.log1p,
        inverse_func=np.expm1,
    )
    enet_base = TransformedTargetRegressor(
        regressor=make_model_pipe(ElasticNet(max_iter=10000)),
        func=np.log1p,
        inverse_func=np.expm1,
    )
    ridge_cv = GridSearchCV(
        ridge_base,
        param_grid={"regressor__model__alpha": alphas},
        cv=5,
        scoring="neg_root_mean_squared_error",
    )
    lasso_cv = GridSearchCV(
        lasso_base,
        param_grid={"regressor__model__alpha": alphas},
        cv=5,
        scoring="neg_root_mean_squared_error",
    )
    enet_cv = GridSearchCV(
        enet_base,
        param_grid={
            "regressor__model__alpha": alphas,
            "regressor__model__l1_ratio": l1_ratios,
        },
        cv=5,
        scoring="neg_root_mean_squared_error",
    )
else:
    ridge_cv = GridSearchCV(
        make_model_pipe(Ridge()),
        param_grid={"model__alpha": alphas},
        cv=5,
        scoring="neg_root_mean_squared_error",
    )
    lasso_cv = GridSearchCV(
        make_model_pipe(Lasso(max_iter=10000)),
        param_grid={"model__alpha": alphas},
        cv=5,
        scoring="neg_root_mean_squared_error",
    )
    enet_cv = GridSearchCV(
        make_model_pipe(ElasticNet(max_iter=10000)),
        param_grid={"model__alpha": alphas, "model__l1_ratio": l1_ratios},
        cv=5,
        scoring="neg_root_mean_squared_error",
    )

ridge_cv.fit(X_train, y_train)
lasso_cv.fit(X_train, y_train)
enet_cv.fit(X_train, y_train)

if USE_LOG_Y:
    best_ridge_alpha = ridge_cv.best_params_["regressor__model__alpha"]
    best_lasso_alpha = lasso_cv.best_params_["regressor__model__alpha"]
    best_enet_alpha = enet_cv.best_params_["regressor__model__alpha"]
    best_enet_l1 = enet_cv.best_params_["regressor__model__l1_ratio"]
else:
    best_ridge_alpha = ridge_cv.best_params_["model__alpha"]
    best_lasso_alpha = lasso_cv.best_params_["model__alpha"]
    best_enet_alpha = enet_cv.best_params_["model__alpha"]
    best_enet_l1 = enet_cv.best_params_["model__l1_ratio"]

print(f"Ridge — alpha: {best_ridge_alpha:.4f}, CV RMSE: {-ridge_cv.best_score_:.3f}")
print(f"Lasso — alpha: {best_lasso_alpha:.4f}, CV RMSE: {-lasso_cv.best_score_:.3f}")
print(f"ElasticNet — alpha: {best_enet_alpha:.4f}, l1_ratio: {best_enet_l1}, CV RMSE: {-enet_cv.best_score_:.3f}")
""",
                },
            ],
        },
        {
            "slide_title": "Сравнение: IQR-путь vs Huber",
            "kind": "experiment",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "IQR-путь: OLS / Ridge / Lasso / **ElasticNet** на **очищенном train**. "
                        "**Huber** — на **полном train**. Метрики на **полном test**; "
                        "для Huber смотрим и **MAE** (робастная модель ближе к модулю, чем к MSE)."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
from sklearn.linear_model import HuberRegressor

candidates = {
    "OLS (IQR train)": make_regressor(LinearRegression(), log_target=USE_LOG_Y),
    "Ridge (IQR train)": make_regressor(Ridge(alpha=best_ridge_alpha), log_target=USE_LOG_Y),
    "Lasso (IQR train)": make_regressor(
        Lasso(alpha=best_lasso_alpha, max_iter=10000), log_target=USE_LOG_Y
    ),
    "ElasticNet (IQR train)": make_regressor(
        ElasticNet(alpha=best_enet_alpha, l1_ratio=best_enet_l1, max_iter=10000),
        log_target=USE_LOG_Y,
    ),
}

rows = []
for name, pipe in candidates.items():
    pipe.fit(X_train, y_train)
    pred_te = pipe.predict(X_test)
    pred_in = pred_te[test_in_bounds]
    w = model_coef(pipe)
    rows.append({
        "model": name,
        "R2 test (full)": r2_score(y_test, pred_te),
        "R2 test (in bounds)": r2_score(y_test[test_in_bounds], pred_in),
        "MAE test": mean_absolute_error(y_test, pred_te),
        "RMSE test": mean_squared_error(y_test, pred_te) ** 0.5,
        "norm_w": np.linalg.norm(w),
    })

pipe_huber = make_model_pipe(HuberRegressor(max_iter=500))
pipe_huber.fit(X_train_full, y_train_full)
pred_huber = pipe_huber.predict(X_test)
pred_huber_in = pred_huber[test_in_bounds]
w_huber = pipe_huber.named_steps["model"].coef_
rows.append({
    "model": "Huber (full train)",
    "R2 test (full)": r2_score(y_test, pred_huber),
    "R2 test (in bounds)": r2_score(y_test[test_in_bounds], pred_huber_in),
    "MAE test": mean_absolute_error(y_test, pred_huber),
    "RMSE test": mean_squared_error(y_test, pred_huber) ** 0.5,
    "norm_w": np.linalg.norm(w_huber),
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
                    "source": "**Решение:** берём модель с лучшим RMSE на **полном test**. Дальше все графики — на том же hold-out.",
                },
                {
                    "type": "code",
                    "source": """\
best_name = metrics_df.iloc[0]["model"]
if best_name == "Huber (full train)":
    final_pipe = pipe_huber
else:
    final_pipe = candidates[best_name]
    final_pipe.fit(X_train, y_train)
y_pred = final_pipe.predict(X_test)
y_pred_train = final_pipe.predict(X_train)
r2_train = r2_score(y_train, y_pred_train)
r2_test = r2_score(y_test, y_pred)

print(f"Выбрана модель: {best_name}")
print(f"Train R2: {r2_train:.3f}  |  Test R2: {r2_test:.3f}")
if r2_train - r2_test > 0.05:
    print("→ Train >> Test: возможное переобучение")
print(f"Test MAE:  {mean_absolute_error(y_test, y_pred):,.0f}")
print(f"Test RMSE: {mean_squared_error(y_test, y_pred) ** 0.5:.3f}")
""",
                },
            ],
        },
        {
            "slide_title": "Диагностика: predicted vs actual и остатки",
            "kind": "viz",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "**Predicted vs actual:** точки у диагонали — хороший прогноз. "
                        "**Residual plot:** случайное облако вокруг нуля; «воронка» — нелинейность."
                    ),
                },
                {
                    "type": "code",
                    "source": """\
residuals = y_test - y_pred

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

axes[0].scatter(y_test, y_pred, alpha=0.35, s=15, color="steelblue")
lo, hi = y_test.min(), y_test.max()
axes[0].plot([lo, hi], [lo, hi], "k--", lw=1, label="идеал ŷ = y")
axes[0].set_xlabel("факт y")
axes[0].set_ylabel("предсказание ŷ")
axes[0].set_title(f"Predicted vs actual ({best_name})")
axes[0].legend(fontsize=8)

axes[1].scatter(y_pred, residuals, alpha=0.35, s=15, color="steelblue")
axes[1].axhline(0, color="crimson", linestyle="--")
axes[1].set_xlabel("предсказание ŷ")
axes[1].set_ylabel("остаток y − ŷ")
axes[1].set_title("Residual plot")

axes[2].hist(residuals, bins=35, color="steelblue", edgecolor="white")
axes[2].set_xlabel("остаток")
axes[2].set_title("Гистограмма остатков")
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
w = model_coef(final_pipe)
feat_names = fitted_preprocessor(final_pipe).get_feature_names_out()
order = np.argsort(np.abs(w))

plt.figure(figsize=(9, 6))
plt.barh(np.array(feat_names)[order], w[order], color="steelblue")
plt.xlabel("вес (OHE + StandardScaler → модель)")
plt.title(f"Интерпретация весов ({best_name})")
plt.tight_layout()
plt.show()

for name, val in sorted(zip(feat_names, w), key=lambda t: abs(t[1]), reverse=True)[:5]:
    print(f"{name:28s}: {val:+.3f}")
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
                        "1. **Split первым** — затем imputation, IQR и scaler только по train.\n"
                        "2. Feature engineering и категориальные признаки в `ColumnTransformer`.\n"
                        "3. Test **не фильтруем**; метрики на полном hold-out.\n"
                        "4. Ridge / Lasso / **ElasticNet** — `GridSearchCV` без участия test.\n"
                        "5. Сравнили IQR-путь и **Huber**; смотрели R², **MAE**, RMSE.\n"
                        "6. **Train vs test R²**, predicted vs actual, residual plot, интерпретация весов."
                    ),
                }
            ],
        },
        {
            "slide_title": "Исследовательские вопросы",
            "kind": "summary",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Дополнительные задания для **самостоятельной** работы. "
                        "Сохраняйте каркас: split → IQR по train → `ColumnTransformer`, "
                        "оценка на **полном** hold-out test. Фиксируйте **R², MAE, RMSE** и краткий вывод.\n\n"
                        "1. **Целевая `log1p(y)` vs исходная `y`:** при том же препроцессинге и IQR на train "
                        "сравните метрики на исходной шкале цены (через `expm1`). "
                        "Когда log-трансформация целевой оправдана, а когда нет?\n\n"
                        "2. **Порядок IQR и split:** (A) IQR на всём датасете → удаление → split; "
                        "(B) split → IQR только на train. Чем отличаются R² и RMSE на test? "
                        "Есть ли утечка в варианте A?\n\n"
                        "3. **Полный test vs in-bounds:** обучите модель на clean train, "
                        "оцените на (a) всём test и (b) объектах внутри train-IQR. "
                        "Какой протокол отражает поведение модели «в проде»?\n\n"
                        "4. **`log1p(median_income)` как признак:** замените или добавьте к raw income. "
                        "Меняется ли качество линейной модели с OHE?\n\n"
                        "5. **`PolynomialFeatures(degree=2)` для `median_income`:** "
                        "внутри `ColumnTransformer` + Ridge с подбором `alpha`. "
                        "Окупается ли усложнение по метрикам и residual plot?\n\n"
                        "6. **Без `ocean_proximity`:** уберите OHE и сравните с базовым пайплайном. "
                        "Как меняются R² и вклад lat/lon, income в весах?\n\n"
                        "7. **Сырые счётчики vs удельные метрики:** `total_rooms`, `population`, `households` "
                        "вместо `rooms_per_household` и др. Как влияет мультиколлинеарность на `norm_w`?\n\n"
                        "8. **Стратегии для выбросов в `y`:** (a) IQR-trim train, (b) полный train + Huber, "
                        "(c) полный train + OLS. При какой метрике — **MAE** или **RMSE** — "
                        "каждый подход сильнее?\n\n"
                        "9. **Winsorize вместо удаления:** ограничьте `y` train-квантилями (например, 1–99%) "
                        "без удаления строк. Сравните размер train, R² и MAE с IQR-trim.\n\n"
                        "10. **`QuantileRegressor`:** линейная модель с pinball-loss (медиана). "
                        "Сравните с Huber и OLS по **MAE**; на predicted vs actual отметьте "
                        "участки с наибольшими ошибками (дешёвое / дорогое жильё)."
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
