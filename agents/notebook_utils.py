"""Отбор слайдов для ноутбука и сборка code.ipynb."""

import json
import re
from pathlib import Path
from typing import Any

from slide_utils import parse_json_response

THEORY_TITLE_MARKERS = (
    "почему нам важна",
    "почему мы строим",
    "почему в узле",
    "зачем дерево",
    "джини или энтропия",
    "классические алгоритмы",
    "многоклассовая классификация без",
)

MOTIVATION_TITLE_MARKERS = (
    "от игры к математике",
    "акинатор",
)

STRONG_TEXT_MARKERS = (
    "jupyter",
    "notebook",
    "ipywidgets",
    "sklearn",
    "эксперимент",
    "сравни",
    "сравнен",
    "замер",
    "скорост",
    "время работы",
    "демо кода",
)

API_MARKERS = (
    "DecisionTree",
    "plot_tree",
    "export_graphviz",
    "export_text",
    "class_weight",
    ".fit(",
    "feature_importances",
    "train_test_split",
    "cross_val",
    "GridSearch",
)

VIZ_LIB_MARKERS = (
    "matplotlib",
    "seaborn",
    "graphviz",
    "plotly",
    "ipywidgets",
    "интерактив",
)


def _slide_text(slide: dict) -> str:
    parts = slide.get("bullets", []) + [slide.get("notes", "")]
    for v in slide.get("visuals", []):
        parts.append(v.get("description", ""))
    nb = slide.get("notebook")
    if isinstance(nb, dict) and nb.get("hint"):
        parts.append(str(nb["hint"]))
    return "\n".join(p for p in parts if p)


def _title_lower(slide: dict) -> str:
    return slide.get("title", "").lower()


def notebook_config(slide: dict) -> dict[str, Any] | None:
    """Вернуть конфиг ноутбука для слайда или None, если слайд пропускаем."""
    nb = slide.get("notebook")
    if nb is False:
        return None
    if isinstance(nb, dict) and nb.get("include") is False:
        return None
    if nb is True or (isinstance(nb, dict) and nb.get("include") is True):
        cfg = dict(nb) if isinstance(nb, dict) else {}
        cfg.setdefault("include", True)
        cfg.setdefault("reason", "explicit")
        return cfg

    title = _title_lower(slide)
    if any(m in title for m in MOTIVATION_TITLE_MARKERS):
        return None
    if any(m in title for m in THEORY_TITLE_MARKERS):
        return None

    text = _slide_text(slide)
    text_lower = text.lower()
    has_api = any(m in text for m in API_MARKERS)
    has_strong = any(m in text_lower for m in STRONG_TEXT_MARKERS)
    has_viz = bool(slide.get("visuals"))
    has_viz_code = has_viz and any(m in text_lower for m in VIZ_LIB_MARKERS)
    notes_lower = slide.get("notes", "").lower()
    notes_want_code = "jupyter" in notes_lower or "notebook" in notes_lower

    reasons: list[str] = []
    if has_api:
        reasons.append("api")
    if has_strong:
        reasons.append("keywords")
    if has_viz_code:
        reasons.append("visuals")
    if notes_want_code:
        reasons.append("notes_jupyter")

    if not reasons:
        return None

    kinds: list[str] = []
    if has_api:
        kinds.append("example")
    if any(w in text_lower for w in ("сравни", "сравнен", "скорост", "время", "эксперимент")):
        kinds.append("experiment")
    if has_viz_code:
        kinds.append("viz")
    if "ipywidgets" in text_lower or "интерактив" in text_lower or "слайдер" in text_lower:
        kinds.append("interactive")
    if not kinds:
        kinds = ["example"] if has_api else ["viz"]

    return {"include": True, "reason": "+".join(reasons), "kinds": kinds}


def select_slides_for_notebook(slides: list[dict]) -> list[tuple[int, dict, dict]]:
    """(номер слайда 1-based, slide, config)."""
    selected = []
    for i, slide in enumerate(slides, 1):
        cfg = notebook_config(slide)
        if cfg:
            selected.append((i, slide, cfg))
    return selected


def slide_to_notebook_context(index: int, slide: dict, cfg: dict) -> str:
    title = slide.get("title", "")
    lines = [f"### Слайд {index:02d}: «{title}»"]
    lines.append(f"_Отбор:_ {cfg.get('reason', '?')}; _типы:_ {', '.join(cfg.get('kinds', ['example']))}")
    if cfg.get("hint"):
        lines.append(f"_Подсказка автора:_ {cfg['hint']}")
    for bullet in slide.get("bullets", []):
        lines.append(f"- {bullet}")
    if slide.get("notes"):
        lines.append(f"_Заметки преподавателя:_ {slide['notes']}")
    for v in slide.get("visuals", []):
        out = v.get("output", "")
        exists = f" (файл assets/{out})" if out else ""
        lines.append(f"_Визуализация{exists}:_ {v.get('description', '')}")
    return "\n".join(lines)


def _normalize_source(source: str | list[str]) -> list[str]:
    if isinstance(source, list):
        return [line if line.endswith("\n") else line + "\n" for line in source]
    if not source:
        return []
    return [line + "\n" for line in source.split("\n")]


def _make_cell(cell_type: str, source: str | list[str]) -> dict:
    return {
        "cell_type": cell_type,
        "metadata": {},
        "source": _normalize_source(source),
    }


def default_setup_cell() -> dict:
    source = """\
# Setup
%matplotlib inline

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    from IPython.display import display
except ImportError:
    display = print

np.random.seed(42)
"""
    return _make_cell("code", source)


def _is_import_line(line: str) -> bool:
    s = line.strip()
    return s.startswith("import ") or s.startswith("from ")


def _split_import_block(lines: list[str], start: int) -> tuple[list[str], int]:
    block = [lines[start]]
    stripped = lines[start].strip()
    if "(" in stripped and ")" not in stripped:
        i = start + 1
        while i < len(lines):
            block.append(lines[i])
            if ")" in lines[i]:
                return block, i + 1
            i += 1
        return block, i
    return block, start + 1


def _try_except_display_block(lines: list[str], start: int) -> tuple[list[str], int] | None:
    if lines[start].strip() != "try:":
        return None
    if start + 1 >= len(lines):
        return None
    if "IPython.display" not in lines[start + 1]:
        return None
    block = [lines[start]]
    i = start + 1
    while i < len(lines):
        block.append(lines[i])
        if lines[i].strip().startswith("display = "):
            return block, i + 1
        i += 1
    return None


def _parse_code_cell_imports(source: str) -> tuple[list[str], str]:
    """Импорты / try-display → setup; остальное — тело ячейки."""
    if not source.strip():
        return [], ""

    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    import_blocks: list[str] = []
    other: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            if other and other[-1] != "":
                other.append("")
            i += 1
            continue
        if stripped.startswith("# Setup") or stripped.startswith("# Практика"):
            i += 1
            continue
        if stripped == "%matplotlib inline":
            i += 1
            continue
        if stripped.startswith("np.random.seed"):
            i += 1
            continue
        display_block = _try_except_display_block(lines, i)
        if display_block is not None:
            block, i = display_block
            import_blocks.append("\n".join(block))
            continue
        if _is_import_line(stripped):
            block, i = _split_import_block(lines, i)
            import_blocks.append("\n".join(block))
            continue
        other.append(line)
        i += 1

    body = "\n".join(other).strip()
    while body.endswith("\n\n"):
        body = body[:-1]
    return import_blocks, body


_DISPLAY_FALLBACK = """try:
    from IPython.display import display
except ImportError:
    display = print"""


def consolidate_imports_in_notebook(nb: dict) -> dict:
    """Все import/from (и try/display) — в первую code-ячейку Setup; из остальных — убрать."""
    cells = list(nb.get("cells", []))
    setup_idx = find_setup_cell_index(cells)
    all_imports: list[str] = []
    seen: set[str] = set()
    rebuilt: list[dict] = []

    for i, cell in enumerate(cells):
        if cell.get("cell_type") != "code":
            rebuilt.append(cell)
            continue
        blocks, body = _parse_code_cell_imports(cell_source(cell))
        for block in blocks:
            key = block.strip()
            if key and key not in seen:
                seen.add(key)
                all_imports.append(block.strip())
        if setup_idx is not None and i == setup_idx:
            continue
        if body:
            rebuilt.append(_make_cell("code", body))

    if _DISPLAY_FALLBACK not in all_imports and _DISPLAY_FALLBACK not in seen:
        if not any("IPython.display" in b for b in all_imports):
            all_imports.append(_DISPLAY_FALLBACK)

    setup_lines = ["# Setup", "%matplotlib inline", ""]
    setup_lines.extend(all_imports)
    setup_lines.extend(["", "np.random.seed(42)"])
    setup_cell = _make_cell("code", "\n".join(setup_lines) + "\n")

    if setup_idx is not None:
        rebuilt.insert(setup_idx, setup_cell)
    else:
        insert_at = 1 if rebuilt and rebuilt[0].get("cell_type") == "markdown" else 0
        rebuilt.insert(insert_at, setup_cell)

    out = dict(nb)
    out["cells"] = rebuilt
    return out


def build_ipynb(
    sections: list[dict],
    topic: str = "Урок",
    setup: bool = True,
    *,
    consolidate: bool = True,
) -> dict:
    cells: list[dict] = []
    if setup:
        cells.append(
            _make_cell(
                "markdown",
                f"# {topic}\n\nПрактические ячейки к слайдам презентации. "
                "Заголовки секций совпадают с заголовками слайдов.",
            )
        )
        cells.append(default_setup_cell())

    for section in sections:
        title = section.get("slide_title", "Без названия")
        kind = section.get("kind", "")
        header = f"## {title}"
        if kind:
            header += f" `({kind})`"
        cells.append(_make_cell("markdown", header))
        for cell in section.get("cells", []):
            ctype = cell.get("type", "code")
            if ctype not in ("markdown", "code"):
                ctype = "code"
            cells.append(_make_cell(ctype, cell.get("source", "")))

    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    if consolidate:
        return consolidate_imports_in_notebook(nb)
    return nb


def parse_notebook_response(raw: str) -> dict:
    data = parse_json_response(raw)
    if not isinstance(data, dict):
        raise ValueError("Ответ должен быть JSON-объектом")
    if "sections" not in data:
        raise ValueError("В ответе нет поля sections")
    if not isinstance(data["sections"], list):
        raise ValueError("sections должен быть массивом")
    return data


def save_ipynb(path: Path, notebook: dict) -> Path:
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def list_assets(lesson_dir: Path) -> list[str]:
    assets = lesson_dir / "assets"
    if not assets.exists():
        return []
    return sorted(p.name for p in assets.glob("*") if p.is_file() and p.suffix.lower() in (".png", ".svg", ".jpg"))


NOTEBOOK_FILES = ("code.ipynb", "project.ipynb")

SLIDE_REF_PATTERN = re.compile(
    r"слайд\s+\d+|см\.\s*слайд|\b\d{2}\.json\b",
    re.IGNORECASE,
)


def cell_source(cell: dict) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return src or ""


def load_ipynb(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_setup_cell_index(cells: list[dict]) -> int | None:
    for i, cell in enumerate(cells):
        if cell.get("cell_type") != "code":
            continue
        text = cell_source(cell).lstrip()
        if text.startswith("# Setup") or text.startswith("# Практика"):
            return i
    return None


def section_titles_from_nb(nb: dict) -> list[str]:
    titles: list[str] = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        text = cell_source(cell).strip()
        m = re.match(r"^##\s+(.+?)(?:\s+`\([^)]+\)`)?\s*$", text)
        if m:
            titles.append(m.group(1).strip())
    return titles


def check_notebook_syntax(nb: dict, label: str) -> list[str]:
    issues: list[str] = []
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        src = cell_source(cell)
        if not src.strip():
            issues.append(f"{label}: code-ячейка {i} пустая")
            continue
        stripped = "\n".join(
            line for line in src.split("\n")
            if not line.strip().startswith("%") and not line.strip().startswith("!")
        )
        try:
            compile(stripped, f"<{label}:{i}>", "exec")
        except SyntaxError as e:
            issues.append(f"{label}: code-ячейка {i} — синтаксис: {e.msg} (строка {e.lineno})")
    return issues


def check_setup_and_imports(nb: dict, label: str) -> list[str]:
    issues: list[str] = []
    cells = nb.get("cells", [])
    setup_idx = find_setup_cell_index(cells)
    if setup_idx is None:
        issues.append(f"{label}: нет code-ячейки `# Setup`")
        return issues

    setup_src = cell_source(cells[setup_idx])
    if "%matplotlib inline" not in setup_src:
        issues.append(f"{label}: в Setup нет `%matplotlib inline`")
    if "np.random.seed" not in setup_src:
        issues.append(f"{label}: в Setup нет `np.random.seed(42)`")

    for i, cell in enumerate(cells):
        if cell.get("cell_type") != "code" or i == setup_idx:
            continue
        for line in cell_source(cell).split("\n"):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                preview = stripped[:70] + ("…" if len(stripped) > 70 else "")
                issues.append(f"{label}: ячейка {i} — import вне Setup: {preview}")
            elif stripped == "%matplotlib inline" or stripped.startswith("np.random.seed"):
                issues.append(f"{label}: ячейка {i} — seed/matplotlib inline вне Setup")
    return issues


def check_slide_cross_refs(nb: dict, label: str) -> list[str]:
    issues: list[str] = []
    for i, cell in enumerate(nb.get("cells", [])):
        text = cell_source(cell)
        if SLIDE_REF_PATTERN.search(text):
            issues.append(f"{label}: ячейка {i} — перекрёстная ссылка на слайд/файл JSON")
    return issues


def check_code_ipynb_slides(nb: dict, slides: list[dict]) -> list[str]:
    issues: list[str] = []
    selected = select_slides_for_notebook(slides)
    expected = {slide.get("title", "") for _, slide, _ in selected}
    actual = set(section_titles_from_nb(nb))
    missing = expected - actual
    extra = actual - expected
    if missing:
        issues.append(f"code.ipynb: нет секций для слайдов: {', '.join(sorted(missing))}")
    if extra:
        issues.append(f"code.ipynb: лишние секции (нет в отборе): {', '.join(sorted(extra))}")
    return issues


def check_project_narrative(nb: dict) -> list[str]:
    issues: list[str] = []
    md_parts = [cell_source(c) for c in nb.get("cells", []) if c.get("cell_type") == "markdown"]
    code_parts = [cell_source(c) for c in nb.get("cells", []) if c.get("cell_type") == "code"]
    all_md = "\n".join(md_parts)
    all_code = "\n".join(code_parts)

    if "Решение:" not in all_md:
        issues.append("project.ipynb: нет markdown «Решение:» между этапами")
    if "final_model" not in all_code and "final_pipe" not in all_code:
        issues.append("project.ipynb: нет переменной final_model / final_pipe")
    split_count = all_code.count("train_test_split")
    if split_count == 0:
        issues.append("project.ipynb: нет train_test_split")
    elif split_count > 1:
        issues.append(f"project.ipynb: train_test_split встречается {split_count} раз (ожидается один)")
    if re.search(r"\bmake_(classification|regression)\b", all_code):
        issues.append("project.ipynb: синтетический make_* — допустимо только в code.ipynb")
    return issues


def check_notebook_file(
    path: Path,
    *,
    slides: list[dict] | None = None,
) -> list[str]:
    """Программная проверка одного ipynb."""
    label = path.name
    if not path.exists():
        return [f"{label}: файл отсутствует"]

    try:
        nb = load_ipynb(path)
    except json.JSONDecodeError as e:
        return [f"{label}: невалидный JSON — {e}"]

    issues: list[str] = []
    issues.extend(check_notebook_syntax(nb, label))
    issues.extend(check_setup_and_imports(nb, label))
    issues.extend(check_slide_cross_refs(nb, label))

    if label == "code.ipynb" and slides is not None:
        issues.extend(check_code_ipynb_slides(nb, slides))
    if label == "project.ipynb":
        issues.extend(check_project_narrative(nb))

    return issues


def check_lesson_notebooks(lesson_dir: Path) -> list[str]:
    """Проверка code.ipynb и project.ipynb урока."""
    slides_dir = lesson_dir / "slides_json"
    slides: list[dict] | None = None
    if slides_dir.exists():
        from slide_utils import read_slides

        slides = read_slides(slides_dir)

    issues: list[str] = []
    for name in NOTEBOOK_FILES:
        issues.extend(check_notebook_file(lesson_dir / name, slides=slides))
    return issues


def notebook_to_prompt_block(path: Path, *, max_code_lines: int = 40) -> str:
    """Сжатое представление ноутбука для промпта рецензента."""
    if not path.exists():
        return f"### {path.name}\n\n(файл отсутствует)\n"

    nb = load_ipynb(path)
    lines = [f"### {path.name} ({len(nb.get('cells', []))} ячеек)\n"]
    for i, cell in enumerate(nb.get("cells", [])):
        ctype = cell.get("cell_type", "?")
        src = cell_source(cell).rstrip()
        if ctype == "code" and src.count("\n") > max_code_lines:
            head = "\n".join(src.split("\n")[:max_code_lines])
            src = f"{head}\n# … ({src.count(chr(10)) + 1 - max_code_lines} строк скрыто)"
        lines.append(f"#### Ячейка {i} ({ctype})\n```\n{src}\n```\n")
    return "\n".join(lines)


def parse_reviewer_response(raw: str) -> dict:
    """Разбор JSON-ответа рецензента ноутбуков (code/project sections + report)."""
    data = parse_json_response(raw)
    if not isinstance(data, dict):
        raise ValueError("Ответ должен быть JSON-объектом")
    for key in ("code", "project"):
        block = data.get(key)
        if block is None:
            continue
        if not isinstance(block, dict) or "sections" not in block:
            raise ValueError(f"Поле {key} должно содержать sections")
        if not isinstance(block["sections"], list):
            raise ValueError(f"{key}.sections должен быть массивом")
    return data
