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
            "slide_title": "Индекс — это не «номер строки», а ключ",
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
df["Embarked"] = df["embarked"].astype(str)

filtered = df[df["Age"] > 30]
print("Индекс после фильтра (рваный):", filtered.index[:5].tolist())
flat = filtered.reset_index(drop=True)
print("После reset_index:", flat.index[:5].tolist())
""",
                },
            ],
        },
        {
            "slide_title": "Булева индексация — магия numpy внутри pandas",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
mask_age = df["Age"] > 30
mask_class = df["Pclass"] == 1
mask = mask_age & mask_class  # скобки обязательны для составных условий
print("Маска (первые 10):", mask.head(10).tolist())
df.loc[mask, ["Sex", "Age", "Pclass", "Survived"]].head()
""",
                },
            ],
        },
        {
            "slide_title": "Три способа обратиться к данным: `[]`, `.loc`, `.iloc`",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
sample = df.head(8).copy()
sample.index = sample.index * 10 + 5  # нестандартные метки
print("loc по метке 45:", sample.loc[45, "Age"])
print("iloc по позиции 0:", sample.iloc[0]["Age"])
sample.loc[45, "Fare_note"] = "vip"
""",
                },
            ],
        },
        {
            "slide_title": "Самая большая боль: SettingWithCopyWarning",
            "kind": "experiment",
            "cells": [
                {
                    "type": "code",
                    "source": """\
import warnings
warnings.filterwarnings("default", category=pd.errors.SettingWithCopyWarning)

subset = df[df["Age"] > 30]  # может быть view
# subset["flag"] = 1  # раскомментируйте — увидите Warning

subset_copy = df[df["Age"] > 30].copy()
subset_copy["flag"] = 1

df.loc[df["Age"] > 30, "high_age"] = 1
print("Через .loc на оригинале — без неоднозначности")
""",
                },
            ],
        },
        {
            "slide_title": "Пропуски: NaN, None, NaT и эволюция типов",
            "kind": "experiment",
            "cells": [
                {
                    "type": "code",
                    "source": """\
print(df[["Age", "Fare"]].isnull().sum())
s_int = pd.Series([1, 2, None], dtype="Int64")
print("Nullable Int64:", s_int.dtype, s_int.tolist())
""",
                },
            ],
        },
        {
            "slide_title": "Базовая аналитика: `value_counts()`, `nunique()`, `corr()`",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
print(df["Sex"].value_counts())
print("nunique Embarked:", df["Embarked"].nunique())
num = df[["Survived", "Pclass", "Age", "Fare"]].dropna()
print(num.corr().round(2))
""",
                },
            ],
        },
        {
            "slide_title": "GroupBy: две операции, которые должен знать ML-инженер",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
agg = df.groupby("Pclass")["Fare"].mean()
print(agg.round(2))
df = df.copy()
df["fare_vs_class"] = df["Fare"] - df.groupby("Pclass")["Fare"].transform("mean")
df[["Pclass", "Fare", "fare_vs_class"]].head()
""",
                },
            ],
        },
        {
            "slide_title": "MultiIndex: иерархические индексы после groupby",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
mi = df.groupby(["Pclass", "Sex"]).agg({"Fare": "mean", "Age": "median"})
print("MultiIndex:", mi.index.names)
flat = mi.reset_index()
flat.head()
""",
                },
            ],
        },
        {
            "slide_title": "Категории: типы кодирования и когда что применять",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
dummies = pd.get_dummies(df, columns=["Sex", "Embarked"], drop_first=True)
print("OHE столбцы:", [c for c in dummies.columns if c.startswith("Sex") or c.startswith("Embarked")][:4])
cat = df["Sex"].astype("category")
print("Ordinal codes:", cat.cat.codes.head())
""",
                },
            ],
        },
        {
            "slide_title": "Быстрый Feature Engineering: условия, биннинг и отсечение",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
df_fe = df.copy()
df_fe["is_expensive"] = np.where(df_fe["Fare"] > df_fe["Fare"].median(), 1, 0)
df_fe["fare_bin"] = pd.qcut(df_fe["Fare"].fillna(0), q=4, labels=["Q1", "Q2", "Q3", "Q4"])
upper = df_fe["Fare"].quantile(0.99)
df_fe["Fare_clip"] = df_fe["Fare"].clip(upper=upper)
df_fe[["Fare", "Fare_clip", "is_expensive", "fare_bin"]].head()
""",
                },
            ],
        },
        {
            "slide_title": "Работа с текстом: стринговый аксессор `.str`",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
names = df["name"].dropna().head(5)
print("Длины:", names.str.len().tolist())
print("Содержит 'Mr':", names.str.contains("Mr").tolist())
""",
                },
            ],
        },
        {
            "slide_title": "Время как признак: аксессор `.dt`",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
dates = pd.date_range("2023-01-01", periods=5, freq="D")
ts = pd.DataFrame({"date": dates})
ts["dow"] = ts["date"].dt.dayofweek
ts["hour_sin"] = np.sin(2 * np.pi * ts["date"].dt.hour / 24)
ts
""",
                },
            ],
        },
        {
            "slide_title": "pandas <-> numpy: мост между экосистемами",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
X_num = df.select_dtypes(include="number").drop(columns=["Survived"], errors="ignore")
arr = X_num.fillna(0).to_numpy(dtype="float32")
print(arr.shape, arr.dtype)
""",
                },
            ],
        },
        {
            "slide_title": "Опасности склейки таблиц: merge и concat",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
ports = pd.DataFrame({"Embarked": ["S", "C", "Q", "S"], "port": ["Soton", "Cher", "Queen", "Soton_dup"]})
merged = pd.merge(df[["Embarked"]].head(6), ports, on="Embarked", how="left")
print(f"Строк после merge с дублями ключа: {len(merged)}")

left = df.iloc[:3].reset_index(drop=True)
right = df.iloc[5:8].reset_index(drop=True)
pd.concat([left[["Age"]], right[["Fare"]]], axis=1)
""",
                },
            ],
        },
        {
            "slide_title": "merge_asof: асинхронный join для временных рядов",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
tx = pd.DataFrame({"ts": pd.to_datetime(["2024-01-01 10:05", "2024-01-01 10:20", "2024-01-01 10:40"]), "amt": [100, 200, 150]})
rates = pd.DataFrame({"ts": pd.to_datetime(["2024-01-01 10:00", "2024-01-01 10:15", "2024-01-01 10:30"]), "rate": [1.0, 1.1, 1.2]})
pd.merge_asof(tx.sort_values("ts"), rates.sort_values("ts"), on="ts", direction="backward")
""",
                },
            ],
        },
        {
            "slide_title": "pandas <-> sklearn: где возникают проблемы",
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

features = ["Pclass", "Age", "Fare", "Sex"]
X = df[features]
y = df["Survived"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

prep = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), ["Pclass", "Age", "Fare"]),
    ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")), ("ohe", OneHotEncoder(handle_unknown="ignore"))]), ["Sex"]),
])
pipe = Pipeline([("prep", prep), ("model", LogisticRegression(max_iter=500, random_state=42))])
pipe.fit(X_train, y_train)
print(f"Test accuracy: {pipe.score(X_test, y_test):.3f}")
""",
                },
            ],
        },
        {
            "slide_title": "pandas <-> PyTorch: создание Dataset",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
try:
    import torch
    from torch.utils.data import TensorDataset

    X_np = df[["Pclass", "Age", "Fare"]].fillna(0).to_numpy(dtype="float32")
    y_np = df["Survived"].to_numpy(dtype="float32")
    t_shared = torch.from_numpy(X_np)
    t_copy = torch.tensor(X_np)
    print("from_numpy shares memory:", t_shared.data_ptr() == X_np.__array_interface__["data"][0])
    ds = TensorDataset(t_copy, torch.tensor(y_np))
    print("Dataset size:", len(ds))
except ImportError:
    print("torch не установлен — пропуск демо")
""",
                },
            ],
        },
        {
            "slide_title": "Data Leakage: где прячется в pandas",
            "kind": "experiment",
            "cells": [
                {
                    "type": "code",
                    "source": """\
# НЕПРАВИЛЬНО: статистика по всему датасету до split
# df["Age"].fillna(df["Age"].mean())

from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer

X = df[["Age", "Fare"]]
y = df["Survived"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=42)
imp = SimpleImputer(strategy="median")
X_tr_imp = imp.fit_transform(X_tr)
X_te_imp = imp.transform(X_te)  # медиана только с train
print("NaN после imputer (train):", np.isnan(X_tr_imp).any())
""",
                },
            ],
        },
        {
            "slide_title": "Итеративная обработка: когда файл не влезает в RAM",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
import io
buf = io.StringIO("\\n".join([f"{i},{i*2}" for i in range(1000)]))
buf.seek(0)
chunks = pd.read_csv(buf, names=["a", "b"], chunksize=200)
total = sum(chunk["a"].sum() for chunk in chunks)
print("Сумма a по chunks:", total)
""",
                },
            ],
        },
        {
            "slide_title": "Производительность: когда pandas «не тянет»",
            "kind": "experiment",
            "cells": [
                {
                    "type": "code",
                    "source": """\
import time
s = pd.Series(range(100_000))
t0 = time.perf_counter(); _ = s.apply(lambda x: x * 2); t1 = time.perf_counter()
t2 = time.perf_counter(); _ = s * 2; t3 = time.perf_counter()
print(f"apply: {t1-t0:.3f}s, vectorized: {t3-t2:.3f}s")
""",
                },
            ],
        },
        {
            "slide_title": "Оптимизация памяти: downcasting типов",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
col = df["Sex"].astype(str)
print("object KiB:", col.memory_usage(deep=True) / 1024)
cat = col.astype("category")
print("category KiB:", cat.memory_usage(deep=True) / 1024)
""",
                },
            ],
        },
        {
            "slide_title": "Форматы хранения: Смерть CSV и восстание Parquet",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
import tempfile
from pathlib import Path

tmp = Path(tempfile.mkdtemp())
pq = tmp / "titanic.parquet"
try:
    df.head(100).to_parquet(pq, index=False)
    loaded = pd.read_parquet(pq)
    print("dtypes сохранены:", loaded.dtypes.head(3).tolist())
except ImportError as e:
    print("Parquet требует pyarrow: pip install pyarrow")
    print(e)
""",
                },
            ],
        },
        {
            "slide_title": "Гигиена памяти в Jupyter: борьба с OOM",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
import gc

big = df.copy()
del big
gc.collect()
print("После del + gc.collect()")
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
df["Embarked"] = df["embarked"].astype(str)
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
                        "Сквозной сценарий на **Titanic (OpenML)**: EDA в pandas, индексы и маски, "
                        "groupby/transform, кодирование, merge, Parquet, sklearn Pipeline без утечки."
                    ),
                }
            ],
        },
        {
            "slide_title": "Загрузка и первичный EDA",
            "kind": "eda",
            "cells": [
                {
                    "type": "code",
                    "source": """\
import warnings
warnings.filterwarnings("ignore")

import gc
import seaborn as sns
from sklearn.datasets import fetch_openml

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
df.info()
print(df.describe(include="all").T.head(8))
print("Пропуски:\\n", df[["Age", "Fare", "Embarked"]].isnull().sum())
""",
                },
            ],
        },
        {
            "slide_title": "Аналитика и кардинальность",
            "kind": "eda",
            "cells": [
                {
                    "type": "code",
                    "source": """\
print(df["Sex"].value_counts())
print("nunique name:", df["name"].nunique(), "— почти ID, в модель не берём")
corr = df[["Survived", "Pclass", "Age", "Fare"]].corr()
sns.heatmap(corr, annot=True, cmap="RdBu_r", center=0, vmin=-1, vmax=1)
plt.title("corr() перед моделью")
plt.tight_layout()
plt.show()
""",
                },
            ],
        },
        {
            "slide_title": "Очистка: пропуски и признаки",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
df_clean = df.copy()
df_clean["Age"] = df_clean.groupby("Pclass")["Age"].transform(lambda s: s.fillna(s.median()))
df_clean["Embarked"] = df_clean["Embarked"].fillna(df_clean["Embarked"].mode()[0])
df_clean["Fare"] = df_clean["Fare"].fillna(df_clean.groupby("Pclass")["Fare"].transform("median"))

df_clean["is_expensive"] = np.where(df_clean["Fare"] > df_clean["Fare"].median(), 1, 0)
upper = df_clean["Fare"].quantile(0.99)
df_clean["Fare_clip"] = df_clean["Fare"].clip(upper=upper)
df_clean["fare_dev"] = df_clean["Fare"] - df_clean.groupby("Pclass")["Fare"].transform("mean")
print("Пропуски Age:", df_clean["Age"].isna().sum())
df_clean[["Fare", "Fare_clip", "fare_dev", "is_expensive"]].head()
""",
                },
            ],
        },
        {
            "slide_title": "groupby, MultiIndex и merge",
            "kind": "viz",
            "cells": [
                {
                    "type": "code",
                    "source": """\
summary = df_clean.groupby(["Pclass", "Sex"]).agg(
    n=("Survived", "size"),
    survival=("Survived", "mean"),
    avg_fare=("Fare", "mean"),
).round(3)
print(summary)

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
            "slide_title": "Кодирование и Parquet",
            "kind": "example",
            "cells": [
                {
                    "type": "code",
                    "source": """\
df_model = pd.get_dummies(df_clean, columns=["Sex", "Embarked"], drop_first=True)
feature_cols = ["Pclass", "Age", "Fare_clip", "is_expensive", "fare_dev"] + [
    c for c in df_model.columns if c.startswith("Sex_") or c.startswith("Embarked_")
]
df_model = df_model[feature_cols + ["Survived"]].reset_index(drop=True)

import tempfile
from pathlib import Path
pq_path = Path(tempfile.mkdtemp()) / "titanic_clean.parquet"
try:
    df_model.to_parquet(pq_path, index=False)
    df_loaded = pd.read_parquet(pq_path)
    print("Загружено из Parquet:", df_loaded.shape)
except ImportError:
    csv_path = pq_path.with_suffix(".csv")
    df_model.to_csv(csv_path, index=False)
    df_loaded = pd.read_csv(csv_path)
    print("pyarrow нет — сохранено в CSV:", df_loaded.shape)
""",
                },
            ],
        },
        {
            "slide_title": "train_test_split и Pipeline",
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
from sklearn.metrics import classification_report

X = df_model.drop(columns=["Survived"])
y = df_model["Survived"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=500, random_state=42)),
])
pipe.fit(X_train, y_train)
pred = pipe.predict(X_test)
print(classification_report(y_test, pred, digits=3))

X_np = pipe.named_steps["scaler"].transform(pipe.named_steps["imputer"].transform(X_test))
print("numpy dtype:", X_np.dtype, "NaN:", np.isnan(X_np).any())
""",
                },
            ],
        },
        {
            "slide_title": "Память и чек-лист",
            "kind": "summary",
            "cells": [
                {
                    "type": "code",
                    "source": """\
del df_ports, summary
gc.collect()

print("Чек-лист:")
print("  info/describe/value_counts/corr — EDA")
print("  transform для контекстных признаков")
print("  get_dummies + Parquet для типов")
print("  split до fit-статистик; Pipeline для imputer/scaler")
print("  to_numpy перед sklearn; del + gc перед тяжёлой моделью")
""",
                },
                {
                    "type": "markdown",
                    "source": (
                        "1. EDA: `info`, `describe`, `value_counts`, `corr`.\n"
                        "2. Индексы: `reset_index` после фильтров и перед concat.\n"
                        "3. Пропуски и признаки — осмысленно; clip/qcut/np.where.\n"
                        "4. `groupby` agg + `transform`; merge по уникальному ключу.\n"
                        "5. OHE; промежуточные данные — Parquet.\n"
                        "6. `train_test_split` → Pipeline → numpy → метрики.\n"
                        "7. `del` + `gc.collect()` в Jupyter."
                    ),
                },
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

import seaborn as sns
from sklearn.datasets import fetch_openml

sns.set_theme(style="whitegrid", font_scale=1.05)

raw = fetch_openml("titanic", version=1, as_frame=True, parser="auto")
df = raw.frame.copy()
df["Survived"] = df["survived"].astype(int)
df["Pclass"] = df["pclass"].astype(int)
df["Age"] = pd.to_numeric(df["age"], errors="coerce")
df["Fare"] = pd.to_numeric(df["fare"], errors="coerce")
df["Sex"] = df["sex"]
df["Embarked"] = df["embarked"].astype(str)
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
        if lesson_dir.name == "pandas":
            code_nb["cells"][1]["source"] = [
                "# Setup\n",
                "%matplotlib inline\n",
                "\n",
                "import numpy as np\n",
                "import pandas as pd\n",
                "import matplotlib.pyplot as plt\n",
                "\n",
                "try:\n",
                "    from IPython.display import display\n",
                "except ImportError:\n",
                "    display = print\n",
                "\n",
                "np.random.seed(42)\n",
            ]
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
