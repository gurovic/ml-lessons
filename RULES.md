# Правила работы для AI-ассистента (Agents mode)

## Основные принципы

1. **Самостоятельность** — выполняй задачу без лишних уточнений, если запрос однозначен.
2. **Минимализм** — делай только то, что запрошено.
3. **Уточнение** — спрашивай разрешение только если запрос неоднозначен или затрагивает необратимые действия.
4. **Минимальный рабочий вариант**.
5. **Следование запросу** — уточни, если неоднозначно.
6. **RULES.md** — единственный источник правил.
7. **Git workflow** — работа **в ветке `main`**: коммит и push в `main`. GitHub issue — **опционально** для крупных задач (см. **docs/issue_workflow.md**). Отдельные feature-ветки и PR — не обязательны.
8. **Сначала документ, потом код** — архитектурные решения, изменения пайплайна и новые правила сначала фиксируются в `.md`-файлах; реализация — только после этого (см. раздел ниже).

## Архитектурные решения и изменения пайплайна

Перед реализацией любого из перечисленного **сначала** записать решение в markdown, **затем** менять код, промпты и RULES.md:

- архитектура модулей и форматов данных (JSON-слайды, формулы, визуализации и т.п.);
- изменения пайплайна (новые шаги, агенты, порядок работы);
- новые или изменённые правила для AI и пользователя.

**Где хранить:** папка `docs/` в корне проекта (например, `docs/formulas.md`, `docs/pipeline.md`). Имя файла — по теме решения, латиницей с подчёркиваниями.

**Что должно быть в документе:**
1. Проблема / мотивация.
2. Принятое решение и альтернативы, которые отвергли.
3. Формат данных, API, порядок шагов — всё, что нужно для реализации.
4. План миграции (если ломается существующее).

**Порядок работы:** обсуждение → запись в `docs/*.md` → согласование (если нужно) → реализация → при необходимости обновить RULES.md и промпты агентов по итогам.

Исключение: мелкие багфиксы и опечатки — править код сразу, без отдельного архитектурного документа.

## Проверка правильности

1. После каждого изменения файла — проверь успешность записи.
2. После каждого коммита — проверь git push.
3. После запуска скрипта — проверь результат.
4. Если файл не обновился — исправь и повтори.

## Структура проекта

- Уроки в папке lessons/.
- Архитектурные решения и описания пайплайна — в папке docs/.
- Название папки урока — транслитерация латиницей с подчеркиваниями.
- Название урока (русское) — в README.md.

## Стиль кода в примерах

Единые правила для `code_examples` в slides_json, `code.ipynb` и `project.ipynb`:

1. **Максимальная лаконичность** — минимум строк, без boilerplate; простые конструкции sklearn/pandas вместо многословных паттернов.
2. **Импорты:** в **ноутбуке** — один раз в `# Setup`; в последующих ячейках не повторять. На **слайдах** (`code_examples`) — в **каждом** блоке сохранять нужные `import`/`from`, чтобы фрагмент был понятен сам по себе (слайд не опирается на код с предыдущих слайдов).
3. **Длина фрагмента на слайде** — 3–5 строк в `source`; без `%matplotlib inline`; **~60 символов в строке** (узкая колонка) — см. `agents/slide_code_utils.py` (`CODE_MAX_LINE_LEN`).
4. **Базовый синтаксис** — без walrus, сложных comprehensions и лишней обработки ошибок; комментарии на русском, кратко.
5. **pandas/numpy по справочнику** — во всех ноутбуках предпочитать базовые конструкции из **docs/pandas_numpy_basics.md**; более сложный API использовать только если этого требует тема урока.
6. **Связность** — `project.ipynb` передаёт `df`, `X_train` и т.д. между этапами; `code.ipynb` — самодостаточен после setup.
7. **Rich text в JSON** — `$...$` формулы, `**жирный**`, `` `inline-код` `` в буллетах (рендер: `agents/rich_text.py`, см. docs/formulas.md).

Подробнее: **docs/pandas_numpy_basics.md**, **docs/slide_code_agent.md**, **docs/notebook_agent.md**, **docs/project_notebook.md**.

## Состав папки урока

- plan.md — создаётся пользователем
- **presentation.pptx** — **основной артефакт для автора**: проверка и правка слайдов в PowerPoint (см. docs/pipeline.md)
- assets/
- slides_json/ — JSON-слайды (01.json, 02.json, …); **редактируют агенты**, не автор вручную; источник для пересборки pptx
- review.md — опциональный отчёт агента-рецензента (до сборки pptx; перезаписывается при повторной рецензии)
- **author_feedback.md** — замечания автора после проверки pptx (чеклисты по слайдам). **Всегда сохранять** при перегенерации урока: это накопленный список прошлых багов и правок; агенты **читают файл перед** правкой JSON/PNG/pptx и **не удаляют** его. Не перезаписывается `lesson_reviewer`. Новые замечания — дописывать; выполненные — помечать `[x]`.
- code.ipynb — короткие примеры по слайдам (см. docs/notebook_agent.md)
- project.ipynb — сквозной мини-проект на реальных данных (см. docs/project_notebook.md)
- info.json — тема, автор (email, Telegram), продолжительность

## Агенты

### Оркестратор слайдов (agents/slides_orchestrator.py)
- Проходит по plan.md, формирует промпты, сохраняет JSON в slides_json/.
- Использование: python agents/slides_orchestrator.py <lesson_dir>
- --save '<JSON>' — сохранить слайд
- --visuals — проверить/сгенерировать визуализации
- --save-script <file> '<code>' — сохранить и запустить скрипт

### Сборщик презентации (agents/pptx_builder.py)
- Из JSON собирает presentation.pptx с титульным слайдом из info.json.
- Формулы в `$...$`, `**жирный**`, `` `inline-код` `` в тексте (см. docs/formulas.md, agents/rich_text.py).
- **Буллеты:** маркер `•` добавляется автоматически при сборке (см. раздел «Значки буллетов»); в `slides_json` писать текст **без** маркера.
- До 4 иллюстраций на слайд — сетка/столбик в правой колонке (см. docs/visuals.md). Если **>3** графиков или картинки перегружены — допустимо (и предпочтительно) вынести их на **отдельный слайд сразу после** текущего.
- Использование: python agents/pptx_builder.py <lesson_dir>

### Генератор визуализаций (agents/viz_generator.py)
- Промпт: agents/prompts/viz_generator.md
- Формирует промпт для генерации Python-скрипта диаграммы.

### Пайплайн иллюстраций (agents/visuals_pipeline.py)
- Запуск `assets/generate_visuals.py` (если есть), программная проверка PNG, пересборка pptx.
- AI-рецензия качества картинок: `--review` → промпт `agents/prompts/visuals_reviewer.md`.
- **Эталон стиля:** `lessons/lineynaya_regressiya` — при крупных правках `viz_style.py` сначала проверять там (`--pilot`); затем `--all-lessons` или по урокам.
- Использование: `python agents/visuals_pipeline.py --pilot` | `lessons/<slug>` | `--check-only` | `--generate-only` | `--review` | `--all-lessons --generate-only`

### Рецензент урока (agents/lesson_reviewer.py)
- Опционально до сборки pptx: фактология, логика, понятность, лаконичность, полнота по JSON; замечания вносят агенты в slides_json/, не автор вручную.
- Промпт: agents/prompts/lesson_reviewer.md, описание: docs/reviewer_agent.md
- Использование: python agents/lesson_reviewer.py <lesson_dir>
- --save [file] — сохранить отчёт в review.md (из файла или stdin)

### Генератор ноутбука (agents/notebook_generator.py)
- По JSON-слайдам отбирает слайды, где нужен код, формирует промпт для AI → `code.ipynb`.
- Описание: docs/notebook_agent.md
- Использование: python agents/notebook_generator.py <lesson_dir>
- --list — показать отобранные слайды
- --save [file] — собрать ноутбук из JSON-ответа AI (файл или stdin)

### Рецензент ноутбуков (agents/notebook_reviewer.py)
- Проверяет `code.ipynb` и `project.ipynb`: синтаксис, setup, imports, покрытие слайдов, narrative pipeline.
- AI-рецензия и правки: промпт `agents/prompts/notebook_reviewer.md`; отчёт в `notebook_review.md`.
- Описание: docs/notebook_agent.md (раздел «Рецензия»)
- Использование: python agents/notebook_reviewer.py <lesson_dir> | --pilot
- --check-only — только программная проверка
- --save [file] — сохранить markdown-отчёт AI
- --apply [file] — применить JSON с исправленными sections к ipynb

### Агент примеров кода на слайдах (agents/slide_code_agent.py)
- Короткие фрагменты Python на слайдах с практикой (`code_examples` в JSON).
- Описание: docs/slide_code_agent.md
- Промпт: agents/prompts/slide_code_agent.md
- Bootstrap: agents/slide_code_bootstrap.py
- Использование: python agents/slide_code_agent.py <lesson_dir>
- --list — кандидаты без code_examples
- --prompt — промпт для AI
- --save [file] — применить JSON-ответ к slides_json/
- --apply — bootstrap-сниппеты для слайдов с notebook.include

### Утилиты пайплайна

- `agents/normalize_slides_code_batch.py` — пакетная нормализация длины строк в `code_examples` (все уроки).
- `agents/rebuild_code_ipynb.py <lesson_dir>` — пересборка `code.ipynb` из существующего ноутбука (setup + секции, импорты в Setup).

### Агент «Источники и практика» (agents/references_agent.py)
- Классические статьи (промпт для AI) + Colab-ссылки на `code.ipynb` / `project.ipynb` + QR на слайде.
- Описание: docs/colab_references.md, формат слайда: docs/references_slide.md
- Промпт: agents/prompts/references_agent.md
- Использование: python agents/references_agent.py <lesson_dir>
- --list — показать статьи и Colab-URL
- --prompt — промпт для AI (список статей)
- --save [file] — сохранить JSON слайда (файл или stdin)
- --apply — вставить/обновить слайд в slides_json/ и пересобрать presentation.pptx

### Агент проверки ссылок (agents/link_checker_agent.py)
- HTTP-доступность, paywall-эвристики для paper, формат Colab URL, поля `link` в slides_json.
- Описание: docs/link_checker_agent.md
- Промпт (LLM-альтернативы): agents/prompts/link_checker_agent.md
- Использование: python agents/link_checker_agent.py <lesson_dir> | --all
- --fix — исправить Colab URL из project_config (без угадывания paper URL)
- --offline — без HTTP (формат и локальные файлы)
- --llm — промпт для AI с бесплатными full-text альтернативами
- Пакетно: python agents/apply_all_link_checks.py

### Мини-проект (project.ipynb)
- Сквозной **непрерывный** сценарий на реальных данных — docs/project_notebook.md
- **Не изолированные демо:** EDA → решение → следующий шаг использует результат (очищенный `df`, выбранная модель); один test-set на весь ноутбук
- Явные markdown-ячейки «**Решение:** …» между этапами; после сравнения вариантов — переменная `final_model` / `final_pipe`
- Шаблоны: `python agents/build_project_notebooks.py`, `python agents/build_pandas_viz_notebooks.py`
- Промпт для ручной сборки: agents/prompts/build_project_notebooks.md

## Порядок работы над уроком

Подробно: **docs/pipeline.md**. Кратко:

1. Создать plan.md (и info.json).
2. Оркестратор → промпт → AI → сохранить JSON в slides_json/ (повторить для каждого слайда).
3. **Опционально:** рецензент → review.md → агенты правят JSON по замечаниям (можно пропустить и перейти к сборке pptx).
4. **visuals_pipeline** (или `--visuals` оркестратора): `generate_visuals.py` → проверка PNG → при необходимости `--review` → pptx. Перед правками урока — прочитать **`author_feedback.md`**, если есть.
5. **slide_code_agent** → --apply или --prompt → --save → `code_examples` в JSON (см. docs/slide_code_agent.md).
6. **pptx_builder** (или `visuals_pipeline` без флагов — generate + check + pptx) → `presentation.pptx`.
7. **Проверка и правка пользователем в PowerPoint** — не JSON. Ручные правки pptx не синхронизируются с JSON; повторный pptx_builder перезаписывает файл. Замечания — в **author_feedback.md** (файл **не удалять**; история багов для следующих перегенераций).
8. При содержательных правках после pptx: **author_feedback.md** и/или чат → агенты правят JSON и пересобирают pptx (указать, что сохранить из ручных правок, или сделать backup).
9. **notebook_generator** → промпт → AI → --save → `code.ipynb` (см. docs/notebook_agent.md).
10. **notebook_reviewer** → автопроверка + AI-рецензия → `notebook_review.md`; при необходимости --apply → правки `code.ipynb` / `project.ipynb`.
11. **project.ipynb** — мини-проект end-to-end по docs/project_notebook.md (вручную или отдельным промптом).
12. **references_agent** → --prompt → AI → --save → --apply (статьи + Colab + QR; см. docs/colab_references.md).
13. **link_checker_agent** → проверить URL (--all или по уроку); при необходимости --fix (Colab) или --llm → AI для paper URL → снова проверить presentation.pptx.

Структурные изменения (новый слайд, порядок) — через plan.md и оркестратор, не только правкой pptx.

## Формат взаимодействия

- AI действует самостоятельно при однозначных задачах; при неясности — уточняет.
- После задачи — краткий отчёт.

## Зависимости

- Список пакетов: `requirements.txt` в корне проекта.
- Установка: `pip install -r requirements.txt`

## Что должно быть на слайде
- Заголовок как в plan.md (но без Слайд X), в редких случаях его можно отредактировать
- Тезисно материал по теме, взятый как из plan.md, так и подготовленный AI RULES.md
- **Буллеты** — массив `bullets[]` в JSON; маркер в pptx добавляет `pptx_builder` (см. «Значки буллетов»)
- Формулы — inline в тексте через `$...$`; API и имена функций — через `` `...` `` (см. docs/formulas.md)
- **Иллюстрации** — по политике docs/visuals.md: по умолчанию ≥1 график/схема на слайд; 2–4 где несколько наглядных идей; при **>3** графиках или перегруженных картинках — вынести на отдельный слайд сразу после текущего; `visuals[]` с `description`, `output`, опционально `size: "large"`; шрифт на диаграмме ≥18 pt эквивалент на слайде (`agents/viz_style.py`)
- При необходимости - ссылка и QR-код на внешний ресурс (поле `link`; см. docs/references_slide.md для слайда литературы + Colab)
- Опционально — поле `notebook` для практики в code.ipynb (см. docs/notebook_agent.md):
  ```json
  "notebook": { "include": true, "kinds": ["example", "experiment"], "hint": "..." }
  ```
- Опционально — поле `code_examples` для кода на слайде (см. docs/slide_code_agent.md):
  ```json
  "code_examples": [{ "source": "import pandas as pd\n...", "caption": "..." }]
  ```

## Значки буллетов

- **В JSON** (`slides_json/*.json`, поле `bullets[]`) — только текст тезиса, **без** маркера в начале строки (не писать `•`, `-`, `*`).
- **При сборке pptx** (`agents/pptx_builder.py`) к каждому буллету автоматически добавляется символ **`•`** (U+2022) через `_format_bullet_text()`.
- **Где применяется:** обычные слайды (20 pt), слайд `type=references` — литература, Colab и доп. тезисы (15–16 pt).
- **Пересборка** после правок JSON или изменения стиля маркера:
  ```bash
  python agents/pptx_builder.py lessons/<имя_урока>
  ```
- Если в JSON случайно остался маркер — сборщик снимает его, чтобы не было двойного `•`.
- Ручные правки маркеров в PowerPoint **не** синхронизируются с JSON; повторный `pptx_builder` перезапишет pptx.

## Отсылки к слайдам

- **Не делай перекрёстных ссылок** между слайдами («см. слайд …», «обсудим в …»). Каждый слайд самодостаточен; повтори мысль кратко или отложи без указания номера/заголовка.
- **Не использовать** номера файлов (05.json), порядковые номера («слайд 21») и метки из plan.md («Слайд 5»).
- Номера в именах файлов (`01.json`) — только для пайплайна, не для авторского текста.