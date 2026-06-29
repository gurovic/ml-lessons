# Агент генерации code.ipynb

## Проблема

После сборки презентации нужен практический Jupyter-ноутбук: примеры кода, эксперименты, интерактивные визуализации. Делать это вручную по 20+ слайдам долго; не все слайды требуют кода (теория, мотивация).

## Решение

Агент **notebook_generator** читает `slides_json/` и `info.json`, **отбирает слайды, где уместен код**, формирует промпт для AI. AI возвращает структурированный JSON с ячейками; агент собирает `code.ipynb`.

Код в ячейках опирается на **docs/pandas_numpy_basics.md**: базовые pandas/numpy-конструкции для загрузки, EDA, подготовки признаков, `X`/`y`, простых метрик и подготовки графиков. Если урок не требует более сложного API, использовать эти паттерны.

### Когда включать

**После** `pptx_builder`, когда JSON, assets и (желательно) проверка `presentation.pptx` завершены. См. **docs/pipeline.md**.

### Типы содержимого ноутбука

| Тип | `kind` | Примеры |
|-----|--------|---------|
| Пример кода | `example` | `DecisionTreeClassifier`, `plot_tree`, метрики |
| Эксперимент | `experiment` | сравнение Gini/entropy, время обучения, переобучение vs глубина |
| Визуализация | `viz` | matplotlib/seaborn, воспроизведение картинки из `assets/` |
| Интерактив | `interactive` | `ipywidgets` — слайдеры глубины, порога, критерия |

Один слайд может дать несколько ячеек и несколько `kind`.

## Отбор слайдов

### Явно в JSON (приоритет)

Опциональное поле `notebook` в слайде:

```json
{
  "notebook": {
    "include": true,
    "kinds": ["example", "experiment"],
    "hint": "сравнить criterion gini и entropy на iris"
  }
}
```

- `"notebook": false` или `"include": false` — **никогда** не включать.
- `"include": true` — **всегда** включать (с подсказкой `hint`).

### Эвристики (если поля нет)

Включить слайд, если выполняется **хотя бы одно**:

- в `notes` есть `jupyter`, `notebook`, `sklearn`, `ipywidgets`;
- в буллетах есть вызовы API: `DecisionTree`, `plot_tree`, `.fit(`, `export_`, `class_weight`;
- есть `visuals` **и** в описании/заметках matplotlib, graphviz, seaborn, интерактив;
- в заметках явный эксперимент: сравнение, скорость, замер времени, демо кода.

**Не включать** (если нет явного `notebook.include: true`):

- чисто теоретические слайды без кода/визуализаций (вогнутость, жадность, «зачем сегодня»);
- мотивационные игры без кода (Угадай число, Акинатор — только ссылка);
- слайды, где единственное «показать» — устное объяснение без кода.

Эвристики можно уточнять в `agents/notebook_utils.py`; список слайдов кандидатов виден через `--list`.

## Формат ответа AI

Только JSON (без markdown-обёртки, если возможно):

```json
{
  "sections": [
    {
      "slide_title": "Дерево решений в sklearn",
      "kind": "example",
      "cells": [
        {
          "type": "markdown",
          "source": "## Дерево решений в sklearn\n\nКраткий текст."
        },
        {
          "type": "code",
          "source": "from sklearn.tree import DecisionTreeClassifier\n..."
        }
      ]
    }
  ]
}
```

- `slide_title` — **точно** как `title` в JSON слайда (для связи с презентацией).
- `source` — массив строк или одна строка; переносы через `\n`.
- В начале ноутбука — **одна** setup-ячейка `# Setup` (импорты, `np.random.seed(42)`, `%matplotlib inline`). Сборщик добавляет её автоматически; в секциях — **без повторных** импортов и seed.
- Pandas/numpy-фрагменты держать в стиле **docs/pandas_numpy_basics.md**.

### Стиль ячеек

- **Setup один раз:** `# Setup` → импорты (`numpy`, `pandas`, `matplotlib`, частые sklearn) → `np.random.seed(42)` → `%matplotlib inline`.
- **Последующие ячейки:** только код слайда/этапа; импорт локально — только если модуль ещё не был в setup и редок для урока.
- **Лаконичность:** 3–10 строк на пример; простые sklearn/pandas one-liner'ы; комментарии — только где неочевидно.
- **pandas/numpy:** сначала выбирать базовые конструкции из **docs/pandas_numpy_basics.md**.
- **Без продвинутого Python:** walrus, сложные comprehensions, лишний boilerplate.

## CLI

```powershell
# Список отобранных слайдов
python agents/notebook_generator.py lessons/derevo_resheniy --list

# Промпт для AI
python agents/notebook_generator.py lessons/derevo_resheniy

# Сохранить ноутбук (файл или stdin)
python agents/notebook_generator.py lessons/derevo_resheniy --save response.json
type response.json | python agents/notebook_generator.py lessons/derevo_resheniy --save
```

Выход: `lessons/<урок>/code.ipynb`.

## Рецензия ноутбуков (notebook_reviewer)

**После** создания `code.ipynb` и `project.ipynb` — опциональная проверка агентом **notebook_reviewer** (промпт: `agents/prompts/notebook_reviewer.md`).

### Программная проверка (`--check-only`)

- наличие файлов, валидный JSON nbformat;
- одна setup-ячейка `# Setup` с `%matplotlib inline` и `np.random.seed(42)`;
- импорты и seed не повторяются в других code-ячейках;
- синтаксис code-ячейок (`compile`);
- `code.ipynb`: заголовки секций совпадают с отбором слайдов (`notebook_utils.select_slides_for_notebook`);
- `project.ipynb`: «Решение:», `final_model`/`final_pipe`, один `train_test_split`, без `make_*`;
- нет перекрёстных ссылок на номера слайдов.

### AI-рецензия и правки

```powershell
python agents/notebook_reviewer.py lessons/lineynaya_regressiya --check-only
python agents/notebook_reviewer.py lessons/lineynaya_regressiya
python agents/notebook_reviewer.py lessons/lineynaya_regressiya --save notebook_review.md
python agents/notebook_reviewer.py lessons/lineynaya_regressiya --apply fixes.json
python agents/notebook_reviewer.py --pilot
```

Отчёт: `notebook_review.md`. Исправления: JSON с полями `report`, `code.sections`, `project.sections` — см. промпт.

## project.ipynb (мини-проект)

Сквозной end-to-end сценарий на реальных данных — см. **docs/project_notebook.md**.  
Сборка шаблонов:

- `python agents/build_project_notebooks.py` — `project.ipynb` для lineynaya_regressiya, logisticheskaya_regressiya, derevo_resheniy
- `python agents/build_pandas_viz_notebooks.py` — `code.ipynb` и `project.ipynb` для pandas и vizualizatsiya
- `python agents/rebuild_code_ipynb.py <lesson_dir>` — нормализация существующего `code.ipynb`

## Отвергнутые альтернативы

| Альтернатива | Почему нет |
|--------------|------------|
| Один код-блок на весь урок | теряется связь со слайдами; сложно править |
| Ноутбук из plan.md | plan устаревает; JSON — источник для пересборки pptx и ноутбука |
| Автогенерация без AI | слишком разнообразные сценарии (эксперименты, widgets) |

## Зависимости ноутбука

В `requirements.txt`: `scikit-learn`, `ipywidgets`, `pandas` (для типичных примеров). В setup-ячейке — `%matplotlib inline` при необходимости.
