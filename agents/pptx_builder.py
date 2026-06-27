"""
Сборщик презентации из JSON-слайдов.

Использование: python agents/pptx_builder.py <lesson_dir>
"""

import json
import sys
from datetime import date
from pathlib import Path


def read_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_config(root_dir: Path) -> dict:
    """Загружает project_config.json из корня проекта, если есть."""
    cfg_path = root_dir / "project_config.json"
    if cfg_path.exists():
        return json.loads(read_file(cfg_path))
    return {}


def load_slides(slides_dir: Path) -> list[dict]:
    from slide_utils import list_slide_files

    return [json.loads(read_file(f)) for f in list_slide_files(slides_dir)]


def build_presentation(slides: list[dict], output_path: Path, assets_dir: Path, lesson_dir: Path):
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN
        from rich_text import set_paragraph_content
    except ImportError as e:
        print(f"Установи зависимости: pip install -r requirements.txt ({e})")
        sys.exit(1)

    title_rgb = (0x1A, 0x1A, 0x2E)
    body_rgb = (0x00, 0x00, 0x00)
    link_rgb = (0x33, 0x66, 0xCC)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Титульный слайд
    project_config = load_config(Path(__file__).parent.parent)

    info = {}
    info_path = lesson_dir / "info.json"
    if info_path.exists():
        with open(info_path, "r", encoding="utf-8") as f:
            info = json.load(f)

    lesson_title = info.get("topic", lesson_dir.name)
    author = info.get("author", "") or project_config.get("author", "")
    email = info.get("email", "") or project_config.get("email", "")
    telegram = info.get("telegram", "") or info.get("tg", "") or project_config.get("telegram", "")
    today = date.today().strftime("%d.%m.%Y")

    title_slide = prs.slides.add_slide(prs.slide_layouts[6])

    tb = title_slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(11), Inches(2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = lesson_title
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
    p.alignment = PP_ALIGN.CENTER

    if author:
        tb2 = title_slide.shapes.add_textbox(Inches(1), Inches(4), Inches(11), Inches(0.6))
        p2 = tb2.text_frame.paragraphs[0]
        p2.text = f"Автор: {author}"
        p2.font.size = Pt(20)
        p2.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        p2.alignment = PP_ALIGN.CENTER

    contacts = " | ".join(filter(None, [f"Email: {email}" if email else "", f"Telegram: {telegram}" if telegram else ""]))
    if contacts:
        tb3 = title_slide.shapes.add_textbox(Inches(1), Inches(4.7), Inches(11), Inches(0.6))
        p3 = tb3.text_frame.paragraphs[0]
        p3.text = contacts
        p3.font.size = Pt(18)
        p3.font.color.rgb = RGBColor(0x77, 0x77, 0x77)
        p3.alignment = PP_ALIGN.CENTER

    tb4 = title_slide.shapes.add_textbox(Inches(1), Inches(5.5), Inches(11), Inches(0.5))
    p4 = tb4.text_frame.paragraphs[0]
    p4.text = today
    p4.font.size = Pt(16)
    p4.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    p4.alignment = PP_ALIGN.CENTER

    # Слайды
    for i, slide_data in enumerate(slides, 1):
        slide = prs.slides.add_slide(prs.slide_layouts[6])

        if slide_data.get("formula"):
            print(f"  [warn] Слайд {i}: поле formula устарело — используйте $...$ в тексте (docs/formulas.md)")

        tb = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.3), Inches(1))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        for w in set_paragraph_content(
            p,
            slide_data.get("title", f"Слайд {i}"),
            font_size=Pt(32),
            bold=True,
            color=title_rgb,
        ):
            print(f"  [warn] Слайд {i}, заголовок: {w}")

        visuals = slide_data.get("visuals", [])
        has_visuals = any(v.get("output") for v in visuals)
        body_width = Inches(7.5) if has_visuals else Inches(12.3)

        bullets = slide_data.get("bullets", [])
        if bullets:
            body = slide.shapes.add_textbox(Inches(0.7), Inches(1.5), body_width, Inches(5.5))
            tf2 = body.text_frame
            tf2.word_wrap = True
            for j, bullet in enumerate(bullets):
                p = tf2.paragraphs[0] if j == 0 else tf2.add_paragraph()
                p.space_after = Pt(8)
                for w in set_paragraph_content(
                    p, bullet, font_size=Pt(20), color=body_rgb
                ):
                    print(f"  [warn] Слайд {i}, буллет {j + 1}: {w}")

        right_col_left = Inches(8.5)
        right_col_width = Inches(4.5)
        visual_top = Inches(1.5)
        for visual_obj in visuals:
            visual = visual_obj.get("output", "")
            if visual:
                img_path = assets_dir / visual
                if img_path.exists():
                    try:
                        slide.shapes.add_picture(str(img_path), right_col_left, visual_top, width=right_col_width)
                        visual_top += Inches(3.0)
                    except Exception as e:
                        print(f"Не удалось вставить {img_path}: {e}")

        # Ссылка и QR-код
        link = slide_data.get("link")
        if link and link.get("url"):
            url = link["url"]
            label = link.get("label", url)

            # Текст ссылки (кликабельный)
            link_box = slide.shapes.add_textbox(Inches(0.7), Inches(6.5), Inches(6), Inches(0.5))
            tf_link = link_box.text_frame
            tf_link.word_wrap = True
            p_link = tf_link.paragraphs[0]
            for w in set_paragraph_content(
                p_link, f"{label}: ", font_size=Pt(14), color=link_rgb
            ):
                print(f"  [warn] Слайд {i}, ссылка: {w}")
            run = p_link.add_run()
            run.text = url
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(*link_rgb)
            run.hyperlink.address = url

            # Генерация QR-кода
            try:
                import qrcode
                qr_path = assets_dir / "_qr_temp.png"
                qr = qrcode.QRCode(box_size=10, border=1)
                qr.add_data(url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img.save(str(qr_path))
                slide.shapes.add_picture(str(qr_path), Inches(11.5), Inches(4.5), width=Inches(1.5))
                qr_path.unlink()  # удаляем временный файл
            except ImportError:
                print("  [warn] Установи qrcode: pip install qrcode[pil]")

        notes = slide_data.get("notes")
        if notes:
            slide.notes_slide.notes_text_frame.text = notes

    prs.save(str(output_path))
    print(f"Сохранено: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Использование: python agents/pptx_builder.py <lesson_dir>")
        sys.exit(1)

    lesson_dir = Path(sys.argv[1])
    if not lesson_dir.exists():
        print(f"Папка не найдена: {lesson_dir}")
        sys.exit(1)

    slides_dir = lesson_dir / "slides_json"
    if not slides_dir.exists():
        print(f"Папка со слайдами не найдена: {slides_dir}")
        sys.exit(1)

    slides = load_slides(slides_dir)
    if not slides:
        print(f"Нет JSON-файлов в {slides_dir}")
        sys.exit(1)

    print(f"Загружено слайдов: {len(slides)}")
    build_presentation(slides, lesson_dir / "presentation.pptx", lesson_dir / "assets", lesson_dir)


if __name__ == "__main__":
    main()
