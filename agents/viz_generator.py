"""
Генератор визуализаций.

Формирует промпт для генерации Python-скрипта диаграммы.

Использование:
    python agents/viz_generator.py <lesson_dir> <описание>
"""

import sys
from pathlib import Path

PROMPT_PATH = Path(__file__).parent / "prompts" / "viz_generator.md"


def main():
    if len(sys.argv) < 3:
        print("Использование: python agents/viz_generator.py <lesson_dir> <описание>")
        sys.exit(1)

    lesson_dir = Path(sys.argv[1])
    description = " ".join(sys.argv[2:])

    if not lesson_dir.exists():
        print(f"Папка не найдена: {lesson_dir}")
        sys.exit(1)

    assets_dir = lesson_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    system_prompt = open(PROMPT_PATH, "r", encoding="utf-8").read()
    user_prompt = f"""Описание визуализации:
{description}

Путь для сохранения: {assets_dir}/

Сгенерируй Python-скрипт.
"""

    print(f"{system_prompt}\n\n{user_prompt}")


if __name__ == "__main__":
    main()
