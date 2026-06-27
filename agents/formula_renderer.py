"""Рендеринг LaTeX-формул в PNG через matplotlib (mathtext).

Использование:
    python agents/formula_renderer.py "<tex>" <output_path> [fontsize]
    python agents/formula_renderer.py <lesson_dir> --batch

Поддерживает:
    - Математические символы (греческие буквы, интегралы, дроби и т.д.)
    - Unicode-текст (кириллица, спецсимволы)
    - Прозрачный фон
    - Многострочные формулы (строки через \\\\))
    - Пакетную обработку всех слайдов урока

Формат поля formula в JSON-слайде:
    {
      "formula": {
        "tex": "E = mc^2",
        "label": "Энергия покоя",
        "fontsize": 24,
        "output": "formula_energy.png"
      }
    }
"""

import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def render_formula(tex: str, output_path: str, fontsize: int = 20):
    """
    Рендерит LaTeX-формулу в PNG-файл.
    
    tex — строка в формате mathtext (без внешних $).
    output_path — путь для сохранения PNG.
    fontsize — размер шрифта (по умолчанию 20).
    
    Формула рендерится с прозрачным фоном для вставки в презентацию.
    """
    fig, ax = plt.subplots(figsize=(0.1, 0.1))
    
    ax.text(
        0, 0, f"${tex}$",
        fontsize=fontsize,
        color='black',
        va='bottom',
        ha='left',
        transform=ax.transData,
        usetex=False,
        math_fontfamily='dejavusans'
    )
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    fig.patch.set_alpha(0)
    
    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches='tight',
        transparent=True,
        pad_inches=0.05
    )
    plt.close()
    print(f"  Сохранено: {output_path}")


def render_multiline(tex_lines: list[str], output_path: str, fontsize: int = 20):
    """
    Рендерит многострочную формулу (строки разделённые \\\\).
    """
    n = len(tex_lines)
    fig, ax = plt.subplots(figsize=(0.1, 0.1))
    
    for i, line in enumerate(tex_lines):
        y_pos = 1.0 - (i + 0.5) / n
        ax.text(
            0, y_pos, f"${line}$",
            fontsize=fontsize,
            color='black',
            va='center',
            ha='left',
            transform=ax.transData,
            usetex=False,
            math_fontfamily='dejavusans'
        )
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    fig.patch.set_alpha(0)
    
    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches='tight',
        transparent=True,
        pad_inches=0.05
    )
    plt.close()
    print(f"  Сохранено (многострочная): {output_path}")


def render_slide_formulas(slides_dir: Path, assets_dir: Path) -> list[str]:
    """
    Проходит по всем JSON-слайдам в slides_dir и рендерит формулы.
    
    Возвращает список сгенерированных файлов PNG.
    """
    import json
    from slide_utils import list_slide_files

    created_files = []
    json_files = list_slide_files(slides_dir)
    
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            slide_data = json.load(f)
        
        formula = slide_data.get("formula", {})
        if not formula:
            continue
        
        tex = formula.get("tex", "")
        if not tex:
            continue
        
        output = formula.get("output", "")
        if not output:
            continue
        
        output_path = assets_dir / output
        if output_path.exists():
            print(f"  [skip] {output} уже существует")
            continue
        
        fontsize = formula.get("fontsize", 24)
        
        lines = tex.split("\\\\")
        if len(lines) > 1:
            lines = [l.strip() for l in lines if l.strip()]
            render_multiline(lines, str(output_path), fontsize)
        else:
            render_formula(tex, str(output_path), fontsize)
        
        created_files.append(output)
    
    return created_files


def main():
    if len(sys.argv) < 3:
        print("Использование:")
        print("  1. Одиночная формула: python agents/formula_renderer.py '<tex>' <output_path> [fontsize]")
        print("  2. Пакетный режим:   python agents/formula_renderer.py <lesson_dir> --batch")
        sys.exit(1)
    
    if len(sys.argv) >= 3 and sys.argv[2] == "--batch":
        lesson_dir = Path(sys.argv[1])
        slides_dir = lesson_dir / "slides_json"
        assets_dir = lesson_dir / "assets"
        
        if not slides_dir.exists():
            print(f"Папка со слайдами не найдена: {slides_dir}")
            sys.exit(1)
        
        assets_dir.mkdir(parents=True, exist_ok=True)
        created = render_slide_formulas(slides_dir, assets_dir)
        if created:
            print(f"Сгенерировано формул: {len(created)}")
        else:
            print("Новых формул не найдено.")
        return
    
    tex = sys.argv[1]
    output_path = sys.argv[2]
    fontsize = int(sys.argv[3]) if len(sys.argv) >= 4 else 20
    render_formula(tex, output_path, fontsize)


if __name__ == '__main__':
    main()

