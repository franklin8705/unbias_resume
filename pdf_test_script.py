from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
import os, json, sys

#Check current working directory
os.getcwd()

#Pull in the image to a canvas object
c=canvas.Canvas("new_sample.pdf")

#Draw the black image onto the target_pdf,
#position:
x1=100
y1=100
x_len=10
y_len=15
c.drawImage('black.png',x1,y1, x_len,y_len)

#Save pdf
c.save()

#Read in image file pdf
image_file=PdfFileReader(open("new_sample.pdf","rb"))

#Read in the primary pdf
primary_file=PdfFileReader(open("sample.pdf","rb"))

#Prepare the output file
output_file=PdfFileWriter()

#Get Page
primary_page=primary_file.getPage(0)
source_page=image_file.getPage(0)

##Merge Page
primary_page.mergePage(source_page)

#Output page
output_file.addPage(primary_page)

#Write to output pdf
with open("final_sample.pdf","wb") as output_stream:
    output_file.write(output_stream)