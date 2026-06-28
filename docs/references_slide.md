# Формат слайда «Источники и практика» (`type: "references"`)

## Назначение

Один слайд в конце урока: классические научные работы + ссылки на практические ноутбуки в Colab с QR-кодами.

## JSON-схема

```json
{
  "title": "Источники и практика",
  "type": "references",
  "references": [
    {
      "kind": "paper",
      "title": "Regression Shrinkage and Selection via the Lasso",
      "authors": "Tibshirani R.",
      "year": 1996,
      "url": "https://doi.org/10.1111/j.2517-6161.1996.tb00880.x"
    },
    {
      "kind": "colab",
      "title": "code.ipynb",
      "label": "Примеры по слайдам",
      "url": "https://colab.research.google.com/github/owner/repo/blob/main/lessons/.../code.ipynb"
    },
    {
      "kind": "colab",
      "title": "project.ipynb",
      "label": "Мини-проект",
      "url": "https://colab.research.google.com/github/owner/repo/blob/main/lessons/.../project.ipynb"
    }
  ],
  "bullets": [
    "Дополнительный тезис (опционально)"
  ],
  "notes": "Заметки докладчика (опционально)"
}
```

### Поля

| Поле | Обязательно | Описание |
|------|-------------|----------|
| `title` | да | Заголовок слайда (рекомендуется: «Источники и практика») |
| `type` | да | Всегда `"references"` |
| `references` | да | Массив записей `paper` и/или `colab` |
| `bullets` | нет | Дополнительные тезисы под списком литературы |
| `notes` | нет | Speaker notes |

### Запись `kind: "paper"`

| Поле | Обязательно | Описание |
|------|-------------|----------|
| `kind` | да | `"paper"` |
| `title` | да | Название работы |
| `authors` | да | Автор(ы), кратко |
| `year` | да | Год публикации (число) |
| `url` | нет | DOI, arXiv, PDF; если нет — текст без гиперссылки |

### Запись `kind: "colab"`

| Поле | Обязательно | Описание |
|------|-------------|----------|
| `kind` | да | `"colab"` |
| `title` | да | Имя файла (`code.ipynb`, `project.ipynb`) |
| `label` | нет | Подпись в презентации (по умолчанию — `title`) |
| `url` | да | Colab URL; агент заполняет автоматически из git |
| `manual` | нет | `true` — не перезаписывать URL при `--apply` |

## Рендеринг в presentation.pptx

`pptx_builder` для `type: "references"`:

1. **Заголовок** — как у обычного слайда.
2. **Левая колонка** (~7.5"):
   - Подзаголовок «Литература» (если есть `paper`).
   - Буллеты: `Authors (year). Title` — гиперссылка на `url`.
   - Подзаголовок «Практика в Colab» (если есть `colab`).
   - Строки: `label` + кликабельный URL.
   - Опциональные `bullets` из корня JSON.
3. **Правая колонка** — QR-код (1.2") на каждую Colab-ссылку, с подписью `label` под QR.
4. Поле `link` на этом типе слайда **не используется** (ссылки только в `references[]`).
5. Поле `visuals` на references-слайде не ожидается.

## Отличие от поля `link`

| | `link` на обычном слайде | `type: "references"` |
|--|--------------------------|----------------------|
| Назначение | одна внешняя ссылка (игра, демо) | литература + ноутбуки |
| QR | один, справа внизу | по одному на Colab |
| Генерация | агент / поле `link` в JSON | Colab — агент; статьи — AI + `--save` |

## Пример файла

`lessons/lineynaya_regressiya/slides_json/17.json` (после `--apply`).

## Ответ AI для `--save`

AI возвращает JSON **только со статьями** (без Colab — агент добавит сам):

```json
{
  "title": "Источники и практика",
  "type": "references",
  "references": [
    {
      "kind": "paper",
      "title": "Ridge Regression: Biased Estimation for Nonorthogonal Problems",
      "authors": "Hoerl A.E., Kennard R.W.",
      "year": 1970,
      "url": "https://doi.org/10.2307/1271436"
    }
  ],
  "bullets": []
}
```

Агент при сохранении **мержит** существующие `colab`-записи и пересчитывает их URL из git.
