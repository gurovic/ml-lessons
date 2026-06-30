# Замечания автора после просмотра presentation.pptx

**Нумерация слайдов — как в PowerPoint** (слайд 1 = титул, слайд 2 = первый содержательный и т.д.).  
Соответствие: **pptx N** → `slides_json/{N-1:02d}.json` (например, pptx 5 → `04.json`).

Файл — постоянный архив. Выполненные пункты помечайте `[x]`.

---

## pptx 2 — Философия визуализации (`01.json`)

- [x] Удалить рисунок.

## pptx 3 — Выбор библиотеки (`02.json`)

- [x] Удалить рисунок (только текст).

## pptx 4 — pandas built-in (`03.json`)

- [x] Убрать код на слайде.
- [x] Удалить рисунок (ранее мелкий текст на картинке — не нужен).

## pptx 5 — Matplotlib Figure/Axes (`04.json`)

- [x] Убрать код из буллетов; код — заголовки над отдельными картинками.
- [x] Убрать `code_examples` под текстом.
- [x] Удалить последний рисунок (`mpl_code_tight_layout.png`).

## pptx 19 — Decision Boundaries (`18.json`)

- [x] Исправить перенос строки внутри `model` → `clf` в API-буллете.

## pptx 31 — Стили и темы (`30.json`)

- [x] Удалить рисунки.

## pptx 32 — Overlay и комбинирование (`31.json`)

- [x] Добавить 4 рисунка по техникам из буллетов (hist, lines, FacetGrid, subplots).

## pptx 33 — Размер и DPI (`32.json`)

- [x] Удалить рисунки.

## pptx 6 — Subplot (`05.json`)

- [x] Перерисовать иллюстрацию (train vs test, понятнее).
- [x] Убрать код на слайде.

## pptx 7 — Кастомизация (`06.json`)

- [x] Убрать код; текст понятнее.

## pptx 8 — Сохранение и экспорт (`07.json`)

- [x] Убрать код на слайде.
- [x] Удалить рисунок (схема форматов).

## pptx 9 — Plotly Express (`08.json`)

- [x] Убрать код на слайде.
- [x] Удалить последний буллет (Line / write_html).
- [x] Без картинки.

## pptx 10 — Plotly advanced (`09.json`)

- (без новых замечаний; буллет Dash/Streamlit оставлен)

---

## Все слайды

- [x] Удалить нижний блок `code_examples` (pptx 11–33, файлы `10.json`–`32.json`).
- [x] Упростить программу: удалено **41** продвинутый буллет (~24% от 173): 3D/animation Plotly, hexbin/webgl, MNAR/dendrogram missingno, ECDF, XOR, t-SNE/UMAP, silhouette, Q-Q, grid search, permutation importance, twinx/FacetGrid/subplots, DPI 600 и др. Скрипт: `agents/trim_advanced_bullets.py`.
