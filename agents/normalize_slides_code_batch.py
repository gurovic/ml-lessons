"""Batch-normalize code_examples in all slides_json.

Использование:
    python agents/normalize_slides_code_batch.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from slide_code_utils import normalize_code_example

REPO = Path(__file__).resolve().parent.parent
LESSONS = REPO / "lessons"


def main() -> int:
    per_lesson: dict[str, int] = {}
    total_files = 0
    for lesson_dir in sorted(LESSONS.iterdir()):
        slides_dir = lesson_dir / "slides_json"
        if not slides_dir.is_dir():
            continue
        updated = 0
        for path in sorted(slides_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            examples = data.get("code_examples")
            if not isinstance(examples, list) or not examples:
                continue
            new_examples = []
            changed = False
            for ex in examples:
                if not isinstance(ex, dict):
                    new_examples.append(ex)
                    continue
                try:
                    norm = normalize_code_example(ex)
                except ValueError:
                    new_examples.append(ex)
                    continue
                if norm != ex:
                    changed = True
                new_examples.append(norm)
            if changed:
                data["code_examples"] = new_examples
                path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                updated += 1
        if updated:
            per_lesson[lesson_dir.name] = updated
            total_files += updated
        elif any((slides_dir / f).exists() for f in []):
            pass
        # print zero too for lessons with slides_json
        if slides_dir.exists() and any(slides_dir.glob("*.json")):
            print(f"{lesson_dir.name}: {updated} slides updated")
    print(f"TOTAL: {total_files} slide files updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
