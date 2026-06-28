"""Курируемые code_examples по (lesson_dir.name, slide.title)."""

from __future__ import annotations


def _ex(source: str, caption: str | None = None) -> dict:
    item: dict = {"source": source.strip()}
    if caption:
        item["caption"] = caption
    return item


BOOTSTRAP: dict[tuple[str, str], list[dict]] = {
    # --- lineynaya_regressiya (5) ---
    ("lineynaya_regressiya", "Как компьютер ищет минимум?"): [
        _ex(
            "from sklearn.linear_model import LinearRegression\n"
            "model = LinearRegression()  # solver='linalg' по умолчанию\n"
            "model.fit(X_train, y_train)\n"
            "y_pred = model.predict(X_test)",
            "МНК через LinearRegression",
        ),
    ],
    ("lineynaya_regressiya", "Предобработка: масштабирование и категории"): [
        _ex(
            "prep = ColumnTransformer([('num', StandardScaler(), num_cols), ('cat', OneHotEncoder(), cat_cols)])\n"
            "X_scaled = prep.fit_transform(X_train)",
            "Числа + категории",
        ),
    ],
    ("lineynaya_regressiya", "Переобучение и разделение train/test"): [
        _ex(
            "X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)\n"
            "model.fit(X_tr, y_tr)  # метрики только на X_te",
            "Отложенная выборка",
        ),
    ],
    ("lineynaya_regressiya", "Метрики качества регрессии"): [
        _ex(
            "mae = mean_absolute_error(y_te, y_pred)\n"
            "r2 = r2_score(y_te, y_pred)\n"
            "print(f'MAE={mae:.2f}, R²={r2:.3f}')",
            "MAE и R²",
        ),
    ],
    ("lineynaya_regressiya", "sklearn и защита от утечек данных"): [
        _ex(
            "pipe = Pipeline([('scaler', StandardScaler()), ('reg', LinearRegression())])\n"
            "pipe.fit(X_train, y_train)",
            "Pipeline без утечки",
        ),
    ],
    # --- logisticheskaya_regressiya (9) ---
    ("logisticheskaya_regressiya", "Почему линейная регрессия не подходит?"): [
        _ex(
            "from sklearn.linear_model import LinearRegression\n"
            "lr = LinearRegression().fit(X, y_binary)\n"
            "pred = lr.predict(X_new)\n"
            "print(pred.min(), pred.max())  # часто вне [0, 1]",
            "МНК на классах 0/1",
        ),
    ],
    ("logisticheskaya_regressiya", "Сигмоида: сжатие выхода в [0, 1]"): [
        _ex(
            "import numpy as np\n"
            "def sigmoid(z):\n"
            "    return 1 / (1 + np.exp(-z))\n"
            "z = np.linspace(-6, 6, 100)\n"
            "p = sigmoid(z)  # всегда в (0, 1)",
            "Функция сигмоиды",
        ),
    ],
    ("logisticheskaya_regressiya", "LogLoss (бинарная кросс-энтропия)"): [
        _ex(
            "from sklearn.metrics import log_loss\n"
            "y_true = [0, 1, 1, 0]\n"
            "y_prob = [0.1, 0.9, 0.8, 0.3]\n"
            "loss = log_loss(y_true, y_prob)\n"
            "print(f'LogLoss = {loss:.3f}')",
            "Штраф за уверенные ошибки",
        ),
    ],
    ("logisticheskaya_regressiya", "Обучение: градиент и оптимизация"): [
        _ex(
            "from sklearn.linear_model import LogisticRegression\n"
            "clf = LogisticRegression(max_iter=1000, random_state=42)\n"
            "clf.fit(X_train, y_train)\n"
            "proba = clf.predict_proba(X_test)[:, 1]",
            "Оптимизация в sklearn",
        ),
    ],
    ("logisticheskaya_regressiya", "ROC, AUC-ROC и PR-кривая"): [
        _ex(
            "from sklearn.metrics import roc_curve, auc\n"
            "fpr, tpr, _ = roc_curve(y_test, y_score)\n"
            "roc_auc = auc(fpr, tpr)\n"
            "print(f'AUC-ROC = {roc_auc:.3f}')",
            "ROC-кривая",
        ),
    ],
    ("logisticheskaya_regressiya", "Логистическая регрессия в sklearn"): [
        _ex(
            "from sklearn.linear_model import LogisticRegression\n"
            "clf = LogisticRegression(C=1.0, random_state=42)\n"
            "clf.fit(X_train, y_train)\n"
            "y_pred = clf.predict(X_test)",
            "Базовый классификатор",
        ),
    ],
    ("logisticheskaya_regressiya", "Несбалансированные данные на практике"): [
        _ex(
            "clf = LogisticRegression(\n"
            "    class_weight='balanced', random_state=42\n"
            ")\n"
            "clf.fit(X_train, y_train)\n"
            "# веса классов подобраны автоматически",
            "class_weight='balanced'",
        ),
    ],
    ("logisticheskaya_regressiya", "Калибровка вероятностей"): [
        _ex(
            "from sklearn.calibration import CalibratedClassifierCV\n"
            "cal = CalibratedClassifierCV(clf, cv=3)\n"
            "cal.fit(X_train, y_train)\n"
            "p_cal = cal.predict_proba(X_test)[:, 1]",
            "Калибровка вероятностей",
        ),
    ],
    ("logisticheskaya_regressiya", "Ограничения и связь с нейросетями"): [
        _ex(
            "from sklearn.neural_network import MLPClassifier\n"
            "mlp = MLPClassifier(hidden_layer_sizes=(8,), max_iter=500)\n"
            "mlp.fit(X_train, y_train)\n"
            "# один скрытый слой ≈ нелинейная логистическая",
            "MLP как обобщение",
        ),
    ],
    # --- derevo_resheniy (10 практических слайдов) ---
    ("derevo_resheniy", "Бинарная классификация деревом"): [
        _ex(
            "from sklearn.datasets import load_iris\n"
            "X, y = load_iris(return_X_y=True)\n"
            "X, y = X[y != 2], (y[y != 2] == 0).astype(int)\n"
            "# бинарная задача: setosa vs остальные",
            "Два класса из iris",
        ),
    ],
    ("derevo_resheniy", "Энтропия и индекс Джини"): [
        _ex(
            "from sklearn.tree import DecisionTreeClassifier\n"
            "clf = DecisionTreeClassifier(criterion='gini')\n"
            "clf_ent = DecisionTreeClassifier(criterion='entropy')\n"
            "# сравните деревья на одних данных",
            "Gini vs entropy",
        ),
    ],
    ("derevo_resheniy", "Оценка качества дерева"): [
        _ex(
            "from sklearn.metrics import accuracy_score, f1_score\n"
            "y_pred = clf.predict(X_test)\n"
            "print(accuracy_score(y_test, y_pred))\n"
            "print(f1_score(y_test, y_pred, average='macro'))",
            "Accuracy и F1",
        ),
    ],
    ("derevo_resheniy", "Переобучение и его решение"): [
        _ex(
            "clf_deep = DecisionTreeClassifier(max_depth=None)\n"
            "clf_reg = DecisionTreeClassifier(max_depth=3)\n"
            "# глубокое дерево: высокий train, низкий test",
            "Ограничение max_depth",
        ),
    ],
    ("derevo_resheniy", "Дерево решений в sklearn"): [
        _ex(
            "from sklearn.tree import DecisionTreeClassifier\n"
            "clf = DecisionTreeClassifier(max_depth=3, random_state=42)\n"
            "clf.fit(X_train, y_train)\n"
            "clf.predict(X_test)",
            "DecisionTreeClassifier",
        ),
    ],
    ("derevo_resheniy", "Интерпретируемость и важность признаков"): [
        _ex(
            "import pandas as pd\n"
            "imp = pd.Series(clf.feature_importances_, index=feature_names)\n"
            "imp.sort_values(ascending=False).head()",
            "feature_importances_",
        ),
    ],
    ("derevo_resheniy", "Дерево решений для регрессии"): [
        _ex(
            "from sklearn.tree import DecisionTreeRegressor\n"
            "reg = DecisionTreeRegressor(max_depth=4, random_state=42)\n"
            "reg.fit(X_train, y_train)\n"
            "reg.predict(X_test)",
            "DecisionTreeRegressor",
        ),
    ],
    ("derevo_resheniy", "Визуализация деревьев в sklearn"): [
        _ex(
            "from sklearn.tree import plot_tree\n"
            "import matplotlib.pyplot as plt\n"
            "plot_tree(clf, feature_names=names, filled=True)\n"
            "plt.show()",
            "plot_tree",
        ),
    ],
    ("derevo_resheniy", "Границы решения: оси-параллельные прямоугольники"): [
        _ex(
            "import numpy as np\n"
            "xx, yy = np.meshgrid(\n"
            "    np.linspace(x.min(), x.max(), 200),\n"
            "    np.linspace(y.min(), y.max(), 200),\n"
            ")\n"
            "Z = clf.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)",
            "Сетка для границы",
        ),
    ],
    ("derevo_resheniy", "Какая предобработка нужна деревьям?"): [
        _ex(
            "from sklearn.tree import DecisionTreeClassifier\n"
            "# масштабирование не обязательно\n"
            "clf = DecisionTreeClassifier(random_state=42)\n"
            "clf.fit(X_raw, y)  # можно на исходных признаках",
            "Без StandardScaler",
        ),
    ],
    # --- pandas (23) ---
    ("pandas", "Индекс — это не «номер строки», а ключ"): [
        _ex(
            "import pandas as pd\n"
            "df = pd.DataFrame({'a': [1, 2]}, index=['x', 'y'])\n"
            "df.loc['x']      # по метке\n"
            "df.iloc[0]       # по позиции",
            "Метка vs позиция",
        ),
    ],
    ("pandas", "Булева индексация — магия numpy внутри pandas"): [
        _ex(
            "mask = df['age'] > 18\n"
            "adults = df[mask]           # фильтр булевой маской\n"
            "df.loc[df['city'] == 'MSK'] # то же через loc",
            "Фильтрация строк",
        ),
    ],
    ("pandas", "Три способа обратиться к данным: `[]`, `.loc`, `.iloc`"): [
        _ex(
            "col = df['price']          # столбец\n"
            "cell = df.loc[10, 'price'] # по метке индекса\n"
            "cell = df.iloc[0, 2]       # по позиции (0, 2)",
            "[] / loc / iloc",
        ),
    ],
    ("pandas", "Самая большая боль: SettingWithCopyWarning"): [
        _ex(
            "df2 = df[df['active']].copy()  # явная копия\n"
            "df2.loc[:, 'score'] = 0        # без предупреждения\n"
            "# без .copy() — риск записи во view",
            "copy() перед присваиванием",
        ),
    ],
    ("pandas", "Пропуски: NaN, None, NaT и эволюция типов"): [
        _ex(
            "df['col'].isna().sum()          # число пропусков\n"
            "df['col'].fillna(df['col'].median())\n"
            "df = df.dropna(subset=['target'])",
            "isna / fillna / dropna",
        ),
    ],
    ("pandas", "Базовая аналитика: `value_counts()`, `nunique()`, `corr()`"): [
        _ex(
            "df['category'].value_counts()\n"
            "df['user_id'].nunique()\n"
            "df[numeric_cols].corr()['target'].sort_values()",
            "Частоты и корреляции",
        ),
    ],
    ("pandas", "GroupBy: две операции, которые должен знать ML-инженер"): [
        _ex(
            "df.groupby('city')['sales'].agg(['mean', 'count'])\n"
            "df.groupby('date')['amount'].sum().reset_index()",
            "groupby + agg",
        ),
    ],
    ("pandas", "MultiIndex: иерархические индексы после groupby"): [
        _ex(
            "g = df.groupby(['city', 'year'])['sales'].mean()\n"
            "g.loc['MSK']          # срез по первому уровню\n"
            "g.reset_index()       # обратно в таблицу",
            "MultiIndex после groupby",
        ),
    ],
    ("pandas", "Категории: типы кодирования и когда что применять"): [
        _ex(
            "df['color'] = df['color'].astype('category')\n"
            "df['color'].cat.codes   # целые коды\n"
            "pd.get_dummies(df, columns=['color'])",
            "category и get_dummies",
        ),
    ],
    ("pandas", "Быстрый Feature Engineering: условия, биннинг и отсечение"): [
        _ex(
            "df['bucket'] = pd.cut(df['age'], bins=[0, 18, 65, 100])\n"
            "df['flag'] = (df['score'] > 0.5).astype(int)\n"
            "df = df[df['amount'] > 0]",
            "cut и условия",
        ),
    ],
    ("pandas", "Работа с текстом: стринговый аксессор `.str`"): [
        _ex(
            "df['email'].str.lower()\n"
            "df['name'].str.contains('ivan', case=False)\n"
            "df['phone'].str.replace('-', '', regex=False)",
            "Аксессор .str",
        ),
    ],
    ("pandas", "Время как признак: аксессор `.dt`"): [
        _ex(
            "df['ts'] = pd.to_datetime(df['ts'])\n"
            "df['hour'] = df['ts'].dt.hour\n"
            "df['weekday'] = df['ts'].dt.dayofweek",
            "Аксессор .dt",
        ),
    ],
    ("pandas", "pandas <-> numpy: мост между экосистемами"): [
        _ex(
            "arr = df[['x', 'y']].to_numpy()   # DataFrame → ndarray\n"
            "df2 = pd.DataFrame(arr, columns=['x', 'y'])\n"
            "df.values  # устаревший alias",
            "to_numpy()",
        ),
    ],
    ("pandas", "Опасности склейки таблиц: merge и concat"): [
        _ex(
            "out = pd.merge(users, orders, on='user_id', how='left')\n"
            "wide = pd.concat([df_a, df_b], axis=1)",
            "merge и concat",
        ),
    ],
    ("pandas", "merge_asof: асинхронный join для временных рядов"): [
        _ex(
            "pd.merge_asof(\n"
            "    quotes.sort_values('time'),\n"
            "    trades.sort_values('time'),\n"
            "    on='time', direction='backward',\n"
            ")",
            "Ближайшее прошлое событие",
        ),
    ],
    ("pandas", "pandas <-> sklearn: где возникают проблемы"): [
        _ex(
            "X = df.drop(columns=['target'])\n"
            "y = df['target']\n"
            "model.fit(X.select_dtypes('number'), y)",
            "Только числовые столбцы",
        ),
    ],
    ("pandas", "pandas <-> PyTorch: создание Dataset"): [
        _ex(
            "import torch\n"
            "X_t = torch.tensor(df[cols].to_numpy(), dtype=torch.float32)\n"
            "y_t = torch.tensor(df['y'].to_numpy())",
            "DataFrame → tensor",
        ),
    ],
    ("pandas", "Data Leakage: где прячется в pandas"): [
        _ex(
            "from sklearn.model_selection import train_test_split\n"
            "train, test = train_test_split(df, random_state=42)\n"
            "mu = train['x'].mean()  # статистика только с train\n"
            "test['x'] = test['x'].fillna(mu)",
            "Impute после split",
        ),
    ],
    ("pandas", "Итеративная обработка: когда файл не влезает в RAM"): [
        _ex(
            "chunks = pd.read_csv('big.csv', chunksize=100_000)\n"
            "for chunk in chunks:\n"
            "    process(chunk)  # обработка по частям",
            "read_csv(chunksize=...)",
        ),
    ],
    ("pandas", "Производительность: когда pandas «не тянет»"): [
        _ex(
            "df['x'] * 2              # векторизация — быстро\n"
            "# for i in range(len(df)): ...  # цикл — медленно",
            "Векторизация vs цикл",
        ),
    ],
    ("pandas", "Оптимизация памяти: downcasting типов"): [
        _ex(
            "df['small_int'] = pd.to_numeric(df['small_int'], downcast='integer')\n"
            "df['category'] = df['category'].astype('category')",
            "Меньше байт на ячейку",
        ),
    ],
    ("pandas", "Форматы хранения: Смерть CSV и восстание Parquet"): [
        _ex(
            "df.to_parquet('data.parquet', index=False)\n"
            "df = pd.read_parquet('data.parquet')\n"
            "# типы и сжатие сохраняются",
            "Parquet вместо CSV",
        ),
    ],
    ("pandas", "Гигиена памяти в Jupyter: борьба с OOM"): [
        _ex(
            "del big_df\n"
            "import gc; gc.collect()\n"
            "df = df[['need', 'only', 'cols']].copy()",
            "del + gc.collect()",
        ),
    ],
    # --- vizualizatsiya (12) ---
    ("vizualizatsiya", "Matplotlib: figure и axes"): [
        _ex(
            "import matplotlib.pyplot as plt\n"
            "fig, ax = plt.subplots(figsize=(6, 4))\n"
            "ax.plot([1, 2, 3], [1, 4, 9])\n"
            "ax.set_xlabel('x'); ax.set_ylabel('y')",
            "OO-стиль matplotlib",
        ),
    ],
    ("vizualizatsiya", "Line plot"): [
        _ex(
            "ax.plot(x, y, label='train', color='C0')\n"
            "ax.plot(x, y_test, label='test', linestyle='--')\n"
            "ax.legend()",
            "Несколько линий",
        ),
    ],
    ("vizualizatsiya", "Scatter plot"): [
        _ex(
            "ax.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis', alpha=0.7)\n"
            "ax.set_xlabel('feature 1'); ax.set_ylabel('feature 2')",
            "Классы цветом",
        ),
    ],
    ("vizualizatsiya", "Bar chart"): [
        _ex(
            "ax.bar(categories, values, color='steelblue')\n"
            "ax.set_ylabel('count')\n"
            "plt.xticks(rotation=45)",
            "Столбчатая диаграмма",
        ),
    ],
    ("vizualizatsiya", "Histogram и box plot"): [
        _ex(
            "ax.hist(data, bins=30, edgecolor='white')\n"
            "ax.boxplot(data, vert=True)\n"
            "ax.set_title('Распределение')",
            "hist + boxplot",
        ),
    ],
    ("vizualizatsiya", "Seaborn: высокоуровневые графики"): [
        _ex(
            "import seaborn as sns\n"
            "sns.scatterplot(data=df, x='x', y='y', hue='class')\n"
            "sns.regplot(data=df, x='x', y='y', scatter_kws={'alpha': 0.5})",
            "scatterplot / regplot",
        ),
    ],
    ("vizualizatsiya", "Подписи, легенды и цвет"): [
        _ex(
            "ax.set_title('ROC-кривая', fontsize=14)\n"
            "ax.legend(loc='lower right')\n"
            "ax.grid(True, alpha=0.3)",
            "title / legend / grid",
        ),
    ],
    ("vizualizatsiya", "Несколько subplots"): [
        _ex(
            "fig, axes = plt.subplots(2, 2, figsize=(8, 6))\n"
            "axes[0, 0].hist(a); axes[0, 1].scatter(x, y)\n"
            "fig.tight_layout()",
            "Сетка 2×2",
        ),
    ],
    ("vizualizatsiya", "Heatmap и корреляции"): [
        _ex(
            "import seaborn as sns\n"
            "corr = df.corr(numeric_only=True)\n"
            "sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1)",
            "heatmap корреляций",
        ),
    ],
    ("vizualizatsiya", "Категориальные графики"): [
        _ex(
            "sns.countplot(data=df, x='category', order=df['category'].value_counts().index)\n"
            "plt.xticks(rotation=30)",
            "countplot",
        ),
    ],
    ("vizualizatsiya", "Визуализация для ML: остатки"): [
        _ex(
            "residuals = y_test - y_pred\n"
            "ax.scatter(y_pred, residuals, alpha=0.6)\n"
            "ax.axhline(0, color='red', linestyle='--')",
            "Остатки vs предсказание",
        ),
    ],
    ("vizualizatsiya", "Визуализация для ML: ROC и PR"): [
        _ex(
            "from sklearn.metrics import RocCurveDisplay\n"
            "RocCurveDisplay.from_predictions(y_test, y_score)\n"
            "plt.title('ROC')",
            "RocCurveDisplay",
        ),
    ],
}


def get_bootstrap_examples(lesson_name: str, slide_title: str) -> list[dict] | None:
    key = (lesson_name, slide_title)
    examples = BOOTSTRAP.get(key)
    if examples is None:
        return None
    return [dict(ex) for ex in examples]


def list_bootstrap_titles(lesson_name: str) -> list[str]:
    return [title for (lesson, title) in BOOTSTRAP if lesson == lesson_name]
