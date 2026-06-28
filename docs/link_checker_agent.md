# Агент проверки ссылок

## Проблема

На слайде «Источники и практика» и в полях `link` обычных слайдов накапливаются URL на статьи и Colab. Часть ссылок устаревает (404), ведёт на paywall или содержит неверный branch в Colab URL после смены ветки в `project_config.json`.

## Решение

Агент **link_checker_agent** автоматически проверяет URL в:

- `lessons/<name>/references.json`
- references-слайдах в `slides_json/` (`type: "references"`)
- полях `link` на любых слайдах

Режим `--llm` формирует промпт для AI (см. `agents/prompts/link_checker_agent.md`) — подбор бесплатных full-text альтернатив для проблемных paper-URL.

## Что проверяется

| Тип | Проверки |
|-----|----------|
| **paper** | HTTP-доступность; эвристика paywall (doi.org, JSTOR, Springer landing без PDF) |
| **colab** | Формат URL; owner/repo/branch из `project_config.json`; локальное наличие ноутбука; опционально raw GitHub |
| **slide link** | HTTP-доступность |
| **нет URL** | WARN |

Флаг `--offline` отключает HTTP — только формат Colab, локальные файлы и paywall-эвристики по URL.

## Использование

```bash
# один урок
python agents/link_checker_agent.py lessons/lineynaya_regressiya

# все уроки
python agents/link_checker_agent.py --all
python agents/apply_all_link_checks.py

# исправить Colab URL (branch/owner/repo/path из project_config)
python agents/link_checker_agent.py lessons/pandas --fix

# без сети
python agents/link_checker_agent.py --all --offline

# промпт для AI (альтернативные paper URL)
python agents/link_checker_agent.py lessons/pandas --llm
```

## Коды выхода

| Код | Значение |
|-----|----------|
| `0` | Нет FAIL (допустимы WARN) |
| `1` | Есть хотя бы одна ссылка с FAIL |

## Режим `--fix`

Автоисправление **только** для Colab URL: подставляет owner, repo, branch и путь к ноутбуку из `project_config.json` / git. Paper URL не меняются без AI (`--llm` → ручной `--save` через references_agent).

## Место в пайплайне

После `references_agent --apply`, **до** финальной проверки `presentation.pptx` (см. **RULES.md**, **docs/pipeline.md**).

## Связанные документы

- **docs/references_slide.md** — формат references-слайда
- **docs/colab_references.md** — генерация Colab URL
- **agents/references_agent.py** — обновление references-слайда

## Отвергнутые альтернативы

| Альтернатива | Почему нет |
|--------------|------------|
| Обязательный `requests` | достаточно stdlib `urllib` |
| Авто-замена paper URL без LLM | риск неверной работы; только Colab `--fix` |
| Проверка только references.json | дубли в slides_json и поля `link` тоже попадают в pptx |
