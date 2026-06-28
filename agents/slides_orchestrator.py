"""
Оркестратор генерации слайдов.

Проходит по плану урока, для каждого пункта формирует промпт,
после получения JSON от AI сохраняет его в slides_json/,
затем генерирует визуализации (если указаны в поле visuals).

Файлы слайдов — последовательные числа: 01.json, 02.json, …
(независимо от нумерации в plan.md).

Использование:
    python agents/slides_orchestrator.py <lesson_dir>
    python agents/slides_orchestrator.py <lesson_dir> --save '<JSON>'
    python agents/slides_orchestrator.py <lesson_dir> --visuals
    python agents/slides_orchestrator.py <lesson_dir> --save-script <file> '<code>'
"""

import json
import re
import subprocess
import sys
from pathlib import Path

from slide_utils import (
    next_slide_number,
    parse_json_response,
    read_slides,
    save_slide,
)

PROMPT_PATH = Path(__file__).parent / "prompts" / "slide_generator.md"
VIZ_PROMPT_PATH = Path(__file__).parent / "prompts" / "viz_generator.md"


def read_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_plan_slides(plan: str) -> list[str]:
    """Разбивает plan.md на блоки слайдов (порядок = порядок в файле)."""
    lines = plan.split("\n")
    plan_lines = []
    current = []
    for line in lines:
        stripped = line.strip()
        if re.match(r"\*{0,2}\s*Слайд\s+\d+", stripped):
            if current:
                plan_lines.append("\n".join(current))
            current = [stripped]
        elif current:
            current.append(stripped)
    if current:
        plan_lines.append("\n".join(current))
    return plan_lines


def build_prompt(plan: str, slide_topic: str, previous_slides: list[dict]) -> str:
    system_prompt = read_file(PROMPT_PATH)
    prev_text = "\n---\n".join(
        [f"{s.get('title', '')}: {', '.join(s.get('bullets', []))}" for s in previous_slides]
    ) if previous_slides else "(слайдов пока нет)"
    user_prompt = f"""План лекции:
{plan}

Предыдущие слайды:
{prev_text}

Тема текущего слайда: {slide_topic}

Сгенерируй следующий слайд."""
    return f"{system_prompt}\n\n{user_prompt}"


def generate_visualizations(lesson_dir: Path, slides_dir: Path) -> bool:
    existing_slides = read_slides(slides_dir)
    assets_dir = lesson_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    system_prompt = read_file(VIZ_PROMPT_PATH)
    any_pending = False

    for slide_data in existing_slides:
        visuals = slide_data.get("visuals", [])
        for viz in visuals:
            output = viz.get("output", "")
            if not output or (assets_dir / output).exists():
                continue
            any_pending = True
            description = viz.get("description", "Без описания")
            print(f"\n=== ВИЗУАЛИЗАЦИЯ: {output} ===")
            print(f"Описание: {description}")
            print(f"Слайд: {slide_data.get('title', '?')}")
            user_prompt = f"""Описание визуализации:
{description}

Путь для сохранения: {assets_dir}/
Название файла: {output}

Сгенерируй Python-скрипт, который создаст эту визуализацию.
Если нужны случайные данные — используй numpy.random.seed(42).

В ответе верни JSON:
{{
  "script": "Python-код целиком",
  "libraries": ["matplotlib", "graphviz"]
}}"""
            print(f"{system_prompt}\n\n{user_prompt}")
            print("\n=== КОНЕЦ ПРОМПТА ===")

    if not any_pending:
        print("Все визуализации уже созданы.")
    return any_pending


def save_and_run_script(lesson_dir: Path, output_file: str, script_content: str):
    script_path = lesson_dir / "assets" / (output_file.rsplit(".", 1)[0] + ".py")
    with open(script_path, "w", encoding="utf-8") as f:
        try:
            parsed = json.loads(script_content)
            if isinstance(parsed, dict) and "script" in parsed:
                script_content = parsed["script"]
        except json.JSONDecodeError:
            pass
        f.write(script_content)
    print(f"Скрипт сохранён: {script_path}")
    result = subprocess.run(["python", str(script_path)], capture_output=True, text=True)
    if result.returncode == 0:
        print("Скрипт выполнен успешно.")
        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                print(f"  {line}")
    else:
        print("Ошибка выполнения:")
        for line in result.stderr.strip().split("\n"):
            print(f"  {line}")


def main():
    if len(sys.argv) < 2:
        print("Использование: python agents/slides_orchestrator.py <lesson_dir> [--save | --visuals | --save-script]")
        sys.exit(1)

    lesson_dir = Path(sys.argv[1])
    if not lesson_dir.exists():
        print(f"Папка не найдена: {lesson_dir}")
        sys.exit(1)

    plan_path = lesson_dir / "plan.md"
    if not plan_path.exists():
        print(f"plan.md не найден в {lesson_dir}")
        sys.exit(1)

    plan = read_file(plan_path)
    plan_lines = parse_plan_slides(plan)

    slides_dir = lesson_dir / "slides_json"
    existing_slides = read_slides(slides_dir)
    current_num = next_slide_number(slides_dir)

    if len(sys.argv) >= 3 and sys.argv[2] == "--visuals":
        print("Проверка визуализаций...")
        gen_script = lesson_dir / "assets" / "generate_visuals.py"
        if gen_script.exists():
            from visuals_pipeline import check_visuals_quality, run_generate_visuals

            run_generate_visuals(lesson_dir)
            print("\n=== Проверка иллюстраций ===")
            issues = check_visuals_quality(lesson_dir)
            if issues:
                for i in issues:
                    print(f"  [warn] {i}")
            else:
                print("  OK: замечаний нет")
            print(
                f"\nДля AI-рецензии: python agents/visuals_pipeline.py {lesson_dir} --review"
            )
            print(f"Пересборка pptx: python agents/visuals_pipeline.py {lesson_dir}")
        else:
            generate_visualizations(lesson_dir, slides_dir)
        return

    if len(sys.argv) >= 4 and sys.argv[2] == "--save-script":
        save_and_run_script(lesson_dir, sys.argv[3], " ".join(sys.argv[4:]))
        return

    if current_num > len(plan_lines):
        print(f"Все слайды сгенерированы. Запусти: python agents/pptx_builder.py {lesson_dir}")
        return

    slide_topic = plan_lines[current_num - 1]

    if len(sys.argv) >= 3 and sys.argv[2] == "--save":
        raw = " ".join(sys.argv[3:]) if len(sys.argv) >= 4 else sys.stdin.read().strip()
        try:
            slide_data = parse_json_response(raw)
        except Exception as e:
            print(f"Ошибка парсинга JSON: {e}")
            sys.exit(1)
        save_slide(slides_dir, slide_data, current_num)
        print(f"\nДалее: python agents/slides_orchestrator.py {lesson_dir}")
        return

    prompt = build_prompt(plan, slide_topic, existing_slides)
    print(f"=== СЛАЙД {current_num} ИЗ {len(plan_lines)} ===")
    print(f"Тема: {slide_topic}")
    print()
    print(prompt)
    print(f"\nСохранить: python agents/slides_orchestrator.py {lesson_dir} --save '<JSON>'")


if __name__ == "__main__":
    main()
