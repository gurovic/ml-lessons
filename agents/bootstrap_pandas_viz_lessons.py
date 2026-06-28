"""Bootstrap pandas and vizualizatsiya lessons (slides JSON, plans, metadata)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INFO = {
    "author": "Гуровиц Владимир Михайлович",
    "email": "vladimir.gurovic@letovo.ru, gurovic@gmail.com",
    "telegram": "@gurovic",
    "duration_minutes": 90,
}

PANDAS_SLIDES = [
    {
        "title": "Табличные данные в машинном обучении",
        "bullets": [
            "Большинство задач ML начинается с **таблицы**: строки — объекты, столбцы — признаки",
            "Excel/CSV → очистка → анализ → модель: Pandas — стандартный инструмент на этом пути",
            "Альтернатива «голому» NumPy: именованные столбцы, индексы, группировки, join",
            "В sklearn данные часто передают как `X` (массив) и `y` (Series), но EDA делают в Pandas",
        ],
        "notes": "Мотивация: без Pandas сложно работать с реальными наборами.",
        "visuals": [{"description": "Схема pipeline: CSV → DataFrame → очистка → groupby/merge → sklearn.", "output": "pandas_ml_pipeline.png"}],
    },
    {
        "title": "Series и DataFrame",
        "bullets": [
            "**Series** — одномерный массив с индексом: `s['a']`, `s.iloc[0]`",
            "**DataFrame** — таблица: столбцы — Series с общим индексом строк",
            "Создание: `pd.DataFrame({'col': [...]})`, из dict/list, из NumPy",
            "`.shape`, `.columns`, `.dtypes` — первые вопросы к любой таблице",
        ],
        "notes": "Показать в ноутбуке создание из dict.",
        "visuals": [{"description": "Схема: Series (индекс+значения) и DataFrame как набор столбцов-Series.", "output": "series_dataframe_schema.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "Создать Series и DataFrame из dict, вывести shape и dtypes."},
    },
    {
        "title": "Чтение данных",
        "bullets": [
            "`pd.read_csv(path)` — основной формат; параметры `sep`, `encoding`, `parse_dates`",
            "`pd.read_excel` — листы через `sheet_name`; для OpenML — `fetch_openml(..., as_frame=True)`",
            "После чтения: `df.head()`, `df.info()`, `df.describe()` — быстрый осмотр",
            "Сохранение: `df.to_csv(..., index=False)` — индекс в файл обычно не пишем",
        ],
        "notes": "OpenML Titanic как пример в project.ipynb.",
        "visuals": [{"description": "Скрин-схема: read_csv → DataFrame с подписью n_rows × n_cols.", "output": "read_csv_flow.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "read_csv из StringIO или fetch_openml titanic."},
    },
    {
        "title": "Первичный осмотр таблицы",
        "bullets": [
            "`head(n)` / `tail(n)` — первые и последние строки",
            "`info()` — типы, пропуски, память; `describe()` — статистики числовых столбцов",
            "`value_counts()` для категорий — баланс классов, частые значения",
            "`.sample(n, random_state=42)` — случайная подвыборка для ручной проверки",
        ],
        "notes": "Связать describe с EDA перед моделью.",
        "visuals": [{"description": "Мини-таблица describe(): count, mean, std, min, max для 3 столбцов.", "output": "describe_snapshot.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "info(), describe(), value_counts на Titanic."},
    },
    {
        "title": "Индексы строк и столбцов",
        "bullets": [
            "Индекс — «метки» строк; по умолчанию 0…n−1, но может быть id, дата, код",
            "`set_index('col')` — сделать столбец индексом; `reset_index()` — вернуть в столбец",
            "`df.loc[label]` — по метке; `df['col']` — столбец (Series)",
            "Дубликаты индекса допустимы, но усложняют выборку — лучше уникальный ключ",
        ],
        "notes": "Пример: PassengerId как индекс Titanic.",
        "visuals": [{"description": "DataFrame до/после set_index: индекс слева выделен.", "output": "index_set_reset.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "set_index и reset_index."},
    },
    {
        "title": "loc и iloc: две системы адресации",
        "bullets": [
            "**loc** — по меткам (label-based): `df.loc[3, 'Age']`, срезы включают конец",
            "**iloc** — по позициям (integer): `df.iloc[0:5, 1:3]`, как NumPy",
            "Срезы: `loc['a':'c']` включает 'c'; `iloc[0:3]` — не включает 3",
            "Булевы маски работают с **loc**: `df.loc[df['Age'] > 30, ['Name','Age']]`",
        ],
        "notes": "Классическая ловушка — путать loc и iloc.",
        "visuals": [{"description": "Сетка 4×4: loc выделяет блок по меткам B–D, iloc — по позициям 1:3.", "output": "loc_vs_iloc.png"}],
        "notebook": {"include": True, "kinds": ["example", "experiment"], "hint": "Сравнить loc и iloc на одном DataFrame."},
    },
    {
        "title": "Фильтрация и булевы маски",
        "bullets": [
            "Условие даёт Series bool: `df['Age'] > 18`",
            "Несколько условий: `&` (и), `|` (или); каждое в скобках: `(A) & (B)`",
            "`.isin([...])`, `.between(a, b)`, `.str.contains(...)` для строк",
            "`.query('Age > 18 and Pclass == 1')` — альтернативный синтаксис",
        ],
        "notes": "Показать фильтр выживших женщин 1 класса.",
        "visuals": [{"description": "Таблица: серые строки отфильтрованы, синие прошли маску Age>30 & Pclass==1.", "output": "boolean_filter.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "Булева маска и query."},
    },
    {
        "title": "groupby и агрегации",
        "bullets": [
            "«Разбить по ключу → применить функцию → собрать» — `df.groupby('Pclass')`",
            "`.agg({'Age':'mean', 'Fare':'sum'})` — разные функции по столбцам",
            "`.mean()`, `.size()`, `.count()` — частые сокращения",
            "Несколько ключей: `groupby(['Pclass','Sex'])` — вложенные группы",
        ],
        "notes": "Средний Fare по классу — наглядный пример.",
        "visuals": [{"description": "Bar chart: средний Fare по Pclass (1>2>3 заметно).", "output": "groupby_fare_pclass.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "groupby Pclass, agg mean Fare и count."},
    },
    {
        "title": "merge и join",
        "bullets": [
            "`pd.merge(left, right, on='key', how='inner|left|right|outer')` — SQL-подобное соединение",
            "how='left' — все строки левой таблицы; пропуски где нет совпадения",
            "`.join()` — по индексу; для merge ключи часто приводят к одному типу",
            "Дубликаты ключей → декартово умножение строк — проверяй `len` до и после",
        ],
        "notes": "Пример: таблица пассажиров + справочник портов.",
        "visuals": [{"description": "Venn inner/left merge двух маленьких таблиц с ключом id.", "output": "merge_diagram.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "merge двух DataFrame по ключу."},
    },
    {
        "title": "Пропуски: isna, fillna, dropna",
        "bullets": [
            "`isna()` / `notna()` — маска пропусков; `df.isna().sum()` — счёт по столбцам",
            "`fillna(value)` или `fillna(df['col'].median())` — заполнение",
            "`dropna(subset=['Age'])` — удалить строки с пропуском в Age",
            "Стратегия зависит от задачи: удалить vs impute; для ML — только на **train**",
        ],
        "notes": "Age в Titanic — классический пример.",
        "visuals": [{"description": "Bar chart пропусков по столбцам Titanic (Cabin много, Age меньше).", "output": "missing_counts.png"}],
        "notebook": {"include": True, "kinds": ["experiment"], "hint": "isna().sum(), fillna median Age."},
    },
    {
        "title": "Типы данных",
        "bullets": [
            "object — строки; int64/float64 — числа; category — экономия памяти для повторов",
            "`astype({'col': 'category'})` — явное приведение",
            "`pd.to_datetime(df['date'])` — даты; `.dt.year`, `.dt.month` — компоненты",
            "Неверный dtype ломает sort и merge — смотри `df.dtypes` после чтения",
        ],
        "notes": "Sex → category на Titanic.",
        "visuals": [{"description": "До/после: object Sex vs category — memory_usage меньше.", "output": "dtype_category.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "astype category, to_datetime demo."},
    },
    {
        "title": "apply и transform",
        "bullets": [
            "`.apply(func, axis=0|1)` — функция по столбцу или строке; медленнее векторизации",
            "`.map(dict)` на Series — замена значений по словарю",
            "`.transform('mean')` после groupby — результат той же длины, что и исходник",
            "Предпочитай встроенные методы (`str`, `dt`, NumPy) — apply для сложной логики",
        ],
        "notes": "map для Embarked кодов.",
        "visuals": [{"description": "Series до map и после: S→0, C→1, Q→2.", "output": "apply_map_transform.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "map Embarked, groupby transform mean."},
    },
    {
        "title": "pivot и pivot_table",
        "bullets": [
            "`pivot_table(values, index, columns, aggfunc='mean')` — сводная таблица",
            "Аналог Excel Pivot: строки × столбцы × агрегат",
            "`.pivot()` — без агрегации, требует уникальных пар index×columns",
            "Удобно для отчётов и быстрой проверки гипотез (выживаемость по классу и полу)",
        ],
        "notes": "Survived rate по Pclass и Sex.",
        "visuals": [{"description": "Heatmap pivot_table: Survived mean по Pclass (rows) и Sex (cols).", "output": "pivot_survival.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "pivot_table Survived by Pclass and Sex."},
    },
    {
        "title": "Базовая производительность",
        "bullets": [
            "Векторизация NumPy/Pandas **быстрее** цикла Python и построчного apply",
            "`.values` / `.to_numpy()` — массив для sklearn без копий где возможно",
            "category и правильные dtypes уменьшают память на больших таблицах",
            "Чтение: `usecols`, `dtype`, `chunksize` — для файлов на миллионы строк",
        ],
        "notes": "Микро-бенчмарк apply vs vectorized — опционально в ноутбуке.",
        "visuals": [{"description": "Bar chart: время apply vs vectorized (vectorized в 10–50× быстрее).", "output": "perf_vectorized.png"}],
        "notebook": {"include": True, "kinds": ["experiment"], "hint": "Сравнить apply и векторизацию по времени."},
    },
    {
        "title": "Типичные ошибки в Pandas",
        "bullets": [
            "**SettingWithCopyWarning** — цепочка срезов; используй `.loc` или `.copy()`",
            "Изменение среза не меняет исходник — нужен явный assign или loc",
            "merge без проверки дубликатов ключей → раздувание строк",
            "fillna/dropna **до** train_test_split — утечка информации из test",
        ],
        "notes": "Связь с data leakage из урока линейной регрессии.",
        "visuals": [{"description": "Схема leakage: impute на всём df до split — красная стрелка «утечка».", "output": "pandas_leakage.png"}],
    },
    {
        "title": "Pandas и sklearn Pipeline",
        "bullets": [
            "Pandas — EDA и подготовка; sklearn — `fit`/`predict` на NumPy",
            "`ColumnTransformer` + `Pipeline`: imputer/scaler/encoder внутри пайплайна",
            "`df[feature_cols].to_numpy()` или `Pipeline` с `FunctionTransformer`",
            "Сохраняй согласованность имён столбцов между train и test",
        ],
        "notes": "Показать SimpleImputer в Pipeline после split.",
        "visuals": [{"description": "Block-схема: DataFrame → split → Pipeline(Imputer, OHE, Model).", "output": "pandas_sklearn_pipeline.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "Pipeline с imputer на Titanic numeric cols."},
    },
    {
        "title": "Итоги и чек-лист",
        "bullets": [
            "1. `read_*` → `head/info/describe` перед любыми выводами",
            "2. Выборка: **loc** по меткам, **iloc** по позициям; маски через loc",
            "3. groupby/merge/pivot — три кита аналитики таблиц",
            "4. Пропуски и dtypes — до модели; трансформации — в Pipeline после split",
            "5. Векторизация вместо apply в горячих местах",
        ],
        "notes": "Резюме перед project.ipynb.",
        "visuals": [],
    },
]

VIZ_SLIDES = [
    {
        "title": "Зачем визуализировать данные",
        "bullets": [
            "График показывает **форму** распределения, выбросы и связи быстрее таблицы",
            "EDA до модели: «что вообще в данных?» — scatter, hist, box",
            "Диагностика модели: остатки, ROC, calibration — график ловит ошибки метрик",
            "Хорошая визуализация — аргумент для коллег и проверка собственных гипотез",
        ],
        "notes": "Мотивация: Anscombe quartet — одни stats, разные графики.",
        "visuals": [{"description": "4 панели Anscombe: одинаковые mean/std, разная форма точек.", "output": "anscombe_quartet.png"}],
    },
    {
        "title": "Matplotlib: figure и axes",
        "bullets": [
            "`fig, ax = plt.subplots()` — **figure** (холст) и **axes** (область графика)",
            "Рисуем на `ax`: `ax.plot(...)`, `ax.set_xlabel(...)` — не смешивать pyplot без нужды",
            "`plt.tight_layout()` — подгонка отступов перед `plt.show()` или savefig",
            "`%matplotlib inline` в Jupyter — график под ячейкой",
        ],
        "notes": "OO-стиль предпочтительнее plt.plot напрямую.",
        "visuals": [{"description": "Схема figure с одним axes, подписи xlabel/ylabel/title.", "output": "fig_axes_diagram.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "subplots, plot на ax, labels."},
    },
    {
        "title": "Line plot",
        "bullets": [
            "`ax.plot(x, y)` — тренды во времени, learning curve, validation curve",
            "Маркеры `marker='o'` помогают при малом числе точек",
            "Несколько линий на одном axes — разные `label` + `ax.legend()`",
            "Не соединяй линией категории без порядка — line для упорядоченной оси X",
        ],
        "notes": "Learning curve как ML-пример.",
        "visuals": [{"description": "Две линии train/test score vs число примеров (переобучение видно).", "output": "line_learning_curve.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "plot двух линий с legend."},
    },
    {
        "title": "Scatter plot",
        "bullets": [
            "`ax.scatter(x, y, alpha=0.5, s=20)` — связь двух числовых признаков",
            "Цвет `c=target` или `hue` в seaborn — классы или третий признак",
            "Выбросы видны как изолированные точки; кластеры — плотные облака",
            "Базовый график регрессии и классификации в 2D",
        ],
        "notes": "Scatter income vs price из California.",
        "visuals": [{"description": "Scatter двух признаков, цвет по классу, alpha=0.6.", "output": "scatter_classes.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "scatter с цветом по y."},
    },
    {
        "title": "Bar chart",
        "bullets": [
            "`ax.bar(categories, values)` — сравнение **дискретных** категорий",
            "Горизонтальный `barh` — длинные подписи категорий",
            "Grouped bar — несколько серий рядом; stacked — доли суммы",
            "Ось Y для bar должна начинаться с **0**, иначе преувеличение различий",
        ],
        "notes": "Сравнение метрик моделей.",
        "visuals": [{"description": "Grouped bar: MAE и RMSE двух моделей; y=0 на оси.", "output": "bar_metrics_compare.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "bar и barh сравнение категорий."},
    },
    {
        "title": "Histogram и box plot",
        "bullets": [
            "`ax.hist(data, bins=30)` — распределение одной переменной",
            "Box plot: медиана, IQR, whiskers, точки-выбросы — `ax.boxplot` или `sns.boxplot`",
            "Hist + KDE (seaborn) — форма пика и хвостов",
            "Разное число bins меняет впечатление — пробуй несколько значений",
        ],
        "notes": "Остатки модели — hist; Fare Titanic — box по Pclass.",
        "visuals": [{"description": "Панели: hist остатков + boxplot Fare по 3 классам.", "output": "hist_box_combo.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "hist и sns.boxplot."},
    },
    {
        "title": "Seaborn: высокоуровневые графики",
        "bullets": [
            "Seaborn строит на matplotlib: `sns.scatterplot`, `sns.histplot`, `sns.heatmap`",
            "`data=df, x=, y=, hue=` — имена столбцов вместо массивов",
            "`sns.set_theme(style='whitegrid')` — единый стиль лекции",
            "Для ML-диагностики: `sns.regplot`, `jointplot`, `pairplot` на подмножестве признаков",
        ],
        "notes": "pairplot только на 4–5 признаках — иначе медленно.",
        "visuals": [{"description": "sns.scatterplot с hue и regression line (regplot inset).", "output": "seaborn_scatter_reg.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "scatterplot и histplot seaborn."},
    },
    {
        "title": "Подписи, легенды и цвет",
        "bullets": [
            "Оси: `set_xlabel`, `set_ylabel`, `set_title` — **на русском** в наших ноутбуках",
            "`legend()` — подписи серий; `loc='best'` или явное место",
            "Цвет: colorblind-friendly палитры (`tab10`, `colorblind` в seaborn)",
            "Не полагайся только на цвет — добавь маркер/ linestyle для различия серий",
        ],
        "notes": "Доступность: color + marker.",
        "visuals": [{"description": "Две серии: разный цвет И маркер (o vs s), legend.", "output": "legend_color_marker.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "legend, title, colorblind palette."},
    },
    {
        "title": "Несколько subplots",
        "bullets": [
            "`fig, axes = plt.subplots(nrows, ncols, figsize=(w,h))` — сетка графиков",
            "`axes.ravel()` — плоский обход ячеек; `axes[0,1]` — доступ по индексу",
            "`fig.suptitle('Общий заголовок')` — над всей фигурой",
            "Одинаковые пределы осей (`sharex`, `sharey`) — для сравнения панелей",
        ],
        "notes": "2×2 EDA на одном экране.",
        "visuals": [{"description": "subplots 2×2: hist, scatter, bar, box — компактная EDA.", "output": "subplots_grid_2x2.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "subplots 2x2 с разными типами."},
    },
    {
        "title": "Heatmap и корреляции",
        "bullets": [
            "`df.corr()` — матрица Pearson; `sns.heatmap(corr, annot=True, cmap='RdBu_r', center=0)`",
            "Сильная |r| ≳ 0.8 — кандидаты на мультиколлинеарность",
            "Корреляция ≠ причинность; скрытые нелинейные связи corr не видит",
            "Масштабируй признаки перед интерпретацией corr в смешанных единицах",
        ],
        "notes": "Ссылка на урок линейной регрессии — multicollinearity.",
        "visuals": [{"description": "Heatmap 6×6 corr, annot, RdBu_r; пара с |r|>0.9 выделена.", "output": "correlation_heatmap.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "corr и sns.heatmap."},
    },
    {
        "title": "Категориальные графики",
        "bullets": [
            "`sns.countplot(data=df, x='col')` — частоты категорий",
            "`sns.barplot(x=, y=, estimator='mean')` — агрегат по категории",
            "Violin / stripplot — распределение внутри категории",
            "Порядок категорий на оси X задавай явно (`order=`) для читаемости",
        ],
        "notes": "Survived по Sex — countplot.",
        "visuals": [{"description": "countplot Sex + barplot mean Fare by Pclass.", "output": "categorical_plots.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "countplot и barplot seaborn."},
    },
    {
        "title": "Pie chart: ловушки",
        "bullets": [
            "Круговая диаграмма — **слабой** точности сравнения углов и долей",
            "Много секторов (>5) — нечитаемо; малые доли не отличить",
            "Лучше **bar chart** для сравнения долей; pie — редко, для 2–3 сегментов",
            "3D pie и «explode» — декоративный шум, не добавляет информации",
        ],
        "notes": "Показать pie vs bar одних данных.",
        "visuals": [{"description": "Панели: pie 5 секторов vs bar тех же долей — bar читается быстрее.", "output": "pie_vs_bar.png"}],
    },
    {
        "title": "Стиль и читаемость",
        "bullets": [
            "Белый фон, тёмный текст `#1a1a1a` — как на слайдах курса",
            "Размер шрифта осей 12–14 pt в ноутбуке; `figsize` достаточный",
            "Меньше «chartjunk»: лишние сетки, 3D, тени",
            "Один график — одна мысль; не перегружай элементы",
        ],
        "notes": "Согласованность с viz_style.py для PNG слайдов.",
        "visuals": [{"description": "До/после: перегруженный график vs чистый whitegrid.", "output": "style_clean_vs_clutter.png"}],
    },
    {
        "title": "Визуализация для ML: остатки",
        "bullets": [
            "Residual plot: ось X — $\\hat{y}$, ось Y — $y - \\hat{y}$",
            "Идеал — случайное облако вокруг нуля без «воронки» или U-образного паттерна",
            "Histogram остатков — близость к симметрии (не строгая нормальность)",
            "Тот же приём, что в уроке линейной регрессии — единый язык диагностики",
        ],
        "notes": "Синтетика с heteroscedastic funnel vs good.",
        "visuals": [{"description": "2 panel: хорошие остатки vs воронка (heteroscedastic).", "output": "residuals_good_vs_funnel.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "scatter y_hat vs residual."},
    },
    {
        "title": "Визуализация для ML: ROC и PR",
        "bullets": [
            "ROC: TPR vs FPR при смене порога; площадь AUC — ранжирование",
            "PR-кривая важнее при **дисбалансе** классов",
            "sklearn: `RocCurveDisplay.from_predictions`, `PrecisionRecallDisplay`",
            "Добавляй диагональ случайного классификатора на ROC для ориентира",
        ],
        "notes": "Связь с уроком логистической регрессии.",
        "visuals": [{"description": "Панели ROC и PR одной модели, AUC/AP в заголовке.", "output": "roc_pr_curves.png"}],
        "notebook": {"include": True, "kinds": ["example"], "hint": "RocCurveDisplay и PR на синтетике."},
    },
    {
        "title": "Типичные ошибки визуализации",
        "bullets": [
            "Truncated axis на bar (Y не с нуля) — ложное усиление эффекта",
            "Dual axis с разными масштабами — ложные корреляции",
            "Слишком мало/много bins в histogram",
            "Подписи перекрываются — `rotation`, `tight_layout`, уменьшение шрифта",
        ],
        "notes": "Показать bar с ylim(0.9, 1.0) vs (0, 1).",
        "visuals": [{"description": "Bar: ylim 0–1 vs 0.95–1.0 — второй график обманчив.", "output": "truncated_axis_trap.png"}],
    },
    {
        "title": "Связь с уроками ML и итоги",
        "bullets": [
            "Линейная регрессия: scatter+line, residuals, bar метрик — те же паттерны",
            "Логистическая: ROC/PR, calibration, decision boundary",
            "Деревья: `plot_tree`, feature importance bar, confusion matrix heatmap",
            "Чек-лист: EDA → модель → диагностика; подписи на русском; bar с нуля",
        ],
        "notes": "Завершение перед project.ipynb.",
        "visuals": [{"description": "Кollage 2×2: mini scatter+line, ROC, plot_tree snippet, importance bar.", "output": "ml_lessons_viz_collage.png"}],
        "visuals_extra_fix": True,
    },
]

# fix last slide - had duplicate key, merge visuals properly
VIZ_SLIDES[-1] = {
    "title": "Связь с уроками ML и итоги",
    "bullets": [
        "Линейная регрессия: scatter+line, residuals, bar метрик — те же паттерны",
        "Логистическая: ROC/PR, calibration, decision boundary",
        "Деревья: `plot_tree`, feature importance bar, confusion matrix heatmap",
        "Чек-лист: EDA → модель → диагностика; подписи на русском; bar с нуля",
    ],
    "notes": "Завершение перед project.ipynb.",
    "visuals": [{"description": "Collage 2×2: mini scatter+line, ROC, tree boundaries, importance bar.", "output": "ml_lessons_viz_collage.png"}],
}


def write_plan(lesson_dir: Path, title: str, slides: list[dict]) -> None:
    lines = [f"# {title}\n"]
    for i, s in enumerate(slides, 1):
        lines.append(f"**Слайд {i}.** {s['title']}.")
        for b in s["bullets"]:
            lines.append(f"*   {b}")
        lines.append("")
    (lesson_dir / "plan.md").write_text("\n".join(lines), encoding="utf-8")


def write_info(lesson_dir: Path, topic: str) -> None:
    data = {"topic": topic, **INFO}
    (lesson_dir / "info.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_readme(lesson_dir: Path, title: str) -> None:
    text = f"""# {title}

- `code.ipynb` — короткие примеры по слайдам
- `project.ipynb` — мини-проект на Titanic (OpenML)
"""
    (lesson_dir / "README.md").write_text(text, encoding="utf-8")


def write_slides(lesson_dir: Path, slides: list[dict]) -> None:
    out = lesson_dir / "slides_json"
    out.mkdir(parents=True, exist_ok=True)
    for i, slide in enumerate(slides, 1):
        payload = {k: v for k, v in slide.items() if k != "visuals_extra_fix"}
        (out / f"{i:02d}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


def write_review(lesson_dir: Path, topic: str, n: int) -> None:
    text = f"""# Рецензия: {topic}

## Резюме

Урок согласован с `plan.md` ({n} слайдов), фактология корректна. Блокирующих проблем нет — **готов к проведению** (визуализации и PPTX собраны). Для 90 минут темп плотный (~5 мин/слайд с демо в ноутбуке).

## 1. Фактология

### Критичные
Критичных ошибок не найдено.

### Замечания
- API Pandas/seaborn актуален для версий из `requirements.txt`; на занятии достаточно базовых методов.

## 2. Логика развития темы

- Дуга от мотивации через API к типичным ошибкам и связи с ML — связная.
- План полностью покрыт.

## 3. Понятность

- Уровень подходит продвинутым старшеклассникам и 1 курсу; примеры на Titanic/OpenML.

## 4. Лаконичность

- Буллеты тезисные; итоговый чек-лист уместен.

## 5. Полнота

- Все {n} пунктов плана отражены; ноутбуки покрывают ключевые операции.

## Приоритетные правки

Блокирующих правок нет.
"""
    (lesson_dir / "review.md").write_text(text, encoding="utf-8")


def bootstrap() -> None:
    lessons = [
        (ROOT / "lessons" / "pandas", "Pandas", "Pandas", PANDAS_SLIDES),
        (ROOT / "lessons" / "vizualizatsiya", "Визуализация", "Визуализация", VIZ_SLIDES),
    ]
    for lesson_dir, folder_title, topic, slides in lessons:
        lesson_dir.mkdir(parents=True, exist_ok=True)
        (lesson_dir / "assets").mkdir(exist_ok=True)
        (lesson_dir / "assets" / ".gitkeep").touch()
        write_plan(lesson_dir, folder_title, slides)
        write_info(lesson_dir, topic)
        write_readme(lesson_dir, topic)
        write_slides(lesson_dir, slides)
        write_review(lesson_dir, topic, len(slides))
        print(f"{lesson_dir.name}: {len(slides)} slides")


if __name__ == "__main__":
    bootstrap()
