"""Удалить ~20% самых продвинутых буллетов из slides_json урока vizualizatsiya."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLIDES_DIR = ROOT / "lessons" / "vizualizatsiya" / "slides_json"

# Индексы 1-based — удаляем с конца, чтобы не сбивать нумерацию
REMOVE: dict[str, list[int]] = {
    "09.json": [6, 5, 3, 2],  # pptx 10: 3D, animation, webgl, Dash
    "10.json": [5],  # marginal violin plotly
    "11.json": [3],  # гетероскедастичность
    "13.json": [5, 3],  # hexbin, webgl 100k
    "14.json": [5, 4, 3],  # MNAR, dendrogram — оставляем matrix
    "16.json": [5, 3, 2],  # ECDF/KDE/plotly — оставляем идею drift
    "18.json": [4],  # XOR
    "19.json": [5, 4, 3],  # t-SNE, UMAP, plotly 3D
    "20.json": [4, 3],  # silhouette детали
    "21.json": [4],  # паттерны остатков (воронка)
    "24.json": [4],  # normalize recall
    "25.json": [5, 4],  # overlay моделей, plotly ROC
    "26.json": [4],  # fill_between CI
    "31.json": [6, 5, 4],  # twinx, FacetGrid, make_subplots
    "32.json": [6, 5, 3],  # golden ratio, SVG, DPI 600
}

CHECKLIST_REPLACEMENTS = {
    "34.json": [
        "**Распределение** → hist + KDE | **Выбросы** → box plot",
        "**Сравнение групп** → violin plot | **Связь признаков** → scatter",
        "**Пропуски** → матрица пропусков | **Корреляции** → heatmap",
        "**Дрейф train/test** → overlay гистограмм | **Дисбаланс** → count plot",
        "**Регрессия** → predicted vs actual, residuals, Q-Q | **Классификация** → confusion matrix, ROC",
        "**Grid search** → heatmap | **Переобучение** → learning curve | **Важность** → permutation importance",
        "Библиотеки: **seaborn** для EDA, **plotly** для интерактива, **matplotlib** для кастомизации, **pandas** для быстрых графиков",
    ],
}

VISUALS_UPDATE = {
    "31.json": [
        {
            "description": "Overlay гистограмм train и test с alpha=0.5.",
            "output": "overlay_hist_train_test.png",
            "size": "compact",
        },
        {
            "description": "Две линии train_scores и val_scores на одних осях.",
            "output": "overlay_lines_scores.png",
            "size": "compact",
        },
    ],
}


def trim_slide(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    name = path.name
    removed = 0

    if name in CHECKLIST_REPLACEMENTS:
        old_n = len(data.get("bullets", []))
        data["bullets"] = CHECKLIST_REPLACEMENTS[name]
        removed = old_n - len(data["bullets"])

    if name in REMOVE:
        bullets = data.get("bullets", [])
        for idx in REMOVE[name]:
            if 1 <= idx <= len(bullets):
                bullets.pop(idx - 1)
                removed += 1
        data["bullets"] = bullets

    if name in VISUALS_UPDATE:
        data["visuals"] = VISUALS_UPDATE[name]

    if removed or name in CHECKLIST_REPLACEMENTS or name in VISUALS_UPDATE:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return removed


def main() -> None:
    total = 0
    for path in sorted(SLIDES_DIR.glob("[0-9]*.json")):
        n = trim_slide(path)
        if n:
            print(f"  {path.name}: -{n} bullets")
            total += n
    print(f"Removed {total} bullets total")


if __name__ == "__main__":
    main()
