# Правила работы для AI-ассистента (Agents mode)

## Основные принципы

1. **Самостоятельность** — выполняй задачу без лишних уточнений, если запрос однозначен.
2. **Минимализм** — делай только то, что запрошено.
3. **Уточнение** — спрашивай разрешение только если запрос неоднозначен или затрагивает необратимые действия.
4. **Минимальный рабочий вариант**.
5. **Следование запросу** — уточни, если неоднозначно.
6. **RULES.md** — единственный источник правил.
7. **Issue-first** — для задач от ~30 мин (агенты, пайплайн, урок, пересборка pptx): сначала GitHub issue по шаблону (см. **docs/issue_workflow.md**), затем ветка `issue-<N>/<short-name>`, в PR — `Closes #N`. Мелкие правки — без issue.
8. **Работа с ветками** — каждая задача в новой ветке, затем PR в main.
9. **Сначала документ, потом код** — архитектурные решения, изменения пайплайна и новые правила сначала фиксируются в `.md`-файлах; реализация — только после этого (см. раздел ниже).

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

## Состав папки урока

- plan.md — создаётся пользователем
- **presentation.pptx** — **основной артефакт для автора**: проверка и правка слайдов в PowerPoint (см. docs/pipeline.md)
- assets/
- slides_json/ — JSON-слайды (01.json, 02.json, …); **редактируют агенты**, не автор вручную; источник для пересборки pptx
- review.md — опциональный отчёт агента-рецензента (до сборки pptx)
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
- Формулы в `$...$` в тексте рендерятся как native Equation (см. docs/formulas.md, agents/rich_text.py).
- До 4 иллюстраций на слайд — сетка/столбик в правой колонке (см. docs/visuals.md).
- Использование: python agents/pptx_builder.py <lesson_dir>

### Генератор визуализаций (agents/viz_generator.py)
- Промпт: agents/prompts/viz_generator.md
- Формирует промпт для генерации Python-скрипта диаграммы.

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
- Сквозной сценарий на реальных данных — docs/project_notebook.md
- Шаблоны: python agents/build_project_notebooks.py

## Порядок работы над уроком

Подробно: **docs/pipeline.md**. Кратко:

1. Создать plan.md (и info.json).
2. Оркестратор → промпт → AI → сохранить JSON в slides_json/ (повторить для каждого слайда).
3. **Опционально:** рецензент → review.md → агенты правят JSON по замечаниям (можно пропустить и перейти к сборке pptx).
4. --visuals → промпты → AI → --save-script (генерация диаграмм в assets/).
5. **slide_code_agent** → --apply или --prompt → --save → `code_examples` в JSON (см. docs/slide_code_agent.md).
6. **pptx_builder** → `presentation.pptx`.
7. **Проверка и правка пользователем в PowerPoint** — не JSON. Ручные правки pptx не синхронизируются с JSON; повторный pptx_builder перезаписывает файл.
8. При содержательных правках после pptx: описать в чате или обновить plan.md → агенты правят JSON и пересобирают pptx (указать, что сохранить из ручных правок, или сделать backup).
9. **notebook_generator** → промпт → AI → --save → `code.ipynb` (см. docs/notebook_agent.md).
10. **project.ipynb** — мини-проект end-to-end по docs/project_notebook.md (вручную или отдельным промптом).
11. **references_agent** → --prompt → AI → --save → --apply (статьи + Colab + QR; см. docs/colab_references.md).
12. **link_checker_agent** → проверить URL (--all или по уроку); при необходимости --fix (Colab) или --llm → AI для paper URL → снова проверить presentation.pptx.

Структурные изменения (новый слайд, порядок) — через plan.md и оркестратор, не только правкой pptx.

## Формат взаимодействия

- AI действует самостоятельно при однозначных задачах; при неясности — уточняет.
- После задачи — краткий отчёт.

## Зависимости

- Список пакетов: `requirements.txt` в корне проекта.
- Установка: `pip install -r requirements.txt`

## Запуск команд без ожидания Accept

- Все вызовы `run_terminal_command` должны использовать флаг `waitForCompletion: false`.
- Исключение: только если нужно дождаться результата команды перед следующим шагом (например, установка пакета).
- AI сам контролирует последовательность: запустил команду в фоне → через паузу проверил результат.

## Что должно быть на слайде
- Заголовок как в plan.md (но без Слайд X), в редких случаях его можно отредактировать
- Тезисно материал по теме, взятый как из plan.md, так и подготовленный AI RULES.md
- Формулы — inline в тексте через `$...$` (см. docs/formulas.md)
- **Иллюстрации** — по политике docs/visuals.md: по умолчанию ≥1 график/схема на слайд; 2–4 где несколько наглядных идей; `visuals[]` с `description`, `output`, опционально `size: "large"`; шрифт на диаграмме ≥18 pt эквивалент на слайде (`agents/viz_style.py`)
- При необходимости - ссылка и QR-код на внешний ресурс (поле `link`; см. docs/references_slide.md для слайда литературы + Colab)
- Опционально — поле `notebook` для практики в code.ipynb (см. docs/notebook_agent.md):
  ```json
  "notebook": { "include": true, "kinds": ["example", "experiment"], "hint": "..." }
  ```
- Опционально — поле `code_examples` для кода на слайде (см. docs/slide_code_agent.md):
  ```json
  "code_examples": [{ "source": "import pandas as pd\n...", "caption": "..." }]
  ```

## Отсылки к слайдам

- **Не делай перекрёстных ссылок** между слайдами («см. слайд …», «обсудим в …»). Каждый слайд самодостаточен; повтори мысль кратко или отложи без указания номера/заголовка.
- **Не использовать** номера файлов (05.json), порядковые номера («слайд 21») и метки из plan.md («Слайд 5»).
- Номера в именах файлов (`01.json`) — только для пайплайна, не для авторского текста.