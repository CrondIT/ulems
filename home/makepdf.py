from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from reportlab.lib.colors import white
from reportlab.lib.styles import ParagraphStyle


import textwrap as textwrap
import csv

# cyrillic font
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# load data from csv file
# default path = data.csv
def load_data(path):
    data = []
    with open(path) as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append({"Prefix": row["Prefix"],
                         "Surname": row["Surname"],
                         "Name": row["Name"],
                         "MiddleName": row["MiddleName"],
                         "Category": row["Category"],
                         "Competence": row["Competence"],
                         "Award": row["Award"],
                         "CreationDate": row["CreationDate"],
                         "Creator": row["Creator"],
                         "ChangeDate": row["ChangeDate"],
                         "ChangedBy": row["ChangedBy"]})
    return data

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

def main():
    pagesize=(210 * mm, 297 * mm)
    c = canvas.Canvas("helloworld.pdf", pagesize)
    pdfmetrics.registerFont(TTFont("Arial", "ARIAL.TTF"))


    data = load_data("data.csv")

    img = ImageReader("d1.png")
    # Get the width and height of the image.
    img_w, img_h = img.getSize()
    # h - img_h is the height of the sheet minus the height
    # of the image.



    for  participant in data:
        c.setFont("Arial", 18)
        c.setFillColor(white)
        c.drawImage(img, 0, 0, 210 * mm, 297 * mm)
        fio = participant["Surname"] + " " + participant["Name"] + " " + participant["MiddleName"]
        c.drawString(60, 510, fio)
        # c.drawString(60, 380, participant["Competence"])

        textlines=split_string(participant["Competence"], 25, 2)
        print(textlines)
        for n, l in enumerate(textlines,1):
            print(l)
            c.drawString(60, 380-(n*40),l)

        c.showPage()

    c.save()
    print("End")


if __name__ == "__main__":
    main()
