"""Slide data for lesson: Визуализации для машинного обучения (34 slides).

Source plan: lessons/vizualizatsiya/plan.md
Format: agents/prompts/slide_generator.md
"""
from __future__ import annotations

SLIDES: list[dict] = [
    {
        "title": "Философия визуализации в ML",
        "bullets": [
            "Визуализация решает три задачи: **EDA**, **диагностика моделей**, **объяснение результатов** бизнесу",
            "Золотое правило: каждый график отвечает на **конкретный вопрос** — без вопроса график не строим",
            "Плохая визуализация ведёт к неверным решениям; хорошая даёт инсайт за **3 секунды**",
            "Главные библиотеки: `matplotlib` (низкоуровневая база), `seaborn` (статистика из коробки), `plotly` (интерактив), `pandas` built-in (быстрые графики)",
        ],
        "notes": "Мотивация: Anscombe quartet — одинаковые статистики, разные графики.",
        "visuals": [
            {
                "description": "Три колонки-сценария: EDA (hist/scatter), диагностика модели (residuals/ROC), презентация бизнесу (bar с KPI). Подписи на русском.",
                "output": "ml_viz_three_roles.png",
            }
        ],
    },
    {
        "title": "Выбор библиотеки под задачу",
        "bullets": [
            "`matplotlib` — полный контроль, кастомные графики, статьи; **основа** для остальных библиотек",
            "`seaborn` — **90% EDA**: красивые дефолты, статистика одной строкой; работает поверх matplotlib",
            "`plotly` — интерактивные дашборды и презентации (zoom, hover, export); медленнее на больших данных",
            "`df.plot()` — быстрые разведочные графики прямо из DataFrame",
            "Правило: **seaborn** для EDA → **plotly** для интерактива → **matplotlib** для тонкой настройки",
        ],
        "notes": "Показать один и тот же scatter в seaborn и plotly для сравнения UX.",
        "visuals": [
            {
                "description": "Таблица-сравнение 4 библиотек: контроль, скорость, интерактив, типичный use case. Иконки matplotlib/seaborn/plotly/pandas.",
                "output": "library_choice_matrix.png",
            }
        ],
    },
    {
        "title": "Быстрый старт: pandas built-in визуализация",
        "bullets": [
            "ML-задача: **моментальный обзор** данных без импорта дополнительных библиотек",
            "`df.plot(kind='hist')`, `df.plot(kind='box')`, `df.plot(kind='scatter', x='col1', y='col2')`",
            "`df['col'].value_counts().plot(kind='bar')` — частоты категорий",
            "`df.plot.hist(alpha=0.5, bins=30)` — overlay гистограмм всех числовых столбцов",
            "Ограничение: меньше контроля над стилем; использовать в **первые 30 секунд** знакомства с датасетом",
        ],
        "notes": "California Housing или Iris — быстрый df.plot() обзор.",
        "visuals": [
            {
                "description": "2×2 панель: hist, box, scatter, bar из df.plot() на одном датасете. Минимальный стиль pandas.",
                "output": "pandas_builtin_overview.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "df.plot hist, box, scatter, value_counts bar."},
    },
    {
        "title": "Matplotlib: архитектура Figure и Axes",
        "bullets": [
            "ML-задача: понимать **иерархию объектов** для кастомизации графиков",
            "**Figure** — «холст»; **Axes** — область координат (сам график)",
            "`fig, ax = plt.subplots()` — создание связки; `ax.plot()`, `ax.scatter()`, `ax.set_xlabel()` — методы Axes",
            "`plt.tight_layout()` — автоматическая подгонка отступов",
            "Понимание иерархии критично для **сложных фигур** с несколькими графиками",
        ],
        "notes": "OO-стиль предпочтительнее plt.plot() напрямую.",
        "visuals": [
            {
                "description": "Схема: Figure (рамка) содержит один Axes с plot, подписи xlabel/ylabel/title. Стрелки Figure → Axes → Artist.",
                "output": "matplotlib_figure_axes_diagram.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "subplots, plot на ax, labels, tight_layout."},
    },
    {
        "title": "Несколько графиков на одной фигуре: subplot",
        "bullets": [
            "ML-задача: сравнить распределения, показать **до/после**, собрать dashboard",
            "`fig, axes = plt.subplots(2, 2, figsize=(12, 10))` — сетка $2 \\times 2$",
            "`axes[0, 0].hist(train['age']); axes[0, 1].hist(test['age'])` — сравнение train/test",
            "Альтернатива: `plt.subplot(2, 3, i)`; общий заголовок: `fig.suptitle('Comparison')`",
            "Используйте `constrained_layout=True` или `tight_layout()` — иначе подписи **перекрываются**",
        ],
        "notes": "2×2 EDA: hist, scatter, box, bar на одном экране.",
        "visuals": [
            {
                "description": "subplots 2×2: hist train vs test age, scatter, box, bar. suptitle сверху, tight_layout без перекрытий.",
                "output": "subplot_grid_train_test.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "subplots 2x2, suptitle, tight_layout."},
    },
    {
        "title": "Кастомизация: цвета, стили, аннотации",
        "bullets": [
            "ML-задача: сделать графики **информативными** и презентационными",
            "Цвета: `color='red'`, `cmap='viridis'`, `alpha=0.6` (прозрачность)",
            "Стили линий: `linestyle='--'`, `linewidth=2`, `marker='o'`",
            "Аннотации: `ax.annotate('Outlier', xy=(x, y), xytext=(x+1, y+1), arrowprops=dict(arrowstyle='->'))`",
            "Легенды: `ax.legend(loc='best', frameon=False)`; сетка: `ax.grid(True, alpha=0.3)`",
            "Для презентаций: увеличивайте `fontsize` через `rcParams` или `fontscale` в seaborn",
        ],
        "notes": "Показать annotate на выбросе в scatter.",
        "visuals": [
            {
                "description": "Scatter с выбросом, annotate со стрелкой, legend, grid alpha=0.3, viridis colormap на colorbar.",
                "output": "customization_annotate_legend.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "colors, linestyle, annotate, legend, grid."},
    },
    {
        "title": "Сохранение и экспорт графиков",
        "bullets": [
            "ML-задача: сохранить графики для **отчётов**, статей, дашбордов",
            "`plt.savefig('plot.png', dpi=300, bbox_inches='tight')` — высокое разрешение",
            "Векторные форматы: `.svg`, `.pdf` — для статей (масштабируются без потери качества)",
            "Прозрачный фон: `transparent=True`",
            "Plotly: `fig.write_html('plot.html')` — HTML с интерактивностью",
            "Всегда `bbox_inches='tight'`, иначе **обрежутся подписи**",
        ],
        "notes": "Сравнить PNG 100 vs 300 dpi на одном графике.",
        "visuals": [
            {
                "description": "Панель: PNG (raster), SVG (vector zoom), HTML (plotly badge). Подписи dpi=300, bbox_inches='tight'.",
                "output": "export_formats_comparison.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "savefig png/svg, write_html plotly."},
    },
    {
        "title": "Plotly: интерактивные графики одной строкой",
        "bullets": [
            "ML-задача: графики с **hover**, zoom, filter для исследования данных",
            "`import plotly.express as px`",
            "`px.scatter(df, x='area', y='price', color='city', hover_data=['id'])` — scatter с подсказками",
            "`px.histogram(df, x='income', color='segment', marginal='box')` — гистограмма с box plot",
            "`px.line(df, x='date', y='sales')` — временные ряды с zoom",
            "`fig.show()` — интерактив; `fig.write_html()` — сохранение. Для презентаций и drill-down",
        ],
        "notes": "California Housing: px.scatter area vs price.",
        "visuals": [
            {
                "description": "Статичный скриншот px.scatter с hover-tooltip (area, price, city), color по city, легенда справа.",
                "output": "plotly_express_scatter_hover.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "px.scatter, px.histogram, write_html."},
    },
    {
        "title": "Plotly: продвинутые возможности",
        "bullets": [
            "ML-задача: **3D**, анимация, субплоты",
            "`px.scatter_3d(df, x='x', y='y', z='z', color='target')` — 3D scatter с вращением",
            "`px.scatter(df, x='x', y='y', animation_frame='year')` — анимация по времени",
            "`make_subplots()` — несколько графиков в plotly",
            "Ограничение: тяжело для $>100k$ точек — `datashader` или `render_mode='webgl'`",
            "Для дашбордов: интеграция с **Dash** / **Streamlit**",
        ],
        "notes": "3D только для демо — не для production EDA на миллионах строк.",
        "visuals": [
            {
                "description": "3D scatter с color=target + inset animation_frame slider (год). Подписи осей x, y, z.",
                "output": "plotly_3d_animation_demo.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "scatter_3d, animation_frame, make_subplots."},
    },
    {
        "title": "Распределение одной переменной: гистограмма и KDE",
        "bullets": [
            "ML-задача: понять распределение признака — нужна ли **трансформация** (`log1p`), есть ли моды",
            "`sns.histplot(df['income'], kde=True)` — гистограмма + кривая плотности",
            "Ищем: **heavy tail** (повод для `log1p`), **мультимодальность** (смешаны группы), выбросы",
            "Параметр `bins`: мало — скрыты детали, много — шум",
            "Альтернатива: `px.histogram(df, x='income', marginal='violin')` в plotly",
        ],
        "notes": "Показать один признак с heavy tail до и после log1p.",
        "visuals": [
            {
                "description": "Две панели: histplot+kde с heavy tail слева; после log1p справа — более симметричное распределение.",
                "output": "histplot_kde_heavy_tail.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "sns.histplot kde=True, bins, log1p."},
    },
    {
        "title": "Быстрый поиск выбросов: Box plot",
        "bullets": [
            "ML-задача: найти аномалии по **IQR**, сравнить распределения по группам",
            "`sns.boxplot(data=df, x='category', y='price')` — медиана, квантили, выбросы за «усами»",
            "Ищем: точки за усами (кандидаты на удаление/winsorization), разная ширина коробок (**гетероскедастичность**), смещение медиан",
            "Ограничение: **не показывает форму** распределения — бимодальность скрывается",
            "Интерактив: `px.box(df, x='category', y='price', points='all')` — hover на каждой точке",
        ],
        "notes": "Fare по Pclass — классический boxplot пример.",
        "visuals": [
            {
                "description": "sns.boxplot x=category y=price, 3 категории, outliers точками за whiskers. Подписи медиана/IQR.",
                "output": "boxplot_outliers_iqr.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "sns.boxplot, px.box points='all'."},
    },
    {
        "title": "Сравнение распределений: Violin plot",
        "bullets": [
            "ML-задача: сравнить распределение **таргета** по категориальным признакам",
            "`sns.violinplot(data=df, x='city', y='income')` — объединяет box plot и KDE",
            "Инсайт: «В Москве средний доход выше, но форма **бимодальная**» — box plot это скрыл бы",
            "Идеален для анализа таргета в **регрессии**: сразу видно, где предсказывать сложно",
            "Plotly: `px.violin(df, x='city', y='income', box=True, points='outliers')`",
        ],
        "notes": "Сравнить box vs violin на одних данных — бимодальность.",
        "visuals": [
            {
                "description": "Панели: boxplot (скрывает бимодальность) vs violinplot (две «горбы» в одном городе). 3 города.",
                "output": "violin_vs_box_bimodal.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "sns.violinplot, px.violin box=True."},
    },
    {
        "title": "Связь двух непрерывных признаков: Scatter и marginal distributions",
        "bullets": [
            "ML-задача: увидеть **линейную/нелинейную** связь, кластеры, выбросы в паре признаков",
            "`sns.scatterplot(data=df, x='area', y='price', hue='city')`",
            "Совместно с распределениями: `sns.jointplot(kind='hex')` — **hexbin** для больших данных",
            "Ищем: линейный тренд, нелинейность (нужны полиномы или деревья), кластеры",
            "Для $>100k$ точек: `alpha=0.1` или `px.scatter(..., render_mode='webgl')`",
        ],
        "notes": "California: MedInc vs MedHouseVal.",
        "visuals": [
            {
                "description": "jointplot kind=hex: центральный hexbin scatter + marginal hist сверху и справа. hue по city на inset scatter.",
                "output": "jointplot_hex_marginals.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "scatterplot hue, jointplot hex."},
    },
    {
        "title": "Пропуски в данных: missingno",
        "bullets": [
            "ML-задача: увидеть **паттерны пропусков** — случайные или систематические",
            "Библиотека `missingno` визуализирует пропуски одной командой",
            "`msno.matrix(df)` — матрица пропусков; `msno.dendrogram(df)` — кластеризация признаков по паттернам",
            "Критический инсайт: если пропуски в A коррелируют с пропусками в B — пропуски **не случайны (MNAR)**",
            "Простая импутация средним при MNAR **сломает модель**",
        ],
        "notes": "Titanic или synthetic MNAR для демо dendrogram.",
        "visuals": [
            {
                "description": "msno.matrix слева (белые полосы = NaN) + msno.dendrogram справа (кластеры признаков с похожими пропусками).",
                "output": "missingno_matrix_dendrogram.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "msno.matrix, msno.dendrogram."},
    },
    {
        "title": "Мультиколлинеарность: Heatmap корреляций",
        "bullets": [
            "ML-задача: найти **дублирующие признаки** и их связь с таргетом",
            "`sns.heatmap(df.corr(), annot=True, cmap='coolwarm', center=0)` — карта с центром в нуле",
            "Ищем: $|r| > 0.9$ — кандидаты на удаление; высокая корреляция с **таргетом**",
            "Пирсон по умолчанию (линейная связь); для нелинейной — `method='spearman'`",
            "Plotly: `px.imshow(df.corr(), text_auto='.2f', color_continuous_scale='RdBu_r')`",
        ],
        "notes": "California Housing — corr heatmap 8 признаков.",
        "visuals": [
            {
                "description": "Heatmap 8×8 corr, annot=True, coolwarm center=0. Пара признаков с |r|>0.9 выделена рамкой.",
                "output": "correlation_heatmap_multicollinearity.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "df.corr(), sns.heatmap, spearman."},
    },
    {
        "title": "Детектирование дрейфа данных: ECDF и overlay",
        "bullets": [
            "ML-задача: сравнить распределения **train/test/production** — выявить **Data Drift**",
            "ECDF (Empirical CDF): `sns.ecdfplot()` — доля объектов меньше $X$; **не зависит от bins**",
            "Overlay KDE: наложение кривых плотности train и prod",
            "Расхождение кривых означает **дрейф** — модель может деградировать",
            "Plotly: `px.ecdf(train_df, x='age', color='dataset')` + overlay test",
        ],
        "notes": "Synthetic shift: mean age train vs prod +5 лет.",
        "visuals": [
            {
                "description": "ECDF две кривые train (синяя) vs prod (оранжевая) — заметный сдвиг по оси X. Подпись «Data Drift».",
                "output": "ecdf_train_prod_drift.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "sns.ecdfplot train vs test, overlay KDE."},
    },
    {
        "title": "Дисбаланс классов: Count plot",
        "bullets": [
            "ML-задача: увидеть распределение классов в **классификации**",
            "`sns.countplot(data=df, x='target')` — частоты каждого класса",
            "Если соотношение **100:1** — accuracy бесполезна; нужны `class_weight`, **PR-AUC**",
            "Стройте **в начале** каждого классификационного проекта",
            "Альтернатива: `df['target'].value_counts().plot(kind='bar')` или `px.histogram(df, x='target')`",
        ],
        "notes": "Credit fraud или imbalanced OpenML dataset.",
        "visuals": [
            {
                "description": "countplot с двумя классами 95% vs 5% — явный дисбаланс. Подпись «не используйте accuracy».",
                "output": "countplot_class_imbalance.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "sns.countplot target, value_counts bar."},
    },
    {
        "title": "Границы решений: Decision Boundaries",
        "bullets": [
            "ML-задача: визуализировать, как **классификатор** разделяет пространство признаков",
            "`DecisionBoundaryDisplay.from_estimator(clf, X, y)` — для **2D**-классификаторов",
            "Видим: линейная граница (логрег), нелинейная (деревья, SVM RBF), **переобучение**",
            "Наглядно: **XOR** не решается линейной моделью",
            "Кастомизация: `alpha=0.3` для прозрачности + overlay scatter точек",
        ],
        "notes": "make_moons + LogisticRegression vs RandomForest.",
        "visuals": [
            {
                "description": "Две панели: линейная граница (логрег, XOR fail) vs нелинейная (RBF SVM, XOR ok). Scatter точек поверх.",
                "output": "decision_boundary_linear_nonlinear.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "DecisionBoundaryDisplay, make_moons."},
    },
    {
        "title": "Многомерные данные: PCA, t-SNE, UMAP",
        "bullets": [
            "ML-задача: визуализировать многомерные данные в **2D/3D**, увидеть кластеры",
            "**PCA** — линейное снижение размерности, сохраняет **глобальную** структуру",
            "**t-SNE** и **UMAP** — нелинейные методы, сохраняют **локальные** кластеры; UMAP быстрее",
            "t-SNE/UMAP **только для визуализации** — не для создания признаков модели",
            "Plotly 3D: `px.scatter_3d(x=pca[:,0], y=pca[:,1], z=pca[:,2], color='target')`",
        ],
        "notes": "Digits или Iris — PCA vs UMAP side by side.",
        "visuals": [
            {
                "description": "Панели: PCA 2D scatter color=target vs UMAP 2D — UMAP показывает tighter clusters. Легенда классов.",
                "output": "pca_vs_umap_clusters.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "PCA, UMAP/t-SNE scatter color=target."},
    },
    {
        "title": "Кластеризация: Silhouette plot и Elbow method",
        "bullets": [
            "ML-задача: выбрать оптимальное число кластеров $K$ в **K-means**",
            "**Elbow method**: график WCSS от $K$ — ищем «локоть»",
            "**Silhouette plot**: качество кластеризации для каждого объекта; значения $\\approx 1$ — хорошая кластеризация",
            "Silhouette scores по кластерам сразу показывают **проблемные группы**",
            "`fig, (ax1, ax2) = plt.subplots(1, 2)` — elbow и silhouette рядом",
        ],
        "notes": "make_blobs n_clusters=3 для демо.",
        "visuals": [
            {
                "description": "1×2: elbow curve WCSS vs K (локоть при K=3) + silhouette plot bar chart по кластерам.",
                "output": "elbow_silhouette_kmeans.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "elbow WCSS, silhouette_plot KMeans."},
    },
    {
        "title": "Диагностика регрессии: Residual plot",
        "bullets": [
            "ML-задача: проверить качество регрессии, найти **систематические ошибки**",
            "`sns.residplot(x=y_pred, y=y_true - y_pred, lowess=True)` — остатки vs предсказания",
            "Хорошая модель: **хаотичное облако** вокруг нуля (гомоскедастичность)",
            "Плохие паттерны: парабола (нелинейность), воронка (**гетероскедастичность**), сдвиг от нуля",
            "Plotly: `px.scatter(x=y_pred, y=residuals, trendline='lowess')`",
        ],
        "notes": "Показать хороший vs funnel-shaped residplot.",
        "visuals": [
            {
                "description": "Две панели: residplot хаотичный (good) vs воронка (heteroscedastic bad). LOWESS линия красная.",
                "output": "residual_plot_good_bad.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "residplot, residuals vs y_pred."},
    },
    {
        "title": "Нормальность остатков: Q-Q plot",
        "bullets": [
            "ML-задача: проверить **нормальность ошибок** (важно для доверительных интервалов)",
            "`statsmodels.api.qqplot(residuals, line='s')` — квантили остатков vs квантили нормального распределения",
            "Точки должны лежать на **прямой**; отклонения на хвостах — **тяжёлые хвосты**",
            "Для ML: при тяжёлых хвостах используйте **MAE/Huber** вместо MSE",
        ],
        "notes": "Сравнить qqplot нормальных остатков vs t-distribution tails.",
        "visuals": [
            {
                "description": "Q-Q plot: точки вдоль диагонали line='s', лёгкое отклонение на верхнем хвосте. Подписи theoretical vs sample quantiles.",
                "output": "qqplot_residuals_normality.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "statsmodels qqplot residuals line='s'."},
    },
    {
        "title": "Предсказание vs реальность",
        "bullets": [
            "ML-задача: **визуально** оценить качество регрессии",
            "`sns.scatterplot(x=y_true, y=y_pred)` + диагональная линия $y = x$",
            "Хорошая модель: точки **плотно вокруг диагонали**",
            "Метрики в заголовке: `ax.set_title(f'R2={r2:.2f}, RMSE={rmse:.2f}')`",
            "Plotly: `px.scatter(x=y_true, y=y_pred, trendline='ols')` + диагональ",
        ],
        "notes": "California regressor pred vs true.",
        "visuals": [
            {
                "description": "Scatter y_true vs y_pred с красной диагональю y=x, title R2=0.85 RMSE=0.45. Точки вдоль диагонали.",
                "output": "predicted_vs_actual_diagonal.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "scatter y_true y_pred, y=x line, R2 RMSE."},
    },
    {
        "title": "Диагностика классификации: Confusion Matrix",
        "bullets": [
            "ML-задача: понять, **какие классы** модель путает",
            "`ConfusionMatrixDisplay.from_estimator(model, X, y)` — тепловая карта ошибок",
            "Ищем: большие **off-diagonal** элементы, дисбаланс FN vs FP",
            "`normalize='true'` — показывает **recall** для каждого класса",
            "Кастомизация: `cmap='Blues'`, `annot=True`, `fmt='.0f'`",
        ],
        "notes": "Multiclass digits — какие цифры путаются.",
        "visuals": [
            {
                "description": "Confusion matrix heatmap 3×3, Blues cmap, annot числа. Off-diagonal 2→3 выделен.",
                "output": "confusion_matrix_heatmap.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "ConfusionMatrixDisplay, normalize='true'."},
    },
    {
        "title": "Качество при разных порогах: ROC и PR кривые",
        "bullets": [
            "ML-задача: выбрать **оптимальный порог**, сравнить модели",
            "`RocCurveDisplay` и `PrecisionRecallDisplay` из sklearn",
            "**PR-кривая** важнее при сильном дисбалансе классов",
            "Overlay: несколько моделей на одном графике — сразу видна **лучшая**",
            "Plotly: `px.line(x=fpr, y=tpr)` + диагональ для случайного классификатора",
        ],
        "notes": "Imbalanced dataset — PR vs ROC side by side.",
        "visuals": [
            {
                "description": "1×2: ROC (AUC=0.92) с diagonal baseline + PR curve. Две модели overlay разными цветами.",
                "output": "roc_pr_curves_overlay.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "RocCurveDisplay, PrecisionRecallDisplay overlay."},
    },
    {
        "title": "Переобучение vs недообучение: Learning Curve",
        "bullets": [
            "ML-задача: понять, нужно ли **больше данных** или **более сложная модель**",
            "`LearningCurveDisplay.from_estimator(model, X, y)` — кривые train/validation",
            "Train высоко, Val низко — **переобучение**; обе низкие — **недообучение**; обе высокие — оптимум",
            "Доверительные интервалы: `plt.fill_between` для визуализации **variance**",
        ],
        "notes": "DecisionTree max_depth=20 vs 3 — over vs underfit.",
        "visuals": [
            {
                "description": "Learning curve: train score высокий, val score низкий (gap) — overfitting. fill_between CI. Подписи train/validation.",
                "output": "learning_curve_overfitting.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "LearningCurveDisplay, fill_between CI."},
    },
    {
        "title": "Кросс-валидация: стабильность модели",
        "bullets": [
            "ML-задача: оценить **variance** модели, а не только среднее качество",
            "Box plot метрик по фолдам: `sns.boxplot(data=cv_scores)`",
            "Line plot: `plt.plot(cv_scores, marker='o')` — видны **аномальные фолды**",
            "Большой разброс означает **нестабильность** модели",
            "Сравнение моделей: `sns.boxplot` для нескольких наборов `cv_scores`",
        ],
        "notes": "5-fold CV scores двух моделей — boxplot compare.",
        "visuals": [
            {
                "description": "Boxplot CV scores двух моделей (Model A узкий, Model B широкий) + line plot fold scores с outlier fold.",
                "output": "cv_scores_stability_boxplot.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "cross_val_score, boxplot по фолдам."},
    },
    {
        "title": "Подбор гиперпараметров: Grid Search visualization",
        "bullets": [
            "ML-задача: выбрать **лучшие гиперпараметры**, увидеть взаимодействия",
            "Heatmap: `sns.heatmap(grid_results)` для 2D grid search (`max_depth` vs `min_samples_leaf`)",
            "Line plot: зависимость метрики от одного параметра с **доверительными интервалами**",
            "Часто есть **«плато»** — широкий диапазон параметров даёт схожее качество",
            "Plotly: `px.imshow` для интерактивного heatmap с hover",
        ],
        "notes": "RandomForest grid max_depth × min_samples_leaf.",
        "visuals": [
            {
                "description": "Heatmap grid search max_depth × min_samples_leaf, annot F1-score. Плато в центре (robust region).",
                "output": "grid_search_heatmap_plateau.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "GridSearchCV results heatmap, line plot param."},
    },
    {
        "title": "Важность признаков: Permutation Importance",
        "bullets": [
            "ML-задача: понять, **какие признаки** влияют на предсказания",
            "Для деревьев: `model.feature_importances_` — **смещено** к high-cardinality признакам",
            "**Permutation Importance** (честнее): перемешиваем признак, смотрим **падение метрики**",
            "`sns.barplot(x=result.importances_mean, y=feature_names)`",
            "Error bars: `plt.barh(y, x, xerr=std)` — показать **variance** важности",
        ],
        "notes": "Сравнить feature_importances_ vs permutation на одном RandomForest.",
        "visuals": [
            {
                "description": "Horizontal barh permutation importance top-10 features с xerr error bars. Один признак с широкими error bars.",
                "output": "permutation_importance_barh.png",
            }
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "permutation_importance, barh xerr."},
    },
    {
        "title": "Стили и темы: единый дизайн для проекта",
        "bullets": [
            "ML-задача: **консистентный** визуальный стиль для всех графиков проекта",
            "`plt.style.use('seaborn-v0_8-whitegrid')` — готовые стили matplotlib",
            "`sns.set_theme(style='whitegrid', palette='husl')` — тема seaborn",
            "Кастомная палитра: `sns.set_palette(['#FF6B6B', '#4ECDC4', '#45B7D1'])`",
            "`rcParams`: `plt.rcParams['figure.figsize'] = (12, 8)`, `plt.rcParams['font.size'] = 12`",
            "Для презентаций: **увеличенный шрифт**, минималистичный стиль, контрастные цвета",
        ],
        "notes": "Один график до/после set_theme.",
        "visuals": [],
        "notebook": {"include": True, "kinds": ["example"], "hint": "set_theme, set_palette, rcParams."},
    },
    {
        "title": "Общие техники: overlay и комбинирование графиков",
        "bullets": [
            "ML-задача: показать **несколько распределений/моделей** на одном графике для сравнения",
            "Overlay гистограмм: `plt.hist(train, alpha=0.5, label='train'); plt.hist(test, alpha=0.5, label='test')`",
            "Overlay линий: `plt.plot(train_scores); plt.plot(val_scores)`",
            "Двойные оси (осторожно!): `ax2 = ax1.twinx()` — разные масштабы, часто **вводит в заблуждение**",
            "`FacetGrid`: `g = sns.FacetGrid(df, col='category'); g.map(sns.histplot, 'value')`",
            "Plotly: `make_subplots(rows=2, cols=2)` — несколько интерактивных графиков",
        ],
        "notes": "Overlay train/test hist — классика drift check.",
        "visuals": [
            {
                "description": "Overlay гистограмм train и test с alpha=0.5.",
                "output": "overlay_hist_train_test.png",
                "size": "compact",
            },
            {
                "description": "Две линии train_scores и val_scores на одних осях.",
                "output": "overlay_lines_scores.png",
                "size": "compact",
            },
            {
                "description": "FacetGrid: histplot по категориям в ряд.",
                "output": "overlay_facetgrid_demo.png",
                "size": "compact",
            },
            {
                "description": "Схема make_subplots 2×2 с четырьмя панелями.",
                "output": "overlay_plotly_subplots.png",
                "size": "compact",
            },
        ],
        "notebook": {"include": True, "kinds": ["example"], "hint": "overlay hist, FacetGrid, twinx caution."},
    },
    {
        "title": "Размер и DPI: подготовка для разных целей",
        "bullets": [
            "ML-задача: оптимизировать **размер и качество** графика для статьи, презентации, дашборда",
            "`figsize=(width, height)` в дюймах: $(10, 6)$ для статьи, $(16, 9)$ для презентации",
            "**DPI** (dots per inch): 100 для экрана, 300 для печати, 600 для журналов",
            "`plt.savefig('plot.png', dpi=300, bbox_inches='tight', facecolor='white')`",
            "Для веба: SVG $<$ PNG по размеру файла для **векторной** графики",
            "Aspect ratio: золотое сечение $1.618:1$ часто выглядит эстетично",
        ],
        "notes": "Таблица рекомендаций: экран/print/journal.",
        "visuals": [],
        "notebook": {"include": True, "kinds": ["example"], "hint": "figsize, savefig dpi=300, aspect ratio."},
    },
    {
        "title": "Антипаттерны и best practices",
        "bullets": [
            "**Антипаттерны**: pie charts (замените на bar), 3D графики (искажают), rainbow colormaps (не colorblind-friendly), отсутствие labels",
            "**Best practices**: один график = один инсайт; всегда **title/labels/units**; тест на коллегах (**5 секунд** на понимание)",
            "Colorblind-friendly: `viridis`, `plasma` — избегайте **красно-зелёных** сочетаний",
            "Для презентаций: минимум текста, крупные шрифты, контрастные цвета, белый фон",
            "Для статей: векторные форматы (SVG/PDF), **grayscale-friendly** палитры",
        ],
        "notes": "Показать pie vs bar и rainbow vs viridis на одних данных.",
        "visuals": [
            {
                "description": "2×2: pie (bad) vs bar (good) same data; rainbow jet cmap (bad) vs viridis (good) heatmap. Красные крестики/зелёные галочки.",
                "output": "viz_antipatterns_best_practices.png",
            }
        ],
    },
    {
        "title": "Итоговый чек-лист: какой график для какой задачи",
        "bullets": [
            "**Распределение** → hist + KDE (`seaborn`/`plotly`) | **Выбросы** → box plot",
            "**Сравнение групп** → violin plot | **Связь признаков** → scatter + jointplot",
            "**Пропуски** → `missingno` | **Мультиколлинеарность** → heatmap",
            "**Дрейф** → ECDF, overlay KDE | **Дисбаланс** → count plot",
            "**Границы решений** → `DecisionBoundaryDisplay` | **Многомерные** → PCA/t-SNE/UMAP",
            "**Регрессия** → residual plot, Q-Q, predicted vs actual | **Классификация** → confusion matrix, ROC/PR",
            "**Переобучение** → learning curve | **Важность признаков** → permutation importance",
            "Библиотеки: **seaborn** для EDA, **plotly** для интерактива, **matplotlib** для кастомизации, **pandas** для быстрых графиков",
        ],
        "notes": "Финальный слайд — можно распечатать как шпаргалку.",
        "visuals": [],
    },
]
SLIDES = [{'title': 'Философия визуализации в ML',
  'bullets': ['Визуализация решает три задачи: **EDA**, **диагностика моделей**, **объяснение результатов** бизнесу',
              'Золотое правило: каждый график отвечает на **конкретный вопрос** — без вопроса график не строим',
              'Плохая визуализация ведёт к неверным решениям; хорошая даёт инсайт за **3 секунды**',
              'Главные библиотеки: `matplotlib` (низкоуровневая база), `seaborn` (статистика из коробки), `plotly` '
              '(интерактив), `pandas` built-in (быстрые графики)'],
  'notes': 'Мотивация: Anscombe quartet — одинаковые статистики, разные графики.',
  'visuals': []},
 {'title': 'Выбор библиотеки под задачу',
  'bullets': ['**matplotlib** — полный контроль, кастомные графики, статьи; **основа** для остальных библиотек',
              '**seaborn** — **90% EDA**: красивые дефолты, статистика одной строкой; работает поверх matplotlib',
              '**plotly** — интерактивные дашборды и презентации (zoom, hover, export); медленнее на больших данных',
              '**pandas** built-in (df.plot) — быстрые разведочные графики прямо из DataFrame',
              'Правило: **seaborn** для EDA → **plotly** для интерактива → **matplotlib** для тонкой настройки'],
  'notes': 'Показать один и тот же scatter в seaborn и plotly для сравнения UX.',
  'visuals': []},
 {'title': 'Быстрый старт: pandas built-in визуализация',
  'bullets': ['ML-задача: **моментальный обзор** данных без импорта дополнительных библиотек',
              'Гистограмма, box plot, scatter и bar chart — одной цепочкой вызовов от DataFrame',
              'Частоты категорий — через value_counts и столбчатую диаграмму',
              'Overlay гистограмм всех числовых столбцов — быстрый взгляд на масштабы',
              'Ограничение: меньше контроля над стилем; использовать в **первые 30 секунд** знакомства с датасетом'],
  'notes': 'California Housing или Iris — быстрый df.plot() обзор.',
  'visuals': [],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'df.plot hist, box, scatter, value_counts bar.'}},
 {'title': 'Matplotlib: архитектура Figure и Axes',
  'bullets': ['ML-задача: понимать **иерархию объектов** — без неё сложно править сложные фигуры',
              '**Figure** — весь «лист» (холст); **Axes** — прямоугольная область, где рисуется график',
              'Сначала создаём figure и axes, затем вызываем методы **на axes** — plot, scatter, подписи осей',
              'Перед показом или сохранением — **подгонка отступов**, иначе подписи обрежутся',
              'Эта схема — основа для subplot, кастомизации и export в PNG/PDF'],
  'notes': 'OO-стиль предпочтительнее plt.plot() напрямую.',
  'visuals': [{'description': 'Мини-график: пунктирная рамка Figure, внутри Axes с scatter. Заголовок PNG: fig, ax = '
                              'plt.subplots()',
               'output': 'mpl_code_subplots.png',
               'size': 'compact'},
              {'description': 'Линия + scatter + подписи xlabel/ylabel. Заголовок PNG: ax.plot() / ax.scatter() / '
                              'ax.set_xlabel()',
               'output': 'mpl_code_axes_methods.png',
               'size': 'compact'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'subplots, plot на ax, labels, tight_layout.'}},
 {'title': 'Несколько графиков на одной фигуре: subplot',
  'bullets': ['ML-задача: **сравнить** train и test (или до/после) на одном экране',
              'subplots — сетка маленьких графиков внутри одного figure; у каждой ячейки свой axes',
              'Верхний ряд: одна и та же переменная в train и test — сразу виден **сдвиг распределения**',
              'Общий заголовок всей фигуры — suptitle; подписи осей — в каждой ячейке отдельно',
              'constrained_layout или tight_layout — **обязательны**, иначе подписи и заголовки **перекрываются**'],
  'notes': '2×2 EDA: hist, scatter, box, bar на одном экране.',
  'visuals': [{'description': '2×1 subplot: слева hist train age, справа hist test age — явный сдвив вправо у test. '
                              'suptitle «train vs test». Крупные подписи.',
               'output': 'subplot_train_test_clear.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'subplots 2x2, suptitle, tight_layout.'}},
 {'title': 'Кастомизация: цвета, стили, аннотации',
  'bullets': ['ML-задача: график должен **читаться** на проекторе и в PDF — не только в ноутбуке',
              '**Цвет и прозрачность** разводят серии; палитра **viridis** удобна для дальтоников',
              '**Тип линии и маркеры** — запасной способ отличить классы, если цветов мало',
              '**Аннотация со стрелкой** — один выброс или ключевая точка, без простыни текста',
              '**Легенда и лёгкая сетка** помогают считывать значения; для слайдов — **крупный шрифт**'],
  'notes': 'Показать annotate на выбросе в scatter.',
  'visuals': [{'description': 'Scatter с выбросом, annotate со стрелкой, legend, grid alpha=0.3, viridis colormap на '
                              'colorbar.',
               'output': 'customization_annotate_legend.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'colors, linestyle, annotate, legend, grid.'}},
 {'title': 'Сохранение и экспорт графиков',
  'bullets': ['ML-задача: сохранить график для **отчёта**, статьи или внутреннего дашборда',
              '**PNG, dpi=300** — слайды и печать; **SVG/PDF** — статьи, масштаб без потери качества',
              '**Прозрачный фон** (transparent=True) — для наложения на цветной слайд или сайт',
              '**Plotly → HTML** — интерактив для коллег (zoom, hover)',
              "**bbox_inches='tight'** — иначе при savefig **обрежутся** подписи осей и легенда"],
  'notes': 'Сравнить PNG 100 vs 300 dpi на одном графике.',
  'visuals': [],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'savefig png/svg, write_html plotly.'}},
 {'title': 'Plotly: интерактивные графики одной строкой',
  'bullets': ['ML-задача: **исследовать** данные — zoom, hover, фильтр серий в легенде',
              '**Plotly Express** — один вызов на типичный график: scatter, histogram, line',
              'Scatter: цвет по категории, hover с дополнительными полями (id, сегмент)',
              'Histogram с marginal box — распределение и квантили на одном экране'],
  'notes': 'California Housing: px.scatter area vs price.',
  'visuals': [],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'px.scatter, px.histogram, write_html.'}},
 {'title': 'Plotly: продвинутые возможности',
  'bullets': ['ML-задача: **3D**, анимация, несколько графиков на одной странице',
              'Несколько subplots в одном plotly-figure'],
  'notes': '3D только для демо — не для production EDA на миллионах строк.',
  'visuals': [{'description': '3D scatter с color=target + inset animation_frame slider (год). Подписи осей x, y, z.',
               'output': 'plotly_3d_animation_demo.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'scatter_3d, animation_frame, make_subplots.'}},
 {'title': 'Распределение одной переменной: гистограмма и KDE',
  'bullets': ['ML-задача: понять распределение признака — нужна ли **трансформация** (`log1p`), есть ли моды',
              "`sns.histplot(df['income'], kde=True)` — гистограмма + кривая плотности",
              'Ищем: **heavy tail** (повод для `log1p`), **мультимодальность** (смешаны группы), выбросы',
              'Параметр `bins`: мало — скрыты детали, много — шум'],
  'notes': 'Показать один признак с heavy tail до и после log1p.',
  'visuals': [{'description': 'Две панели: histplot+kde с heavy tail слева; после log1p справа — более симметричное '
                              'распределение.',
               'output': 'histplot_kde_heavy_tail.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'sns.histplot kde=True, bins, log1p.'}},
 {'title': 'Быстрый поиск выбросов: Box plot',
  'bullets': ['ML-задача: найти аномалии по **IQR**, сравнить распределения по группам',
              "`sns.boxplot(data=df, x='category', y='price')` — медиана, квантили, выбросы за «усами»",
              'Ограничение: **не показывает форму** распределения — бимодальность скрывается',
              "Интерактив: `px.box(df, x='category', y='price', points='all')` — hover на каждой точке"],
  'notes': 'Fare по Pclass — классический boxplot пример.',
  'visuals': [{'description': 'sns.boxplot x=category y=price, 3 категории, outliers точками за whiskers. Подписи '
                              'медиана/IQR.',
               'output': 'boxplot_outliers_iqr.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': "sns.boxplot, px.box points='all'."}},
 {'title': 'Сравнение распределений: Violin plot',
  'bullets': ['ML-задача: сравнить распределение **таргета** по категориальным признакам',
              "`sns.violinplot(data=df, x='city', y='income')` — объединяет box plot и KDE",
              'Инсайт: «В Москве средний доход выше, но форма **бимодальная**» — box plot это скрыл бы',
              'Идеален для анализа таргета в **регрессии**: сразу видно, где предсказывать сложно',
              "Plotly: `px.violin(df, x='city', y='income', box=True, points='outliers')`"],
  'notes': 'Сравнить box vs violin на одних данных — бимодальность.',
  'visuals': [{'description': 'Панели: boxplot (скрывает бимодальность) vs violinplot (две «горбы» в одном городе). 3 '
                              'города.',
               'output': 'violin_vs_box_bimodal.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'sns.violinplot, px.violin box=True.'}},
 {'title': 'Связь двух непрерывных признаков: Scatter и marginal distributions',
  'bullets': ['ML-задача: увидеть **линейную/нелинейную** связь, кластеры, выбросы в паре признаков',
              "`sns.scatterplot(data=df, x='area', y='price', hue='city')`",
              'Ищем: линейный тренд, нелинейность (нужны полиномы или деревья), кластеры'],
  'notes': 'California: MedInc vs MedHouseVal.',
  'visuals': [{'description': 'jointplot kind=hex: центральный hexbin scatter + marginal hist сверху и справа. hue по '
                              'city на inset scatter.',
               'output': 'jointplot_hex_marginals.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'scatterplot hue, jointplot hex.'}},
 {'title': 'Пропуски в данных: missingno',
  'bullets': ['ML-задача: увидеть **паттерны пропусков** — случайные или систематические',
              'Библиотека `missingno` визуализирует пропуски одной командой'],
  'notes': 'Titanic или synthetic MNAR для демо dendrogram.',
  'visuals': [{'description': 'msno.matrix слева (белые полосы = NaN) + msno.dendrogram справа (кластеры признаков с '
                              'похожими пропусками).',
               'output': 'missingno_matrix_dendrogram.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'msno.matrix, msno.dendrogram.'}},
 {'title': 'Мультиколлинеарность: Heatmap корреляций',
  'bullets': ['ML-задача: найти **дублирующие признаки** и их связь с таргетом',
              "`sns.heatmap(df.corr(), annot=True, cmap='coolwarm', center=0)` — карта с центром в нуле",
              'Ищем: $|r| > 0.9$ — кандидаты на удаление; высокая корреляция с **таргетом**',
              "Пирсон по умолчанию (линейная связь); для нелинейной — `method='spearman'`",
              "Plotly: `px.imshow(df.corr(), text_auto='.2f', color_continuous_scale='RdBu_r')`"],
  'notes': 'California Housing — corr heatmap 8 признаков.',
  'visuals': [{'description': 'Heatmap 8×8 corr, annot=True, coolwarm center=0. Пара признаков с |r|>0.9 выделена '
                              'рамкой.',
               'output': 'correlation_heatmap_multicollinearity.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'df.corr(), sns.heatmap, spearman.'}},
 {'title': 'Детектирование дрейфа данных: ECDF и overlay',
  'bullets': ['ML-задача: сравнить распределения **train/test/production** — выявить **Data Drift**',
              'Расхождение кривых означает **дрейф** — модель может деградировать'],
  'notes': 'Synthetic shift: mean age train vs prod +5 лет.',
  'visuals': [{'description': 'ECDF две кривые train (синяя) vs prod (оранжевая) — заметный сдвиг по оси X. Подпись '
                              '«Data Drift».',
               'output': 'ecdf_train_prod_drift.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'sns.ecdfplot train vs test, overlay KDE.'}},
 {'title': 'Дисбаланс классов: Count plot',
  'bullets': ['ML-задача: увидеть распределение классов в **классификации**',
              "`sns.countplot(data=df, x='target')` — частоты каждого класса",
              'Если соотношение **100:1** — accuracy бесполезна; нужны `class_weight`, **PR-AUC**',
              'Стройте **в начале** каждого классификационного проекта',
              "Альтернатива: `df['target'].value_counts().plot(kind='bar')` или `px.histogram(df, x='target')`"],
  'notes': 'Credit fraud или imbalanced OpenML dataset.',
  'visuals': [{'description': 'countplot с двумя классами 95% vs 5% — явный дисбаланс. Подпись «не используйте '
                              'accuracy».',
               'output': 'countplot_class_imbalance.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'sns.countplot target, value_counts bar.'}},
 {'title': 'Границы решений: Decision Boundaries',
  'bullets': ['ML-задача: визуализировать, как **классификатор** разделяет пространство признаков',
              '`DecisionBoundaryDisplay.from_estimator(clf, X, y)` — для **2D**-классификаторов',
              'Видим: линейная граница (логрег), нелинейная (деревья, SVM RBF), **переобучение**',
              'Кастомизация: `alpha=0.3` для прозрачности + overlay scatter точек'],
  'notes': 'make_moons + LogisticRegression vs RandomForest.',
  'visuals': [{'description': 'Две панели: линейная граница (логрег, XOR fail) vs нелинейная (RBF SVM, XOR ok). '
                              'Scatter точек поверх.',
               'output': 'decision_boundary_linear_nonlinear.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'DecisionBoundaryDisplay, make_moons.'}},
 {'title': 'Многомерные данные: PCA, t-SNE, UMAP',
  'bullets': ['ML-задача: визуализировать многомерные данные в **2D/3D**, увидеть кластеры',
              '**PCA** — линейное снижение размерности, сохраняет **глобальную** структуру'],
  'notes': 'Digits или Iris — PCA vs UMAP side by side.',
  'visuals': [{'description': 'Панели: PCA 2D scatter color=target vs UMAP 2D — UMAP показывает tighter clusters. '
                              'Легенда классов.',
               'output': 'pca_vs_umap_clusters.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'PCA, UMAP/t-SNE scatter color=target.'}},
 {'title': 'Кластеризация: Silhouette plot и Elbow method',
  'bullets': ['ML-задача: выбрать оптимальное число кластеров $K$ в **K-means**',
              '**Elbow method**: график WCSS от $K$ — ищем «локоть»',
              '`fig, (ax1, ax2) = plt.subplots(1, 2)` — elbow и silhouette рядом'],
  'notes': 'make_blobs n_clusters=3 для демо.',
  'visuals': [{'description': '1×2: elbow curve WCSS vs K (локоть при K=3) + silhouette plot bar chart по кластерам.',
               'output': 'elbow_silhouette_kmeans.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'elbow WCSS, silhouette_plot KMeans.'}},
 {'title': 'Диагностика регрессии: Residual plot',
  'bullets': ['ML-задача: проверить качество регрессии, найти **систематические ошибки**',
              '`sns.residplot(x=y_pred, y=y_true - y_pred, lowess=True)` — остатки vs предсказания',
              'Хорошая модель: **хаотичное облако** вокруг нуля (гомоскедастичность)',
              "Plotly: `px.scatter(x=y_pred, y=residuals, trendline='lowess')`"],
  'notes': 'Показать хороший vs funnel-shaped residplot.',
  'visuals': [{'description': 'Две панели: residplot хаотичный (good) vs воронка (heteroscedastic bad). LOWESS линия '
                              'красная.',
               'output': 'residual_plot_good_bad.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'residplot, residuals vs y_pred.'}},
 {'title': 'Нормальность остатков: Q-Q plot',
  'bullets': ['ML-задача: проверить **нормальность ошибок** (важно для доверительных интервалов)',
              "`statsmodels.api.qqplot(residuals, line='s')` — квантили остатков vs квантили нормального распределения",
              'Точки должны лежать на **прямой**; отклонения на хвостах — **тяжёлые хвосты**',
              'Для ML: при тяжёлых хвостах используйте **MAE/Huber** вместо MSE'],
  'notes': 'Сравнить qqplot нормальных остатков vs t-distribution tails.',
  'visuals': [{'description': "Q-Q plot: точки вдоль диагонали line='s', лёгкое отклонение на верхнем хвосте. Подписи "
                              'theoretical vs sample quantiles.',
               'output': 'qqplot_residuals_normality.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': "statsmodels qqplot residuals line='s'."}},
 {'title': 'Предсказание vs реальность',
  'bullets': ['ML-задача: **визуально** оценить качество регрессии',
              '`sns.scatterplot(x=y_true, y=y_pred)` + диагональная линия $y = x$',
              'Хорошая модель: точки **плотно вокруг диагонали**',
              "Метрики в заголовке: `ax.set_title(f'R2={r2:.2f}, RMSE={rmse:.2f}')`",
              "Plotly: `px.scatter(x=y_true, y=y_pred, trendline='ols')` + диагональ"],
  'notes': 'California regressor pred vs true.',
  'visuals': [{'description': 'Scatter y_true vs y_pred с красной диагональю y=x, title R2=0.85 RMSE=0.45. Точки вдоль '
                              'диагонали.',
               'output': 'predicted_vs_actual_diagonal.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'scatter y_true y_pred, y=x line, R2 RMSE.'}},
 {'title': 'Диагностика классификации: Confusion Matrix',
  'bullets': ['ML-задача: понять, **какие классы** модель путает',
              '`ConfusionMatrixDisplay.from_estimator(model, X, y)` — тепловая карта ошибок',
              'Ищем: большие **off-diagonal** элементы, дисбаланс FN vs FP',
              "Кастомизация: `cmap='Blues'`, `annot=True`, `fmt='.0f'`"],
  'notes': 'Multiclass digits — какие цифры путаются.',
  'visuals': [{'description': 'Confusion matrix heatmap 3×3, Blues cmap, annot числа. Off-diagonal 2→3 выделен.',
               'output': 'confusion_matrix_heatmap.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': "ConfusionMatrixDisplay, normalize='true'."}},
 {'title': 'Качество при разных порогах: ROC и PR кривые',
  'bullets': ['ML-задача: выбрать **оптимальный порог**, сравнить модели',
              '`RocCurveDisplay` и `PrecisionRecallDisplay` из sklearn',
              '**PR-кривая** важнее при сильном дисбалансе классов'],
  'notes': 'Imbalanced dataset — PR vs ROC side by side.',
  'visuals': [{'description': '1×2: ROC (AUC=0.92) с diagonal baseline + PR curve. Две модели overlay разными цветами.',
               'output': 'roc_pr_curves_overlay.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'RocCurveDisplay, PrecisionRecallDisplay overlay.'}},
 {'title': 'Переобучение vs недообучение: Learning Curve',
  'bullets': ['ML-задача: понять, нужно ли **больше данных** или **более сложная модель**',
              '`LearningCurveDisplay.from_estimator(model, X, y)` — кривые train/validation',
              'Train высоко, Val низко — **переобучение**; обе низкие — **недообучение**; обе высокие — оптимум'],
  'notes': 'DecisionTree max_depth=20 vs 3 — over vs underfit.',
  'visuals': [{'description': 'Learning curve: train score высокий, val score низкий (gap) — overfitting. fill_between '
                              'CI. Подписи train/validation.',
               'output': 'learning_curve_overfitting.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'LearningCurveDisplay, fill_between CI.'}},
 {'title': 'Кросс-валидация: стабильность модели',
  'bullets': ['ML-задача: оценить **variance** модели, а не только среднее качество',
              'Box plot метрик по фолдам: `sns.boxplot(data=cv_scores)`',
              "Line plot: `plt.plot(cv_scores, marker='o')` — видны **аномальные фолды**",
              'Большой разброс означает **нестабильность** модели',
              'Сравнение моделей: `sns.boxplot` для нескольких наборов `cv_scores`'],
  'notes': '5-fold CV scores двух моделей — boxplot compare.',
  'visuals': [{'description': 'Boxplot CV scores двух моделей (Model A узкий, Model B широкий) + line plot fold scores '
                              'с outlier fold.',
               'output': 'cv_scores_stability_boxplot.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'cross_val_score, boxplot по фолдам.'}},
 {'title': 'Подбор гиперпараметров: Grid Search visualization',
  'bullets': ['ML-задача: выбрать **лучшие гиперпараметры**, увидеть взаимодействия',
              'Heatmap: `sns.heatmap(grid_results)` для 2D grid search (`max_depth` vs `min_samples_leaf`)',
              'Line plot: зависимость метрики от одного параметра с **доверительными интервалами**',
              'Часто есть **«плато»** — широкий диапазон параметров даёт схожее качество',
              'Plotly: `px.imshow` для интерактивного heatmap с hover'],
  'notes': 'RandomForest grid max_depth × min_samples_leaf.',
  'visuals': [{'description': 'Heatmap grid search max_depth × min_samples_leaf, annot F1-score. Плато в центре '
                              '(robust region).',
               'output': 'grid_search_heatmap_plateau.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'GridSearchCV results heatmap, line plot param.'}},
 {'title': 'Важность признаков: Permutation Importance',
  'bullets': ['ML-задача: понять, **какие признаки** влияют на предсказания',
              'Для деревьев: `model.feature_importances_` — **смещено** к high-cardinality признакам',
              '**Permutation Importance** (честнее): перемешиваем признак, смотрим **падение метрики**',
              '`sns.barplot(x=result.importances_mean, y=feature_names)`',
              'Error bars: `plt.barh(y, x, xerr=std)` — показать **variance** важности'],
  'notes': 'Сравнить feature_importances_ vs permutation на одном RandomForest.',
  'visuals': [{'description': 'Horizontal barh permutation importance top-10 features с xerr error bars. Один признак '
                              'с широкими error bars.',
               'output': 'permutation_importance_barh.png'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'permutation_importance, barh xerr.'}},
 {'title': 'Стили и темы: единый дизайн для проекта',
  'bullets': ['ML-задача: **консистентный** визуальный стиль для всех графиков проекта',
              "`plt.style.use('seaborn-v0_8-whitegrid')` — готовые стили matplotlib",
              "`sns.set_theme(style='whitegrid', palette='husl')` — тема seaborn",
              "Кастомная палитра: `sns.set_palette(['#FF6B6B', '#4ECDC4', '#45B7D1'])`",
              "`rcParams`: `plt.rcParams['figure.figsize'] = (12, 8)`, `plt.rcParams['font.size'] = 12`",
              'Для презентаций: **увеличенный шрифт**, минималистичный стиль, контрастные цвета'],
  'notes': 'Один график до/после set_theme.',
  'visuals': [],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'set_theme, set_palette, rcParams.'}},
 {'title': 'Общие техники: overlay и комбинирование графиков',
  'bullets': ['ML-задача: показать **несколько распределений/моделей** на одном графике для сравнения',
              "Overlay гистограмм: `plt.hist(train, alpha=0.5, label='train'); plt.hist(test, alpha=0.5, "
              "label='test')`",
              'Overlay линий: `plt.plot(train_scores); plt.plot(val_scores)`'],
  'notes': 'Overlay train/test hist — классика drift check.',
  'visuals': [{'description': 'Overlay гистограмм train и test с alpha=0.5.',
               'output': 'overlay_hist_train_test.png',
               'size': 'compact'},
              {'description': 'Две линии train_scores и val_scores на одних осях.',
               'output': 'overlay_lines_scores.png',
               'size': 'compact'}],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'overlay hist, FacetGrid, twinx caution.'}},
 {'title': 'Размер и DPI: подготовка для разных целей',
  'bullets': ['ML-задача: оптимизировать **размер и качество** графика для статьи, презентации, дашборда',
              '`figsize=(width, height)` в дюймах: $(10, 6)$ для статьи, $(16, 9)$ для презентации',
              "`plt.savefig('plot.png', dpi=300, bbox_inches='tight', facecolor='white')`"],
  'notes': 'Таблица рекомендаций: экран/print/journal.',
  'visuals': [],
  'notebook': {'include': True, 'kinds': ['example'], 'hint': 'figsize, savefig dpi=300, aspect ratio.'}},
 {'title': 'Антипаттерны и best practices',
  'bullets': ['**Антипаттерны**: pie charts (замените на bar), 3D графики (искажают), rainbow colormaps (не '
              'colorblind-friendly), отсутствие labels',
              '**Best practices**: один график = один инсайт; всегда **title/labels/units**; тест на коллегах (**5 '
              'секунд** на понимание)',
              'Colorblind-friendly: `viridis`, `plasma` — избегайте **красно-зелёных** сочетаний',
              'Для презентаций: минимум текста, крупные шрифты, контрастные цвета, белый фон',
              'Для статей: векторные форматы (SVG/PDF), **grayscale-friendly** палитры'],
  'notes': 'Показать pie vs bar и rainbow vs viridis на одних данных.',
  'visuals': [{'description': '2×2: pie (bad) vs bar (good) same data; rainbow jet cmap (bad) vs viridis (good) '
                              'heatmap. Красные крестики/зелёные галочки.',
               'output': 'viz_antipatterns_best_practices.png'}]},
 {'title': 'Итоговый чек-лист: какой график для какой задачи',
  'bullets': ['**Распределение** → hist + KDE | **Выбросы** → box plot',
              '**Сравнение групп** → violin plot | **Связь признаков** → scatter',
              '**Пропуски** → матрица пропусков | **Корреляции** → heatmap',
              '**Дрейф train/test** → overlay гистограмм | **Дисбаланс** → count plot',
              '**Регрессия** → predicted vs actual, residuals, Q-Q | **Классификация** → confusion matrix, ROC',
              '**Grid search** → heatmap | **Переобучение** → learning curve | **Важность** → permutation importance',
              'Библиотеки: **seaborn** для EDA, **plotly** для интерактива, **matplotlib** для кастомизации, '
              '**pandas** для быстрых графиков'],
  'notes': 'Финальный слайд — можно распечатать как шпаргалку.',
  'visuals': []}]
