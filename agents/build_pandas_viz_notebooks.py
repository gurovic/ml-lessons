"""Сборка code.ipynb и project.ipynb для уроков pandas и vizualizatsiya."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents"))
from notebook_utils import build_ipynb, save_ipynb  # noqa: E402


def _pandas_code_sections() -> list[dict]:
    return [
        {
            "slide_title": "Series и DataFrame",
            "kind": "example",
            "cells": [
                {"type": "markdown", "source": "Базовые структуры Pandas."},
                {
                    "type": "code",
                    "source": """\
import pandas as pd

s = pd.Series([10, 20, 15], index=["a", "b", "c"])
df = pd.DataFrame({"Age": [22, 38, 26], "Fare": [7.25, 71.28, 7.92], "Sex": ["male", "female", "female"]})

print("Series:\\n", s)
print("\\nDataFrame shape:", df.shape)
print(df.dtypes)
""",
                },
            ],
        },
        {
            "slide_title": "Чтение данных",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
from sklearn.datasets import fetch_openml

raw = fetch_openml("titanic", version=1, as_frame=True, parser="auto")
df = raw.frame.copy()
df["Survived"] = df["survived"].astype(int)
df["Pclass"] = df["pclass"].astype(int)
df["Age"] = pd.to_numeric(df["age"], errors="coerce")
df["Fare"] = pd.to_numeric(df["fare"], errors="coerce")
df["Sex"] = df["sex"]
df["Embarked"] = df["embarked"]

print(df.shape)
df.head()
""",
                },
            ],
        },
        {
            "slide_title": "Первичный осмотр таблицы",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
df.info()
display(df.describe())
print("Sex counts:\\n", df["Sex"].value_counts())
""",
                },
            ],
        },
        {
            "slide_title": "Индексы строк и столбцов",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
df_idx = df.set_index("name")
print(df_idx.index[:3])
df_back = df_idx.reset_index()
print("После reset_index:", df_back.columns[:3].tolist())
""",
                },
            ],
        },
        {
            "slide_title": "loc и iloc: две системы адресации",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
sample = df.head(8)
print("loc по меткам 3:5, столбцы Age/Fare:")
display(sample.loc[3:5, ["Age", "Fare"]])
print("iloc по позициям 0:3, столбцы 1:3:")
display(sample.iloc[0:3, 1:3])
""",
                },
            ],
        },
        {
            "slide_title": "Фильтрация и булевы маски",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
mask = (df["Age"] > 30) & (df["Pclass"] == 1)
filtered = df.loc[mask, ["Sex", "Age", "Pclass", "Survived"]]
print(f"Строк по маске: {len(filtered)}")
filtered.head()
""",
                },
            ],
        },
        {
            "slide_title": "groupby и агрегации",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
by_class = df.groupby("Pclass").agg({"Fare": "mean", "Age": "median", "Survived": "mean"})
by_class.round(2)
""",
                },
            ],
        },
        {
            "slide_title": "merge и join",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
ports = pd.DataFrame({"Embarked": ["S", "C", "Q"], "port_name": ["Southampton", "Cherbourg", "Queenstown"]})
merged = pd.merge(df[["Embarked", "Fare"]].drop_duplicates("Embarked"), ports, on="Embarked", how="left")
merged
""",
                },
            ],
        },
        {
            "slide_title": "Пропуски: isna, fillna, dropna",
            "kind": "experiment",
            "cells": [
                {
                    "type": "code",
                    "source": """\
print("Пропуски Age:", df["Age"].isna().sum())
df_filled = df.copy()
df_filled["Age"] = df_filled["Age"].fillna(df_filled["Age"].median())
print("После fillna median:", df_filled["Age"].isna().sum())
""",
                },
            ],
        },
        {
            "slide_title": "Типы данных",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
df_cat = df.copy()
df_cat["Sex"] = df_cat["Sex"].astype("category")
print(df_cat["Sex"].dtype)
print("Память object vs category:", df["Sex"].memory_usage(deep=True), df_cat["Sex"].memory_usage(deep=True))
""",
                },
            ],
        },
        {
            "slide_title": "apply и transform",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
emb_map = {"S": 0, "C": 1, "Q": 2}
df["Embarked_code"] = df["Embarked"].map(emb_map)
df["Fare_z"] = df.groupby("Pclass")["Fare"].transform(lambda x: (x - x.mean()) / x.std())
df[["Embarked", "Embarked_code", "Pclass", "Fare_z"]].head()
""",
                },
            ],
        },
        {
            "slide_title": "pivot и pivot_table",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
pt = df.pivot_table(values="Survived", index="Pclass", columns="Sex", aggfunc="mean")
pt.round(2)
""",
                },
            ],
        },
        {
            "slide_title": "Базовая производительность",
            "kind": "experiment",
            "cells": [
                {
                    "type": "code",
                    "source": """\
import time
s = pd.Series(range(200_000))
t0 = time.perf_counter(); _ = s.apply(lambda x: x * 2); t1 = time.perf_counter()
t2 = time.perf_counter(); _ = s * 2; t3 = time.perf_counter()
print(f"apply: {t1-t0:.3f}s, vectorized: {t3-t2:.3f}s")
""",
                },
            ],
        },
        {
            "slide_title": "Pandas и sklearn Pipeline",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

features = ["Pclass", "Age", "Fare"]
X = df[features]
y = df["Survived"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=500, random_state=42)),
])
pipe.fit(X_train, y_train)
print(f"Test accuracy: {pipe.score(X_test, y_test):.3f}")
""",
                },
            ],
        },
    ]


def _viz_code_sections() -> list[dict]:
    return [
        {
            "slide_title": "Matplotlib: figure и axes",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(6, 4))
x = np.linspace(0, 2 * np.pi, 100)
ax.plot(x, np.sin(x))
ax.set_xlabel("x")
ax.set_ylabel("sin(x)")
ax.set_title("OO-стиль: fig, ax")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Line plot",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
epochs = np.arange(1, 11)
train = 0.5 + 0.04 * epochs
test = 0.5 + 0.03 * epochs - 0.002 * (epochs - 6) ** 2

plt.figure(figsize=(6, 4))
plt.plot(epochs, train, "o-", label="train")
plt.plot(epochs, test, "s-", label="test")
plt.xlabel("эпоха")
plt.ylabel("accuracy")
plt.legend()
plt.title("Learning curve (схематично)")
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Scatter plot",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
from sklearn.datasets import make_classification
X, y = make_classification(n_samples=100, n_features=2, n_redundant=0, random_state=42)
plt.figure(figsize=(6, 4))
plt.scatter(X[y==0, 0], X[y==0, 1], alpha=0.7, label="0")
plt.scatter(X[y==1, 0], X[y==1, 1], alpha=0.7, label="1")
plt.legend()
plt.xlabel("x1")
plt.ylabel("x2")
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Bar chart",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
models = ["A", "B"]
mae = [0.12, 0.09]
rmse = [0.18, 0.14]
x = np.arange(len(models))
w = 0.35
fig, ax = plt.subplots(figsize=(5, 4))
ax.bar(x - w/2, mae, w, label="MAE")
ax.bar(x + w/2, rmse, w, label="RMSE")
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.set_ylim(0, 0.25)
ax.legend()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Histogram и box plot",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
import seaborn as sns
import pandas as pd
from sklearn.datasets import fetch_openml

raw = fetch_openml("titanic", version=1, as_frame=True, parser="auto")
df = raw.frame
df["Fare"] = pd.to_numeric(df["fare"], errors="coerce")
df["Pclass"] = df["pclass"].astype(int)

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].hist(df["Fare"].dropna(), bins=30, color="steelblue", edgecolor="white")
axes[0].set_title("Histogram Fare")
sns.boxplot(data=df, x="Pclass", y="Fare", ax=axes[1])
axes[1].set_title("Boxplot Fare by Pclass")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Seaborn: высокоуровневые графики",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
sns.set_theme(style="whitegrid")
tips = sns.load_dataset("tips")
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="day")
plt.title("sns.scatterplot")
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Подписи, легенды и цвет",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
x = np.linspace(0, 5, 30)
plt.figure(figsize=(6, 4))
plt.plot(x, np.sin(x), "o-", label="sin")
plt.plot(x, np.cos(x), "s--", label="cos")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Подписи и legend")
plt.legend()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Несколько subplots",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
fig, axes = plt.subplots(2, 2, figsize=(8, 6))
axes[0, 0].hist(np.random.randn(200), bins=20)
axes[0, 1].scatter(np.random.randn(50), np.random.randn(50), alpha=0.6)
axes[1, 0].bar(["A", "B"], [3, 5])
axes[1, 1].boxplot([np.random.randn(40) for _ in range(3)])
fig.suptitle("2×2 subplots")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Heatmap и корреляции",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
num = df[["Fare"]].join(pd.to_numeric(df[["age"]], errors="coerce"))
num.columns = ["Fare", "Age"]
corr = num.corr()
plt.figure(figsize=(4, 3))
sns.heatmap(corr, annot=True, cmap="RdBu_r", center=0, vmin=-1, vmax=1)
plt.title("Корреляция Fare–Age")
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Категориальные графики",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
df["Sex"] = df["sex"]
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
sns.countplot(data=df, x="Sex", hue="Sex", ax=axes[0], palette="Set2", legend=False)
sns.barplot(data=df, x="Pclass", y="Fare", hue="Pclass", ax=axes[1], palette="Blues", legend=False)
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Визуализация для ML: остатки",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
from sklearn.linear_model import LinearRegression
x = np.linspace(0, 10, 80).reshape(-1, 1)
y = 2 * x.ravel() + np.random.normal(0, 1.5, 80)
model = LinearRegression().fit(x, y)
y_hat = model.predict(x)
res = y - y_hat
plt.figure(figsize=(6, 4))
plt.scatter(y_hat, res, alpha=0.6)
plt.axhline(0, color="crimson", ls="--")
plt.xlabel("предсказание ŷ")
plt.ylabel("остаток")
plt.title("Residual plot")
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Визуализация для ML: ROC и PR",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import RocCurveDisplay, PrecisionRecallDisplay
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = make_classification(n_samples=300, random_state=42)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500))
clf.fit(X_tr, y_tr)
proba = clf.predict_proba(X_te)[:, 1]

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
RocCurveDisplay.from_predictions(y_te, proba, ax=axes[0])
PrecisionRecallDisplay.from_predictions(y_te, proba, ax=axes[1])
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
    ]


def _pandas_project_sections() -> list[dict]:
    return [
        {
            "slide_title": "Постановка задачи",
            "kind": "intro",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "Разберём **Titanic (OpenML)**: загрузка, очистка, groupby, merge, pivot, "
                        "экспорт инсайтов и подготовка данных для sklearn Pipeline."
                    ),
                }
            ],
        },
        {
            "slide_title": "Загрузка и первичный осмотр",
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

np.random.seed(42)
sns.set_theme(style="whitegrid", font_scale=1.05)

raw = fetch_openml("titanic", version=1, as_frame=True, parser="auto")
df = raw.frame.copy()
df["Survived"] = df["survived"].astype(int)
df["Pclass"] = df["pclass"].astype(int)
df["Age"] = pd.to_numeric(df["age"], errors="coerce")
df["Fare"] = pd.to_numeric(df["fare"], errors="coerce")
df["Sex"] = df["sex"].astype(str)
df["Embarked"] = df["embarked"].astype(str)

print(f"Объектов: {len(df)}")
display(df.head())
print("Пропуски:\\n", df[["Age", "Fare", "Embarked"]].isna().sum())
""",
                },
            ],
        },
        {
            "slide_title": "Очистка и типы",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
df_clean = df.copy()
df_clean["Age"] = df_clean["Age"].fillna(df_clean.groupby("Pclass")["Age"].transform("median"))
df_clean["Embarked"] = df_clean["Embarked"].fillna(df_clean["Embarked"].mode()[0])
df_clean["Sex"] = df_clean["Sex"].astype("category")
print("Пропуски Age после impute:", df_clean["Age"].isna().sum())
""",
                },
            ],
        },
        {
            "slide_title": "groupby и агрегаты",
            "kind": "viz",
            "cells": [
                {
                    "type": "code",
                    "source": """\
summary = df_clean.groupby(["Pclass", "Sex"]).agg(
    count=("Survived", "size"),
    survival_rate=("Survived", "mean"),
    avg_fare=("Fare", "mean"),
).round(3)
display(summary)

summary.reset_index().pivot(index="Pclass", columns="Sex", values="survival_rate").plot(
    kind="bar", figsize=(7, 4), title="Доля выживших по классу и полу"
)
plt.ylabel("survival_rate")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "merge справочника",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
ports = pd.DataFrame({
    "Embarked": ["S", "C", "Q"],
    "port_name": ["Southampton", "Cherbourg", "Queenstown"],
})
df_ports = pd.merge(df_clean, ports, on="Embarked", how="left")
df_ports.groupby("port_name")["Survived"].mean().sort_values(ascending=False)
""",
                },
            ],
        },
        {
            "slide_title": "pivot_table и инсайты",
            "kind": "viz",
            "cells": [
                {
                    "type": "code",
                    "source": """\
pt = df_clean.pivot_table(values="Survived", index="Pclass", columns="Sex", aggfunc="mean")
display(pt.round(2))
print("Инсайт: женщины 1 класса выживали чаще всего")
""",
                },
            ],
        },
        {
            "slide_title": "Экспорт и Pipeline",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

feature_cols = ["Pclass", "Age", "Fare", "Sex", "Embarked"]
X = df_clean[feature_cols]
y = df_clean["Survived"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

preprocess = ColumnTransformer([
    ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), ["Pclass", "Age", "Fare"]),
    ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("ohe", OneHotEncoder(handle_unknown="ignore"))]), ["Sex", "Embarked"]),
])
pipe = Pipeline([("prep", preprocess), ("model", LogisticRegression(max_iter=500, random_state=42))])
pipe.fit(X_train, y_train)
print(f"Test accuracy: {pipe.score(X_test, y_test):.3f}")

insights = summary.reset_index()
insights.to_csv("titanic_groupby_summary.csv", index=False)
print("Сводка сохранена в titanic_groupby_summary.csv")
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
                        "1. `fetch_openml` → `head/info/describe`.\n"
                        "2. Пропуски — осмысленный impute (по группе или median).\n"
                        "3. groupby + pivot — инсайты до модели.\n"
                        "4. merge справочников по ключу.\n"
                        "5. Pipeline после train_test_split.\n"
                        "6. Экспорт агрегатов для отчёта."
                    ),
                }
            ],
        },
    ]


def _viz_project_sections() -> list[dict]:
    return [
        {
            "slide_title": "Постановка задачи",
            "kind": "intro",
            "cells": [
                {
                    "type": "markdown",
                    "source": (
                        "EDA **Titanic** одним набором графиков: line/scatter/bar/hist/box, "
                        "seaborn, heatmap, категориальные plot, subplots — все темы урока в одном сценарии."
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

raw = fetch_openml("titanic", version=1, as_frame=True, parser="auto")
df = raw.frame.copy()
df["Survived"] = df["survived"].astype(int)
df["Pclass"] = df["pclass"].astype(int)
df["Age"] = pd.to_numeric(df["age"], errors="coerce")
df["Fare"] = pd.to_numeric(df["fare"], errors="coerce")
df["Sex"] = df["sex"]
print(df.shape)
df.head()
""",
                },
            ],
        },
        {
            "slide_title": "Распределения: hist и box",
            "kind": "viz",
            "cells": [
                {
                    "type": "code",
                    "source": """\
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].hist(df["Age"].dropna(), bins=30, color="steelblue", edgecolor="white")
axes[0].set_xlabel("Age")
axes[0].set_title("Histogram возраста")
sns.boxplot(data=df, x="Pclass", y="Fare", hue="Pclass", ax=axes[1], palette="Blues", legend=False)
axes[1].set_title("Boxplot Fare по классу")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Scatter и bar",
            "kind": "viz",
            "cells": [
                {
                    "type": "code",
                    "source": """\
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for survived, color, label in [(0, "crimson", "не выжил"), (1, "steelblue", "выжил")]:
    sub = df[df["Survived"] == survived]
    axes[0].scatter(sub["Age"], sub["Fare"], alpha=0.35, s=15, c=color, label=label)
axes[0].set_xlabel("Age")
axes[0].set_ylabel("Fare")
axes[0].legend()
axes[0].set_title("Scatter Age vs Fare")

rates = df.groupby("Pclass")["Survived"].mean()
axes[1].bar(rates.index.astype(str), rates.values, color="steelblue")
axes[1].set_ylim(0, 1)
axes[1].set_xlabel("Pclass")
axes[1].set_ylabel("доля выживших")
axes[1].set_title("Bar: survival by class")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Heatmap корреляций",
            "kind": "viz",
            "cells": [
                {
                    "type": "code",
                    "source": """\
num = df[["Survived", "Pclass", "Age", "Fare"]].dropna()
corr = num.corr()
plt.figure(figsize=(5, 4))
sns.heatmap(corr, annot=True, cmap="RdBu_r", center=0, vmin=-1, vmax=1)
plt.title("Корреляции числовых признаков")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Категориальные графики seaborn",
            "kind": "viz",
            "cells": [
                {
                    "type": "code",
                    "source": """\
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
sns.countplot(data=df, x="Sex", hue="Sex", ax=axes[0], palette="Set2", legend=False)
sns.barplot(data=df, x="Sex", y="Survived", hue="Sex", estimator="mean", ax=axes[1], palette="muted", legend=False)
axes[1].set_ylim(0, 1)
axes[1].set_ylabel("доля выживших")
fig.suptitle("Категориальные plot")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Subplots 2×2 — сводная EDA",
            "kind": "viz",
            "cells": [
                {
                    "type": "code",
                    "source": """\
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
axes[0, 0].hist(df["Fare"].dropna(), bins=40, color="steelblue", edgecolor="white")
axes[0, 0].set_title("hist Fare")
axes[0, 1].scatter(df["Age"], df["Fare"], c=df["Survived"], alpha=0.3, s=10, cmap="coolwarm")
axes[0, 1].set_title("scatter c=Survived")
df["Survived"].value_counts().plot(kind="bar", ax=axes[1, 0], color=["crimson", "steelblue"])
axes[1, 0].set_title("bar Survived")
sns.boxplot(data=df, x="Sex", y="Age", hue="Sex", ax=axes[1, 1], palette="pastel", legend=False)
axes[1, 1].set_title("box Age by Sex")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "ML-диагностика: остатки и ROC",
            "kind": "viz",
            "cells": [
                {
                    "type": "code",
                    "source": """\
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import RocCurveDisplay

X = df[["Pclass", "Age", "Fare"]]
y = df["Survived"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

pipe = make_pipeline(
    SimpleImputer(strategy="median"),
    StandardScaler(),
    LogisticRegression(max_iter=500, random_state=42),
)
pipe.fit(X_train, y_train)
proba = pipe.predict_proba(X_test)[:, 1]

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
residual_proxy = y_test.values - proba
axes[0].scatter(proba, residual_proxy, alpha=0.5)
axes[0].axhline(0, color="crimson", ls="--")
axes[0].set_xlabel("P(survive)")
axes[0].set_ylabel("y - proba")
axes[0].set_title("Диагностика вероятностей")
RocCurveDisplay.from_predictions(y_test, proba, ax=axes[1])
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
                        "1. Один датасет — все типы графиков.\n"
                        "2. Bar chart — ось Y с нуля.\n"
                        "3. Heatmap для corr; countplot/barplot для категорий.\n"
                        "4. subplots 2×2 для компактной EDA.\n"
                        "5. После модели — residual-style plot и ROC.\n"
                        "6. Подписи осей на русском/английском последовательно."
                    ),
                }
            ],
        },
    ]


def build_all() -> None:
    jobs = [
        (ROOT / "lessons" / "pandas", "Pandas", _pandas_code_sections(), _pandas_project_sections(), "Pandas — мини-проект"),
        (ROOT / "lessons" / "vizualizatsiya", "Визуализация", _viz_code_sections(), _viz_project_sections(), "Визуализация — мини-проект"),
    ]
    for lesson_dir, topic, code_sections, proj_sections, proj_title in jobs:
        code_nb = build_ipynb(code_sections, topic=topic)
        save_ipynb(lesson_dir / "code.ipynb", code_nb)
        proj_nb = build_ipynb(proj_sections, topic=proj_title)
        proj_nb["cells"][0]["source"] = [
            f"# {proj_title}\n",
            "\n",
            "Сквозной мини-проект на реальных данных. Повторяет ключевые темы урока.\n",
        ]
        save_ipynb(lesson_dir / "project.ipynb", proj_nb)
        print(f"{lesson_dir.name}: code {len(code_sections)} sections, project {len(proj_sections)} sections")


if __name__ == "__main__":
    build_all()
