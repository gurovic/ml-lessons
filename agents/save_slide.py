"""
Сохраняет JSON слайда из stdin или из аргумента.

Использование:
    python agents/save_slide.py <lesson_dir> <slide_num>
    python agents/save_slide.py <lesson_dir> <slide_num> '<JSON>'

Если JSON не передан аргументом, читает из stdin (pipe).
"""

import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        print("Использование: python agents/save_slide.py <lesson_dir> <slide_num> ['<JSON>']")
        sys.exit(1)

    lesson_dir = Path(sys.argv[1])
    slide_num = int(sys.argv[2])

    if len(sys.argv) >= 4:
        raw = sys.argv[3]
    else:
        raw = sys.stdin.read().strip()

    # Парсим JSON, ищем блок ```json ... ```
    if "```json" in raw:
        start = raw.index("```json") + 7
        end = raw.index("```", start)
        raw = raw[start:end].strip()
    elif "```" in raw:
        start = raw.index("```") + 3
        end = raw.index("```", start)
        raw = raw[start:end].strip()

    try:
        slide_data = json.loads(raw)
    except Exception as e:
        print(f"Ошибка парсинга JSON: {e}")
        sys.exit(1)

    slides_dir = lesson_dir / "slides_json"
    slides_dir.mkdir(parents=True, exist_ok=True)

    path = slides_dir / f"{slide_num:02d}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(slide_data, f, ensure_ascii=False, indent=2)

    print(f"Слайд {slide_num} сохранён: {path}")


if __name__ == "__main__":
    main()
