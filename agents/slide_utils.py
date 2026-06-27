"""Общие утилиты для работы с JSON-слайдами (последовательная нумерация 01, 02, …)."""

import json
from pathlib import Path


def list_slide_files(slides_dir: Path) -> list[Path]:
    if not slides_dir.exists():
        return []
    files = [p for p in slides_dir.glob("*.json") if p.stem.isdigit()]
    non_numeric = [p.name for p in slides_dir.glob("*.json") if not p.stem.isdigit()]
    if non_numeric:
        print(f"  [warn] Файлы с нечисловыми именами (переименуйте): {', '.join(non_numeric)}")
    return sorted(files, key=lambda p: int(p.stem))


def read_slides(slides_dir: Path) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in list_slide_files(slides_dir)
    ]


def next_slide_number(slides_dir: Path) -> int:
    return len(list_slide_files(slides_dir)) + 1


def slide_path(slides_dir: Path, slide_num: int) -> Path:
    return slides_dir / f"{slide_num:02d}.json"


def parse_json_response(response: str) -> dict:
    if "```json" in response:
        start = response.index("```json") + 7
        end = response.index("```", start)
        response = response[start:end].strip()
    elif "```" in response:
        start = response.index("```") + 3
        end = response.index("```", start)
        response = response[start:end].strip()
    return json.loads(response)


def save_slide(slides_dir: Path, slide_data: dict, slide_num: int) -> Path:
    slides_dir.mkdir(parents=True, exist_ok=True)
    path = slide_path(slides_dir, slide_num)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(slide_data, f, ensure_ascii=False, indent=2)
    print(f"Слайд {slide_num} сохранён: {path}")
    return path
