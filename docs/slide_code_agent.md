# Агент примеров кода на слайдах

## Проблема

На слайдах с практическим API (sklearn, pandas, matplotlib) аудитории полезен короткий фрагмент кода прямо на слайде — не только в `code.ipynb`. Добавлять вручную на ~50 слайдов долго; не на всех слайдах код уместен (теория, мотивация).

## Решение

Агент **slide_code_agent** читает `slides_json/`, отбирает слайды без `code_examples`, где уместен код, и либо подставляет **bootstrap-сниппеты**, либо формирует промпт для AI.

### Когда добавлять

**После** генерации JSON и визуализаций, **до** или **после** `pptx_builder` — поле `code_examples` рендерится сборщиком. Автор проверяет код на слайде в **presentation.pptx** (см. docs/pipeline.md).

Включить слайд, если **все** условия:

1. Нет поля `code_examples` (или пустой массив).
2. Не слайд `type: "references"`.
3. Выполняется **хотя бы одно**:
   - `"notebook": { "include": true }` в JSON;
   - в буллетах вызовы API: `sklearn`, `pandas`, `.fit(`, `DecisionTree`, `plt.`, `sns.`, `Pipeline`, `train_test_split` и т.п.

**Не добавлять:**

- чисто теоретические слайды без API;
- слайды, где код уже есть в `code_examples`;
- мотивационные блоки без практики.

## Формат данных

Опциональное поле в JSON слайда:

```json
{
  "title": "Дерево решений в sklearn",
  "bullets": ["..."],
  "code_examples": [
    {
      "source": "from sklearn.tree import DecisionTreeClassifier\nclf = DecisionTreeClassifier(max_depth=3)\nclf.fit(X, y)",
      "caption": "Минимальный пример обучения"
    }
  ]
}
```

| Поле | Тип | Описание |
|------|-----|----------|
| `code_examples` | `array` | 1–2 коротких блока на слайд |
| `source` | `string` | Python-код, **3–5 строк**; переносы `\n` |
| `caption` | `string?` | Подпись под блоком (опционально) |

- Комментарии в коде — **на русском**.
- Без markdown-обёртки ``` в `source`.
- Длина: **3–5 строк**; умещается в нижнюю часть слайда под буллетами.
- **Ширина строки:** не более **~60 символов** (Consolas 11 pt в узкой колонке с картинкой). Длинные вызовы переноси по скобкам/запятым; `normalize_code_example` и `pptx_builder` дополнительно обрезают переполнение.

### Стиль фрагментов

- **Импорты в блоке:** каждый `source` — самодостаточный фрагмент; сохраняй нужные `import`/`from` (sklearn, pandas, numpy), даже если они уже были на другом слайде урока.
- **Лаконичность:** однострочники sklearn/pandas где уместно; без лишнего boilerplate (`seed`, `plt.style`, `%matplotlib inline`).
- **Без `%matplotlib inline`** — только для ноутбука.

## Рендеринг в pptx

`agents/pptx_builder.py`:

- Шрифт: **Consolas** (fallback Courier New), ~**11 pt**.
- Расположение: **внизу слайда** (`CODE_BOTTOM_MARGIN` от нижнего края); буллеты и картинка — выше, без сдвига кода вверх.
- **Макс. длина строки:** ~**60 символов** при узкой колонке (`CODE_MAX_LINE_LEN` в `slide_code_utils.py`); для полной ширины — `max_code_line_length_for_width()`. Перенос в JSON/агенте и при сборке pptx.
- При наличии `visuals[]` — левая колонка уже сужена (~7.5″); высота блока кода уменьшается, буллеты сжимаются.
- Фон: серая рамка + **отдельный textbox на каждую строку** (без line break и лишнего межстрочного интервала); снизу ≈ одна пустая строка.
- **Подсветка синтаксиса:** Pygments, стиль `friendly` (`pip install pygments` — см. `requirements.txt`); без Pygments — монохромный fallback.
- `caption` — курсив 10 pt под блоком.

## CLI

```powershell
# Кандидаты без code_examples
python agents/slide_code_agent.py lessons/pandas --list

# Промпт для AI (урок целиком)
python agents/slide_code_agent.py lessons/pandas --prompt

# Применить JSON-ответ AI к slides_json/
python agents/slide_code_agent.py lessons/pandas --save response.json

# Bootstrap-сниппеты для всех notebook.include слайдов
python agents/slide_code_agent.py lessons/pandas --apply
```

`--apply` для всех уроков:

```powershell
python agents/slide_code_agent.py lessons/lineynaya_regressiya --apply
python agents/slide_code_agent.py lessons/logisticheskaya_regressiya --apply
python agents/slide_code_agent.py lessons/derevo_resheniy --apply
python agents/slide_code_agent.py lessons/pandas --apply
python agents/slide_code_agent.py lessons/vizualizatsiya --apply
```

После `--apply` или `--save` пересобрать презентацию:

```powershell
python agents/pptx_builder.py lessons/<урок>
```

## Формат ответа AI

Только JSON:

```json
{
  "slides": [
    {
      "slide_index": 12,
      "title": "Дерево решений в sklearn",
      "code_examples": [
        {
          "source": "from sklearn.tree import DecisionTreeClassifier\n...",
          "caption": "Обучение на iris"
        }
      ]
    }
  ]
}
```

- `slide_index` — номер файла `NN.json` (1-based, как в пайплайне).
- `title` — для проверки соответствия (должен совпадать с JSON слайда).
- Генерировать **только** для слайдов из списка кандидатов в user prompt.

## Bootstrap

`agents/slide_code_bootstrap.py` — курируемые сниппеты по ключу `(lesson_dir.name, slide.title)` для всех слайдов с `notebook.include: true` (~49) и практических слайдов `derevo_resheniy`.

`--apply` подставляет bootstrap без вызова AI.

## Порядок в пайплайне (RULES.md)

После финализации слайдов (шаг 4–6), **перед** `notebook_generator`:

1. `slide_code_agent --apply` (bootstrap) или `--prompt` → `--save` (AI).
2. `pptx_builder` — код на слайдах.
3. `notebook_generator` → `code.ipynb`.

## Отвергнутые альтернативы

| Альтернатива | Почему нет |
|--------------|------------|
| Код только в notes | не виден на проекторе |
| Один общий слайд «весь код урока» | теряется связь с темой слайда |
| Автоген без bootstrap | нужен быстрый старт без AI для всех уроков |
