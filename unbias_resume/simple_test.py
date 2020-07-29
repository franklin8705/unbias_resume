import requests
import os
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm,inch
from reportlab.lib.pagesizes import A4,letter
from reportlab.platypus import Frame, Image

from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.textanalytics import TextAnalyticsClient
import pandas as pd, numpy as np
from utils import format_bounding_box,content_df

#****************************#
## Set up Azure Form Recognizer


#Resource variables (get from portal)
endpoint='https://unbiasresume.cognitiveservices.azure.com'
key= '60a7d355004e491bb60b4d32562bd5e3'

#Define client
form_recognizer_client = FormRecognizerClient(endpoint=endpoint,credential=AzureKeyCredential(key))

#****************************#
#Point to Data in Azure Blob
#define data urls
trainingDataUrl = "https://hackforthecultureblob.blob.core.windows.net/?sv=2019-12-12&ss=bfqt&srt=sco&sp=rwdlacupx&se=2020-07-29T04:29:19Z&st=2020-07-28T20:29:19Z&spr=https,http&sig=Z6YMfjTWBl1oXsubTqZkD1KAGXZs%2FVYAfsF3bELEyv0%3D"
formUrl_af="https://hackforthecultureblob.blob.core.windows.net/resumedemo/train/A Franklin Resume 2020.pdf"
formUrl = "https://hackforthecultureblob.blob.core.windows.net/resumedemo/train/Invoice_1.pdf"
receiptUrl = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-receipt.png"
#Call AFRS
poller = form_recognizer_client.begin_recognize_content_from_url(formUrl_af)
contents = poller.result()
testdf=content_df(contents)
testdf.head(10)

#***************************#


from azure.core.credentials import AzureKeyCredential

def authenticate_client():

    endpoint = "https://resumedemo.cognitiveservices.azure.com/"
    key = "5c7482cd4e03480ca132e113eab8c4f6"
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, credential=ta_credential)
    return text_analytics_client

def entity_recognition_example(client, documents):

    try:
       
        result = client.recognize_entities(documents = documents)[0]
        f= open("example.txt","w+")
        f.write("Named Entities:\n")
        for entity in result.entities:
            f.write("\tText: \t"+ str(entity.text)+ "\tCategory: \t" + str(entity.category)+ "\tSubCategory: \t"+ str(entity.subcategory)+
                    "\n")

    except Exception as err:
        print("Encountered exception. {}".format(err))
         
client = authenticate_client()

pdfFileObject = open('resume.pdf', 'rb')

pdfReader = PyPDF2.PdfFileReader(pdfFileObject)


pageObject = pdfReader.getPage(0)

documents  = [pageObject.extractText()]


entity_recognition_example(client, documents) 






pdfFileObject.close()

#****************************#
# Set up PDF Editor

#create blackout images pdf
c=canvas.Canvas("new_sample.pdf",pagesize=letter)
# c.translate()

#Draw the black image onto the target_pdf
#Note AFR: [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
#Note 72 pxl = 1 inch
#position:
element=5
testdf['box'][element]
height=abs(testdf['box'][element][2][1]-testdf['box'][element][1][1])
width=abs(testdf['box'][element][1][0]-testdf['box'][element][0][0])
x1=testdf['box'][element][3][0]
y1=testdf['box'][element][3][1]
x_len=width
y_len=height
x1
y1

offset_x=0
offset_y=11
c.drawImage('black.png',(x1)*inch,(offset_y-y1)*inch, x_len*inch,y_len*inch)#,preserveAspectRatio=True)
# c.drawImage('black.png',(1)*inch,(11-y_len-1)*inch, x_len*inch,y_len*inch)
# c.drawImage('black.png',(1)*inch,(offset_y-1)*inch, x_len*inch,y_len*inch)

#Save pdf
c.save()

#Read in image file pdf
image_file=PdfFileReader(open("new_sample.pdf","rb"))
image_file.getPage(0).mediaBox

#Read in the primary pdf
primary_file=PdfFileReader(open("A Franklin Resume 2020.pdf","rb"))
primary_file.getPage(0).mediaBox

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


