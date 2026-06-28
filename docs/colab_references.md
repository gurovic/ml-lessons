# Colab-ссылки и слайд «Источники и практика»

## Проблема

После сборки презентации и ноутбуков (`code.ipynb`, `project.ipynb`) слушателям нужны:

1. **Публичные ссылки на Colab** — открыть ноутбук в браузере без установки Jupyter.
2. **QR-коды** на слайде с литературой — быстро открыть практику с телефона.
3. **Классические научные статьи** по алгоритмам урока — на том же слайде, что и Colab.

Раньше в `pptx_builder` была только одиночная ссылка `link` + QR на произвольном слайде. Нужен отдельный тип слайда `references` и агент, который собирает литературу и Colab-URL автоматически.

## Решение

Агент **references_agent** формирует JSON слайда `type: "references"`, вставляет его в `slides_json/`, пересобирает `presentation.pptx`. Colab-URL строятся **без загрузки** через шаблон GitHub → Colab (репозиторий должен быть публичным).

Подробный формат слайда — **docs/references_slide.md**.

## Colab URL: стратегии

### По умолчанию: GitHub → Colab (без API-ключей)

Если репозиторий **публичный** на GitHub, Colab открывает ноутбук напрямую:

```
https://colab.research.google.com/github/{owner}/{repo}/blob/{branch}/{path}
```

Пример:

```
https://colab.research.google.com/github/gurovic/ml-lessons/blob/main/lessons/lineynaya_regressiya/code.ipynb
```

**Откуда берутся параметры:**

| Параметр | Источник |
|----------|----------|
| `owner`, `repo` | `git remote get-url origin` (парсинг HTTPS/SSH) |
| `branch` | `git rev-parse --abbrev-ref HEAD` |
| `path` | путь к `.ipynb` относительно корня репозитория |

Переопределение (опционально) в `project_config.json`:

```json
{
  "github": {
    "owner": "gurovic",
    "repo": "ml-lessons",
    "branch": "main"
  }
}
```

### Ручная загрузка в Google Drive

Если репозиторий **приватный**, GitHub-URL в Colab не сработает. Варианты:

1. **Вручную:** загрузить `.ipynb` в Google Drive → «Открыть в Colab» → «Поделиться» → скопировать URL.
2. **В JSON слайда** указать готовый URL в записи `kind: "colab"` (агент не перезапишет явный `url`, если задан флаг или поле `manual: true`).

Автоматическая загрузка через Google Drive API (`pydrive`, `google-api-python-client`) **не входит** в пайплайн: требует OAuth/credentials и усложняет CI. При необходимости — отдельный скрипт вне агентов.

### Отвергнутые альтернативы

| Альтернатива | Почему нет |
|--------------|------------|
| Только ручные URL | не масштабируется на 10+ уроков |
| Обязательный Drive API | ключи, квоты, хрупкий CI |
| Отдельный слайд только для Colab | дублирование; пользователь просил один слайд с литературой |

## Агент references_agent

**Файлы:** `agents/references_agent.py`, `agents/references_utils.py`, `agents/prompts/references_agent.md`.

### Что делает

1. Читает `info.json`, `plan.md`, список ноутбуков в папке урока.
2. Строит Colab-ссылки для `code.ipynb` и `project.ipynb` (если файлы есть).
3. Формирует промпт для AI: 3–6 классических статей по теме урока.
4. Сохраняет JSON слайда, вставляет/обновляет в `slides_json/`, запускает `pptx_builder`.

### CLI

```powershell
# Что будет на слайде (статьи + Colab)
python agents/references_agent.py lessons/lineynaya_regressiya --list

# Промпт для AI (список статей)
python agents/references_agent.py lessons/lineynaya_regressiya --prompt

# Сохранить слайд из ответа AI (файл или stdin)
python agents/references_agent.py lessons/lineynaya_regressiya --save references.json

# Вставить/обновить слайд и пересобрать presentation.pptx
python agents/references_agent.py lessons/lineynaya_regressiya --apply
```

`--apply` без предварительного `--save`: обновляет Colab-ссылки в существующем слайде `references` или создаёт слайд только с Colab (статьи добавить через `--save` после промпта).

## QR-коды

Генерация в `agents/references_utils.py` (`generate_qr_png`), библиотека `qrcode[pil]` (уже в `requirements.txt`). `pptx_builder` вставляет по одному QR на каждую Colab-ссылку справа на слайде `references`; для обычного поля `link` — поведение без изменений.

## Порядок в пайплайне

После сборки и **проверки** `presentation.pptx` (см. **docs/pipeline.md**), затем **notebook_generator** / **project.ipynb** (когда `.ipynb` существуют):

1. `references_agent --prompt` → AI → `--save`
2. `references_agent --apply` (или `--apply` сразу, если статьи уже в JSON)
3. Снова проверить **`presentation.pptx`** (основная human QA; JSON править не обязательно)

См. обновлённый раздел в **RULES.md**.

## Настройка пользователем

1. **Публичный GitHub-репозиторий** с закоммиченными `.ipynb`.
2. Запушить ветку, с которой работаете (Colab открывает файл с этой ветки).
3. При нестандартном remote — задать `github` в `project_config.json`.
4. Для приватного репо — попросить агента подставить Colab-URL в JSON или сделать репо публичным (автор не правит JSON вручную).

## Миграция

- Существующие слайды с полем `link` **не меняются**.
- Новый тип `references` — опциональный финальный (или предпоследний) слайд.
- Нумерация файлов `NN.json` — как у остальных слайдов; агент ищет слайд по `type: "references"`, а не по номеру.
