from reportlab.pdfgen import canvas

from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from reportlab.lib.colors import white

from reportlab.platypus import Paragraph, Frame

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet

import textwrap as textwrap

# cyrillic font
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def split_string(text, textwidth, strings):
    lines = []
    # text = text.replace('  ', ' ')
    text = text.replace('\n', ' ')
    # if case_number:
    lines = textwrap.wrap(text, textwidth)  # 25
    first_line = lines[0]
    remainder = ' '.join(lines[0:])

    lines = textwrap.wrap(remainder, textwidth)  # 25
    lines = lines[:strings]  # максимальное количество строк, не считая первой

    #  can.drawString(405, 775, first_line)
    #  for n, l in enumerate(lines, 1):
    #      can.drawString(405, 773 - (n*15), l)
    return lines


def make_pdf(page_width, page_height,
             font_size, image, texts,
             start_x, start_y):
    page_width = page_width * mm
    page_height = page_height * mm
    page_size = (page_width, page_height)
    canva = canvas.Canvas("helloworld.pdf", page_size)
    pdfmetrics.registerFont(TTFont("Arial", "ARIAL.TTF"))
    img = ImageReader(image)
    # for text in texts:
    canva.setFont("Arial", font_size)
    canva.setFillColor(white)
    canva.drawImage(img, 0, 0, page_width, page_height)
    # canva.drawString(start_x * mm, start_y * mm, texts)

    text = canva.beginText(start_x * mm, start_y * mm)
    text.setFont("Arial", font_size)
    text.textLine(texts)
    canva.drawText(text)

       # textlines=split_string(text, 25, 1)
       # print(textlines)
       # for n, l in enumerate(textlines,1):
       # print(texts)
       # canva.drawString(start_x, start_y, texts)

    canva.showPage()

    canva.save()


# def using paragraph
def make_pdf3(page_data, text_data):

    page_width = page_data['page_width'] * mm
    page_height = page_data['page_height'] * mm
    page_size = (page_width, page_height)
    canva = canvas.Canvas("helloworld.pdf", page_size)
    pdfmetrics.registerFont(TTFont("Arial", "ARIAL.TTF"))
    image = page_data['image']
    img = ImageReader(image)
    canva.drawImage(img, 0, 0, page_width, page_height)

    for td in text_data:
        current_style = ParagraphStyle(
            name="CurrentStyle",
            fontName="Arial",
            fontSize=td['font_size'],
            leading=td['font_leading'],
            textColor=td['font_color'],
            alignment=td['font_alignment'],
            justifyLastLine=1,
            wordWrap=True
            )
        current_paragraph = Paragraph(
            str(td['text']).replace('\n','<br />\n'),
            current_style
            )
       
        current_frame = Frame(td['start_x'] * mm,
                              td['start_y'] * mm,
                              td['delta_x'] * mm,
                              td['delta_y'] * mm,
                              showBoundary=0)
        current_frame.addFromList([current_paragraph], canva)

    canva.showPage()
    canva.save()


def make_pdf2(page_data, text_data):
    page_width = page_data['page_width'] * mm
    page_height = page_data['page_height'] * mm
    page_size = (page_width, page_height)
    canva = canvas.Canvas("helloworld.pdf", page_size)
    pdfmetrics.registerFont(TTFont("Arial", "ARIAL.TTF"))
    image = page_data['image']
    img = ImageReader(image)
    canva.drawImage(img, 0, 0, page_width, page_height)
    for td in text_data:
        canva.setFont("Arial", td['font_size'])
        canva.setFillColor(td['font_color'])
        
        #canva.drawString(start_x * mm, start_y * mm, texts)

        text = canva.beginText(td['start_x'] * mm, td['start_y'] * mm)
        text.setFont("Arial", td['font_size'])
        text.setLeading(td['font_leading'])
        text.textLines(td['text'])
        canva.drawText(text)

       # textlines=split_string(text, 25, 1)
       # print(textlines)
       # for n, l in enumerate(textlines,1):
       # print(texts)
       # canva.drawString(start_x, start_y, texts)

    canva.showPage()
    canva.save()
