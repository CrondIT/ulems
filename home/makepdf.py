from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from reportlab.lib.colors import white
from reportlab.lib.styles import ParagraphStyle

import textwrap as textwrap


# cyrillic font
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def split_string(text, textwidth, strings):
    lines=[]
   # text = text.replace('  ', ' ')
    text = text.replace('\n', ' ')
   #if case_number:
    lines = textwrap.wrap(text, textwidth) # 25
    first_line = lines[0]
    remainder = ' '.join(lines[0:])

    lines = textwrap.wrap(remainder, textwidth) # 25
    lines = lines[:strings]  # максимальное количество строк, не считая первой..

    #  can.drawString(405, 775, first_line)
    #  for n, l in enumerate(lines, 1):
    #      can.drawString(405, 773 - (n*15), l)
    return lines

def make_pdf(page_width, page_height,
             font_size, image, texts,
             start_x, start_y):
    
    page_size = (210 * mm, 297 * mm)
    canva = canvas.Canvas("helloworld.pdf", page_size)
    pdfmetrics.registerFont(TTFont("Arial", "ARIAL.TTF"))
    img = ImageReader(image)
    # for text in texts:
    canva.setFont("Arial", font_size)
    canva.setFillColor(white)
    canva.drawImage(img, 0, 0, 210 * mm, 296 * mm)
    canva.drawString(start_x, start_y, texts)
      
       # textlines=split_string(text, 25, 1)
       # print(textlines)
       # for n, l in enumerate(textlines,1):
       # print(texts)
       # canva.drawString(start_x, start_y, texts)

    canva.showPage()

    canva.save()
   

