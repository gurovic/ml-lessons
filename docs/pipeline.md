# Пайплайн урока: от plan.md до presentation.pptx

## Проблема

Раньше автор проверял и правил каждый файл в `slides_json/` вручную. JSON удобен агентам и сборщику, но неудобен человеку: формулы, вёрстка и иллюстрации лучше оцениваются в готовой презентации PowerPoint.

## Решение

**Для человека (автор, рецензия):** главный артефакт — `presentation.pptx`.  
**Для машин (агенты, пересборка):** источник истины — `slides_json/` + `assets/`.

Направление синхронизации **одностороннее:** JSON → pptx. Правки в PowerPoint **не** попадают обратно в JSON автоматически.

## Порядок работы

1. **Пользователь** пишет `plan.md` (и при необходимости `info.json`).
2. **Агенты** генерируют контент:
   - `slides_orchestrator` → `slides_json/` (по одному слайду из plan.md);
   - опционально `lesson_reviewer` → `review.md` → правки через агентов в JSON (см. ниже);
   - **`visuals_pipeline`** (или `--visuals` оркестратора) → PNG в `assets/`; программная проверка; опционально AI-рецензия (`--review`);
   - `slide_code_agent` → `code_examples` в JSON;
   - `pptx_builder` → **`presentation.pptx`**;
   - `notebook_generator` → `code.ipynb`;
   - `project.ipynb` (вручную или по шаблону);
   - `references_agent` → слайд «Источники и практика» + пересборка pptx;
   - `link_checker_agent` → проверка URL (после references, до финальной QA pptx).
3. **Пользователь проверяет и правит `presentation.pptx` в PowerPoint** — не JSON. Замечания по слайдам — в **`author_feedback.md`** (чеклисты; файл не перезаписывается рецензентом).
4. Если после проверки pptx нужны **содержательные** изменения:
   - зафиксировать в **`author_feedback.md`**, описать в чате с ассистентом **или** обновить `plan.md`;
   - агенты правят `slides_json/` и пересобирают pptx;
   - **внимание:** повторный `pptx_builder` **перезаписывает** `presentation.pptx` — ручные правки в PowerPoint будут потеряны, если не указать, что сохранить (или не сделать резервную копию).
5. Слайд литературы, `code_examples`, Colab/QR — добавляются агентами; результат виден в pptx.

## Роль JSON, review.md и author_feedback.md

| Артефакт | Кто редактирует | Назначение |
|----------|-----------------|------------|
| `slides_json/*.json` | **только агенты** | машинный формат для генерации и пересборки |
| `presentation.pptx` | **автор** | основная проверка и финальная правка текста, формул, вёрстки |
| `review.md` | агент-рецензент | опциональный QA **до** сборки pptx; перезаписывается при повторной рецензии; правки в JSON — агентами |
| `author_feedback.md` | **автор** | замечания **после** проверки pptx (чеклисты по слайдам); persistent, не трогается lesson_reviewer |

Рецензент (`lesson_reviewer`) полезен **до** первой сборки pptx: отчёт помогает поймать ошибки до визуализаций. Автор может **пропустить** JSON-рецензию и сразу собрать pptx, если доверяет черновику — тогда основная QA — просмотр презентации.

## Важные ограничения

### Ручные правки pptx не синхронизируются с JSON

Изменения текста, формул или картинок только в PowerPoint останутся только в `.pptx`. Следующий запуск `pptx_builder.py`, `references_agent --apply` или оркестратора с пересборкой **затирает** файл.

**Рекомендации:**
- завершите правки в pptx **до** повторной пересборки;
- перед regen сохраните копию: `presentation_backup.pptx`;
- если правка должна сохраниться в пайплайне — опишите её для агентов (обновление JSON/plan.md), а не только в pptx.

### Структурные изменения — через plan.md, не только pptx

Новый слайд, удаление, **перестановка порядка** — через `plan.md` и оркестратор (или правки JSON агентами по запросу). Ручная перестановка слайдов в PowerPoint не отразится в `slides_json/` и пропадёт при пересборке.

### Мелкие правки можно оставить только в pptx

Если урок «заморожен» и пересборка не планируется, финальный `.pptx` может жить отдельно от JSON. Для курса с регенерацией и ноутбуками лучше дублировать важные правки в plan/чат для агентов.

## Схема потока

```
plan.md (автор)
    ↓
slides_json/ + assets/ (агенты)
    ↓
presentation.pptx (pptx_builder)
    ↓
правки в PowerPoint (автор)  ←  основная human QA
    ↓
[опционально] plan.md / чат → агенты → JSON → pptx (перезапись!)
    ↓
code.ipynb, project.ipynb, references, link_checker (агенты)
```

## Связанные документы

- **docs/issue_workflow.md** — когда создавать issue, ветка `issue-N/…`, PR с `Closes #N`; issue vs `plan.md`
- **RULES.md** — краткий порядок шагов и состав папки урока
- **docs/reviewer_agent.md** — рецензент до pptx (опционально)
- **docs/notebook_agent.md**, **docs/slide_code_agent.md**, **docs/colab_references.md**, **docs/link_checker_agent.md** — шаги после/вокруг pptx
- **docs/formulas.md**, **docs/visuals.md** — как JSON рендерится в pptx
- **agents/visuals_pipeline.py**, **agents/prompts/visuals_reviewer.md** — генерация PNG, автопроверка, AI-рецензия иллюстраций

### Иллюстрации (visuals_pipeline)

Если в уроке есть `assets/generate_visuals.py`:

```bash
python agents/visuals_pipeline.py lessons/<slug>              # generate + check + pptx
python agents/visuals_pipeline.py lessons/<slug> --check-only
python agents/visuals_pipeline.py lessons/<slug> --review     # промпт для AI-рецензии PNG
```

Шаги: (1) запуск `generate_visuals.py`; (2) проверка — missing/orphan PNG, aspect для правой колонки, слайды без visuals; (3) пересборка pptx. Рецензия **PNG** (педагогика, контраст, подписи) — отдельно от `lesson_reviewer` (текст JSON).

## Отвергнутые альтернативы

| Альтернатива | Почему нет |
|--------------|------------|
| Ручное редактирование JSON автором | неудобно; pptx — естественный формат для лекции |
| Автосинхронизация pptx → JSON | сложно, хрупко; вне scope |
| Только pptx без JSON | агентам и ноутбукам нужен структурированный источник |
