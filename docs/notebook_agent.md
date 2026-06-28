# Агент генерации code.ipynb

## Проблема

После сборки презентации нужен практический Jupyter-ноутбук: примеры кода, эксперименты, интерактивные визуализации. Делать это вручную по 20+ слайдам долго; не все слайды требуют кода (теория, мотивация).

## Решение

Агент **notebook_generator** читает `slides_json/` и `info.json`, **отбирает слайды, где уместен код**, формирует промпт для AI. AI возвращает структурированный JSON с ячейками; агент собирает `code.ipynb`.

### Когда включать

**После** `pptx_builder` (или параллельно, когда JSON и assets финальны).

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
- В начале ноутбука агент добавляет ячейку setup (импорты, `random_state=42`).

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

## project.ipynb (мини-проект)

Сквозной end-to-end сценарий на реальных данных — см. **docs/project_notebook.md**.  
Сборка шаблонов: `python agents/build_project_notebooks.py` (пока для lineynaya и logisticheskaya).

## Отвергнутые альтернативы

| Альтернатива | Почему нет |
|--------------|------------|
| Один код-блок на весь урок | теряется связь со слайдами; сложно править |
| Ноутбук из plan.md | plan устаревает; JSON — источник истины для презентации |
| Автогенерация без AI | слишком разнообразные сценарии (эксперименты, widgets) |

## Зависимости ноутбука

В `requirements.txt`: `scikit-learn`, `ipywidgets`, `pandas` (для типичных примеров). В setup-ячейке — `%matplotlib inline` при необходимости.
