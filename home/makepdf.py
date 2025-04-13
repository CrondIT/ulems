from reportlab.pdfgen import canvas

from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm

from reportlab.platypus import Paragraph, Frame

from reportlab.lib.styles import ParagraphStyle

# cyrillic font
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def make_pdf(page_data, text_data):
    page_width = page_data['page_width'] * mm
    page_height = page_data['page_height'] * mm
    page_size = (page_width, page_height)
    canva = canvas.Canvas("helloworld.pdf", page_size)

    # Загрузка фонового изображения
    image = page_data['image']
    img = ImageReader(image)
    canva.drawImage(img, 0, 0, page_width, page_height)

    # Словарь для отслеживания зарегистрированных шрифтов
    registered_fonts = {}

    for index, td in enumerate(text_data):
        font_path = td['user_font_file_path']

        # Генерация уникального имени шрифта на основе индекса
        if font_path not in registered_fonts:
            font_name = f"UserFont_{index}"
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            registered_fonts[font_path] = font_name
        else:
            font_name = registered_fonts[font_path]

        current_style = ParagraphStyle(
            name=f"Style_{index}",
            fontName=font_name,
            fontSize=td['font_size'],
            leading=td['font_leading'],
            textColor=td['font_color'],
            alignment=td['font_alignment'],
            justifyLastLine=1,
            wordWrap=True,
            borderColor=(0, 0, 250),
            borderWidth=0.5
        )

        current_paragraph = Paragraph(
            str(td['text']).replace('\n', '<br />\n'),
            current_style
        )

        if td['delta_y'] > td['start_y']:
            td['delta_y'] = td['start_y']

        current_frame = Frame(
            td['start_x'] * mm,
            (td['start_y'] - td['delta_y']) * mm,
            td['delta_x'] * mm,
            td['delta_y'] * mm,
            showBoundary=0
        )
        current_frame.addFromList([current_paragraph], canva)

    canva.showPage()
    canva.save()
