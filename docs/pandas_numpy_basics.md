# Базовые pandas/numpy-конструкции для ML-ноутбуков

## Зачем

Этот справочник задаёт общий язык кода для `code.ipynb` и `project.ipynb`: короткие, понятные pandas/numpy-паттерны для типичных ML-подзадач. Он практический, а не исчерпывающий.

Во всех ноутбуках предполагается одна первая code-ячейка `# Setup`:

```python
%matplotlib inline

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(42)
```

Дальше импорты `pandas`/`numpy`, seed и `%matplotlib inline` не повторяются.

## Загрузка и первичный осмотр

```python
df = pd.read_csv("data.csv")
df.head()
```

```python
print(df.shape)
df.info()
df.describe().round(2)
```

```python
df.columns.tolist()
df["target"].value_counts(dropna=False)
```

## Выбор столбцов и строк

```python
num_cols = ["age", "income", "score"]
cat_cols = ["city", "segment"]

X = df[num_cols + cat_cols]
y = df["target"]
```

```python
df.loc[df["age"] >= 18, ["age", "income"]].head()
```

```python
cols = df.select_dtypes(include="number").columns
df[cols].head()
```

## Пропуски

```python
df.isna().sum().sort_values(ascending=False)
```

```python
df["age"] = df["age"].fillna(df["age"].median())
df["city"] = df["city"].fillna("unknown")
```

```python
df_clean = df.dropna(subset=["target"]).copy()
```

## Приведение типов

```python
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["date"] = pd.to_datetime(df["date"], errors="coerce")
```

```python
df["target"] = df["target"].astype(int)
df["city"] = df["city"].astype("category")
```

## Подготовка категориальных признаков

```python
df["city"] = df["city"].fillna("unknown")
df["city_code"] = df["city"].astype("category").cat.codes
```

```python
df_model = pd.get_dummies(df, columns=["city", "segment"], drop_first=True)
```

```python
counts = df["city"].value_counts()
popular = counts[counts >= 20].index
df["city_short"] = np.where(df["city"].isin(popular), df["city"], "other")
```

## Числовые признаки

```python
df["income_log"] = np.log1p(df["income"])
df["rooms_per_person"] = df["rooms"] / df["people"].clip(lower=1)
```

```python
df["age_bin"] = pd.cut(df["age"], bins=[0, 18, 35, 60, 100])
df["is_high_income"] = np.where(df["income"] > df["income"].median(), 1, 0)
```

```python
df["score_z"] = (df["score"] - df["score"].mean()) / df["score"].std()
```

## Фильтрация и выбросы

```python
q1 = df["income"].quantile(0.25)
q3 = df["income"].quantile(0.75)
iqr = q3 - q1

df_clean = df[df["income"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)].copy()
```

```python
upper = df["income"].quantile(0.99)
df["income_clip"] = df["income"].clip(upper=upper)
```

```python
df = df[df["target"].notna()].copy()
df = df[df["income"] > 0].copy()
```

## X/y и train/test-friendly подготовка

```python
target_col = "target"
feature_cols = [c for c in df.columns if c != target_col]

X = df[feature_cols]
y = df[target_col]
```

```python
num_cols = X.select_dtypes(include="number").columns.tolist()
cat_cols = X.select_dtypes(exclude="number").columns.tolist()
```

```python
X_np = X[num_cols].to_numpy()
y_np = y.to_numpy()
```

## Агрегации и groupby

```python
df.groupby("segment")["target"].mean().sort_values(ascending=False)
```

```python
summary = df.groupby("segment").agg(
    income_mean=("income", "mean"),
    target_rate=("target", "mean"),
    n=("target", "size"),
)
summary.reset_index()
```

```python
df["income_vs_segment"] = df["income"] - df.groupby("segment")["income"].transform("mean")
```

## Join, merge, map

```python
city_income = df.groupby("city")["income"].mean()
df["city_income_mean"] = df["city"].map(city_income)
```

```python
lookup = pd.DataFrame({"city": ["Moscow", "Kazan"], "region": ["Center", "Volga"]})
df = df.merge(lookup, on="city", how="left")
```

```python
label_map = {"yes": 1, "no": 0}
df["target"] = df["target"].map(label_map)
```

## Сортировка и ранжирование

```python
df.sort_values("income", ascending=False).head(10)
```

```python
df["income_rank"] = df["income"].rank(method="dense", ascending=False)
```

```python
top_segments = df["segment"].value_counts().head(5).index
df_top = df[df["segment"].isin(top_segments)].copy()
```

## Подготовка к масштабированию и numpy

```python
X_num = df[num_cols].fillna(df[num_cols].median())
X_arr = X_num.to_numpy()
```

```python
means = X_arr.mean(axis=0)
stds = X_arr.std(axis=0)
X_scaled = (X_arr - means) / stds
```

```python
y_arr = y.to_numpy().reshape(-1, 1)
```

## Векторные вычисления numpy

```python
df["risk"] = np.where(df["score"] > 0.7, "high", "low")
df["score_clip"] = np.clip(df["score"], 0, 1)
```

```python
df["income_log"] = np.log1p(df["income"])
df["distance_sqrt"] = np.sqrt(df["distance"])
```

```python
mean = np.mean(y_np)
std = np.std(y_np)
```

## Простые метрики без sklearn

```python
error = y_true - y_pred
mae = np.mean(np.abs(error))
rmse = np.sqrt(np.mean(error ** 2))
```

```python
accuracy = np.mean(y_true == y_pred)
```

```python
tp = np.sum((y_true == 1) & (y_pred == 1))
fp = np.sum((y_true == 0) & (y_pred == 1))
fn = np.sum((y_true == 1) & (y_pred == 0))

precision = tp / (tp + fp)
recall = tp / (tp + fn)
```

## Подготовка к графикам

```python
df["segment"].value_counts().plot(kind="bar")
plt.show()
```

```python
df["income"].hist(bins=30)
plt.show()
```

```python
corr = df[num_cols + ["target"]].corr().round(2)
corr
```

```python
bins = pd.cut(df["age"], bins=[0, 18, 35, 60, 100])
df.groupby(bins)["target"].mean()
```

## Перед коммитом кода ноутбука

1. В ноутбуке есть одна setup-ячейка; импорты и seed не повторяются ниже.
2. Ячейки выполняются сверху вниз без скрытых переменных.
3. Примеры используют базовые конструкции из этого справочника, если урок не требует более сложного API.
4. `project.ipynb` сохраняет непрерывный сценарий: один датасет, один test-set, явные решения между этапами.
5. Код не раздувает урок: лучше 5 понятных строк, чем универсальная функция на 30 строк.
