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


def _image_aspect(img_path: Path) -> float:
    from PIL import Image

    with Image.open(img_path) as im:
        w, h = im.size
    return w / h if h else 1.0


def _visual_layout_slots(n: int, col_left: float, col_w: float, top: float, bottom: float):
    """Координаты ячеек (left, top, width, height) в дюймах для 1–4 картинок."""
    gap = 0.08
    h_avail = bottom - top

    if n <= 0:
        return []
    if n == 1:
        return [(col_left, top, col_w, h_avail)]
    if n == 2:
        slot_h = (h_avail - gap) / 2
        return [
            (col_left, top, col_w, slot_h),
            (col_left, top + slot_h + gap, col_w, slot_h),
        ]

    slot_w = (col_w - gap) / 2
    slot_h = (h_avail - gap) / 2
    if n == 3:
        return [
            (col_left, top, slot_w, slot_h),
            (col_left + slot_w + gap, top, slot_w, slot_h),
            (col_left, top + slot_h + gap, col_w, slot_h),
        ]
    return [
        (col_left, top, slot_w, slot_h),
        (col_left + slot_w + gap, top, slot_w, slot_h),
        (col_left, top + slot_h + gap, slot_w, slot_h),
        (col_left + slot_w + gap, top + slot_h + gap, slot_w, slot_h),
    ]


def _add_picture_fit(slide, img_path: Path, left, top, box_w, box_h):
    from pptx.util import Inches

    aspect = _image_aspect(img_path)
    box_aspect = box_w / box_h if box_h else aspect
    if aspect >= box_aspect:
        width = box_w
        height = width / aspect
    else:
        height = box_h
        width = height * aspect
    x = left + (box_w - width) / 2
    y = top + (box_h - height) / 2
    slide.shapes.add_picture(str(img_path), Inches(x), Inches(y), width=Inches(width))


def _add_hyperlink_run(paragraph, text: str, url: str, font_size, link_rgb):
    from pptx.dml.color import RGBColor

    run = paragraph.add_run()
    run.text = text
    run.font.size = font_size
    run.font.color.rgb = RGBColor(*link_rgb)
    run.hyperlink.address = url


def _render_references_slide(
    slide,
    slide_data: dict,
    assets_dir: Path,
    slide_num: int,
    *,
    set_paragraph_content,
    Pt,
    Inches,
    body_rgb,
    link_rgb,
):
    """Слайд type=references: литература слева, QR для Colab справа."""
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN

    from references_utils import format_paper_bullet, generate_qr_png

    refs = slide_data.get("references", [])
    papers = [r for r in refs if r.get("kind") == "paper"]
    colabs = [r for r in refs if r.get("kind") == "colab"]

    body_left, body_top = 0.7, 1.45
    body_width = 7.2
    y_cursor = body_top

    def add_section_heading(text: str):
        nonlocal y_cursor
        box = slide.shapes.add_textbox(
            Inches(body_left), Inches(y_cursor), Inches(body_width), Inches(0.35)
        )
        p = box.text_frame.paragraphs[0]
        p.text = text
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = RGBColor(*body_rgb)
        y_cursor += 0.38

    def add_text_line(height: float = 0.55):
        nonlocal y_cursor
        box = slide.shapes.add_textbox(
            Inches(body_left), Inches(y_cursor), Inches(body_width), Inches(height)
        )
        tf = box.text_frame
        tf.word_wrap = True
        y_cursor += height
        return tf.paragraphs[0]

    if papers:
        add_section_heading("Литература")
        for ref in papers:
            p = add_text_line(0.62)
            p.space_after = Pt(4)
            bullet_text = format_paper_bullet(ref)
            url = ref.get("url")
            if url:
                for w in set_paragraph_content(
                    p, "• ", font_size=Pt(16), color=body_rgb
                ):
                    print(f"  [warn] Слайд {slide_num}, литература: {w}")
                _add_hyperlink_run(p, bullet_text, url, Pt(16), link_rgb)
            else:
                for w in set_paragraph_content(
                    p, f"• {bullet_text}", font_size=Pt(16), color=body_rgb
                ):
                    print(f"  [warn] Слайд {slide_num}, литература: {w}")

    if colabs:
        add_section_heading("Практика в Colab")
        for entry in colabs:
            url = entry.get("url", "")
            label = entry.get("label") or entry.get("title", "Colab")
            p = add_text_line(0.5)
            for w in set_paragraph_content(
                p, f"• {label}: ", font_size=Pt(15), color=body_rgb
            ):
                print(f"  [warn] Слайд {slide_num}, Colab: {w}")
            if url:
                _add_hyperlink_run(p, url, url, Pt(14), link_rgb)

    bullets = slide_data.get("bullets", [])
    if bullets:
        y_cursor += 0.1
        for bullet in bullets:
            p = add_text_line(0.45)
            for w in set_paragraph_content(
                p, f"• {bullet}", font_size=Pt(15), color=body_rgb
            ):
                print(f"  [warn] Слайд {slide_num}, буллет: {w}")

    qr_size = 1.15
    qr_gap = 0.25
    qr_left = 9.0
    qr_top_start = 1.6
    for i, entry in enumerate(colabs):
        url = entry.get("url", "")
        if not url:
            continue
        label = entry.get("label") or entry.get("title", "Colab")
        top = qr_top_start + i * (qr_size + qr_gap + 0.35)
        try:
            qr_path = assets_dir / f"_qr_ref_{slide_num}_{i}.png"
            generate_qr_png(url, qr_path)
            slide.shapes.add_picture(
                str(qr_path), Inches(qr_left), Inches(top), width=Inches(qr_size)
            )
            qr_path.unlink(missing_ok=True)
        except ImportError:
            print("  [warn] Установи qrcode: pip install qrcode[pil]")
            break

        cap = slide.shapes.add_textbox(
            Inches(qr_left - 0.1),
            Inches(top + qr_size + 0.02),
            Inches(qr_size + 0.4),
            Inches(0.3),
        )
        cp = cap.text_frame.paragraphs[0]
        cp.text = label
        cp.font.size = Pt(10)
        cp.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        cp.alignment = PP_ALIGN.CENTER


def _place_visuals(slide, visuals: list[dict], assets_dir: Path, slide_num: int):
    paths = []
    for visual_obj in visuals:
        output = visual_obj.get("output", "")
        if not output:
            continue
        img_path = assets_dir / output
        if img_path.exists():
            paths.append(img_path)
        else:
            print(f"  [warn] Слайд {slide_num}: нет файла {img_path.name}")

    if not paths:
        return

    col_left, col_w = 8.35, 4.75
    top, bottom = 1.45, 6.35
    slots = _visual_layout_slots(len(paths), col_left, col_w, top, bottom)
    for img_path, (left, slot_top, w, h) in zip(paths, slots):
        try:
            _add_picture_fit(slide, img_path, left, slot_top, w, h)
        except Exception as e:
            print(f"Не удалось вставить {img_path}: {e}")


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
        is_references = slide_data.get("type") == "references"

        if is_references:
            _render_references_slide(
                slide,
                slide_data,
                assets_dir,
                i,
                set_paragraph_content=set_paragraph_content,
                Pt=Pt,
                Inches=Inches,
                body_rgb=body_rgb,
                link_rgb=link_rgb,
            )
        else:
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

            _place_visuals(slide, visuals, assets_dir, i)

            # Ссылка и QR-код
            link = slide_data.get("link")
            if link and link.get("url"):
                url = link["url"]
                label = link.get("label", url)

                link_box = slide.shapes.add_textbox(Inches(0.7), Inches(6.5), Inches(6), Inches(0.5))
                tf_link = link_box.text_frame
                tf_link.word_wrap = True
                p_link = tf_link.paragraphs[0]
                for w in set_paragraph_content(
                    p_link, f"{label}: ", font_size=Pt(14), color=link_rgb
                ):
                    print(f"  [warn] Слайд {i}, ссылка: {w}")
                _add_hyperlink_run(p_link, url, url, Pt(14), link_rgb)

                try:
                    from references_utils import generate_qr_png

                    qr_path = assets_dir / "_qr_temp.png"
                    generate_qr_png(url, qr_path, box_size=10)
                    slide.shapes.add_picture(str(qr_path), Inches(11.5), Inches(4.5), width=Inches(1.5))
                    qr_path.unlink(missing_ok=True)
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
