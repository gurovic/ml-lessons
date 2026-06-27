"""
Сохраняет JSON слайда из stdin или из аргумента.

Использование:
    python agents/save_slide.py <lesson_dir> <slide_num>
    python agents/save_slide.py <lesson_dir> <slide_num> '<JSON>'

Если JSON не передан аргументом, читает из stdin (pipe).
"""

import sys
from pathlib import Path

from slide_utils import parse_json_response, save_slide


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

    try:
        slide_data = parse_json_response(raw)
    except Exception as e:
        print(f"Ошибка парсинга JSON: {e}")
        sys.exit(1)

    save_slide(lesson_dir / "slides_json", slide_data, slide_num)


if __name__ == "__main__":
    main()
