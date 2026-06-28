"""Apply references slides to all complete lessons with code.ipynb."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
AGENT = REPO_ROOT / "agents" / "references_agent.py"

LESSONS = [
    "lineynaya_regressiya",
    "logisticheskaya_regressiya",
    "derevo_resheniy",
    "pandas",
    "vizualizatsiya",
]


def main() -> int:
    errors: list[str] = []

    for name in LESSONS:
        lesson_dir = REPO_ROOT / "lessons" / name
        refs_json = lesson_dir / "references.json"

        if not lesson_dir.is_dir():
            errors.append(f"{name}: lesson directory not found")
            continue
        if not refs_json.exists():
            errors.append(f"{name}: references.json missing")
            continue

        print(f"\n=== {name} ===")
        result = subprocess.run(
            [sys.executable, str(AGENT), str(lesson_dir), "--apply"],
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            errors.append(f"{name}: --apply failed (exit {result.returncode})")

    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\nAll lessons processed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
