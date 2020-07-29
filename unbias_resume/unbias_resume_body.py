import requests
import os, re
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm,inch
from reportlab.lib.pagesizes import A4,letter
from reportlab.platypus import Frame, Image

from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.textanalytics import TextAnalyticsClient
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

import pandas as pd, numpy as np
from unbias_resume.utils import (format_bounding_box,content_df,
                                 authenticate_form_client,
                                 authenticate_text_client,
                                 entity_recognition_caller)

#****************************#
## Set up Azure Form Recognizer
#Define Form client
form_client=authenticate_form_client()

#***************************#
#Set up Text Analytics Client
text_client=authenticate_text_client()    

#****************************#
#Point to Data in Azure Blob
#get connection string from environment var
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

#define data urls
trainingDataUrl = "https://hackforthecultureblob.blob.core.windows.net/?sv=2019-12-12&ss=bfqt&srt=sco&sp=rwdlacupx&se=2020-07-29T04:29:19Z&st=2020-07-28T20:29:19Z&spr=https,http&sig=Z6YMfjTWBl1oXsubTqZkD1KAGXZs%2FVYAfsF3bELEyv0%3D"
formUrl_af="https://hackforthecultureblob.blob.core.windows.net/resumedemo/train/A Franklin Resume 2020.pdf"
formUrl_base = "https://hackforthecultureblob.blob.core.windows.net/resumedemo/train/"

# Point to local file in local data directory to upload and download
local_path = "./unbias_resume/temp_folder"
blob_path='train'
local_upload_file_name = "marked_file.pdf"
blob_download_file_name = "A Franklin Resume 2020.pdf"

# Upload the blob from local filepath and name
upload_file_path = os.path.join(local_path, local_upload_file_name)
upload_to_blob_path = os.path.join(blob_path,local_upload_file_name)

# Download the blob to a local filepath and name
download_file_path = os.path.join(local_path, local_download_file_name)
blob_file_path=os.path.join(blob_path, local_download_file_name)

# Create a blob client using the local file name as the name for the blob
upload_client = blob_service_client.get_blob_client(container='resumedemo', blob=upload_to_blob_path)
download_client = blob_service_client.get_blob_client(container='resumedemo', blob=blob_file_path)
#****************************#
##Download File
print("\nDownloading blob to \n\t" + download_file_path)

with open(download_file_path, "wb") as download_file:
    download_file.write(download_client.download_blob().readall())

#****************************#
#Call AFRS
poller = form_client.begin_recognize_content_from_url(formUrl_base+blob_download_file_name)
contents = poller.result()

#create dataframe
testdf=content_df(contents,text_client)
testdf[['text','category']].head(10)
# testdf.columns
    
#Filter to records with appropriate entities
entities_of_interest=["'person'","'url'","'email'"]
pattern = "|".join(re.escape(s) for s in entities_of_interest)
crexp = re.compile(f"({pattern})")
ind_list=[True if crexp.search(s.lower()) else False for s in testdf['category'] ]
ind_list
tempdf=testdf[ind_list]
tempdf.head()

#****************************#
# Set up PDF Editor

#create blackout images pdf
c=canvas.Canvas("./unbias_resume/temp_folder/new_sample.pdf",pagesize=letter)

#Draw the black image onto the target_pdf
#Note AFR: [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
#Note reportlab (0,0) is bottom left corner
#position:
offset_x=0
offset_y=11
#loop through text in pdf
for element in range(tempdf.shape[0]):
    # element=0
    temp_list=tempdf['box'].values
    temp_list[element]
    height=abs(temp_list[element][2][1]-temp_list[element][1][1])
    width=abs(temp_list[element][1][0]-temp_list[element][0][0])
    x1=temp_list[element][3][0]
    y1=temp_list[element][3][1]
    x_len=width
    y_len=height
    c.drawImage('./unbias_resume/black.png',(x1)*inch,(offset_y-y1)*inch, x_len*inch,y_len*inch)


#Save temp pdf
c.save()

#Read in image file pdf
image_file=PdfFileReader(open("./unbias_resume/temp_folder/new_sample.pdf","rb"))
image_file.getPage(0).mediaBox

#Read in the primary pdf
primary_file=PdfFileReader(open(download_file_path,"rb"))
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
with open("./unbias_resume/temp_folder/marked_file.pdf","wb") as output_stream:
    output_file.write(output_stream)
    

print("\nUploading to Azure Storage as blob:\n\t" + upload_file_path)
# Upload the created file
with open(upload_file_path, "rb") as data:
    upload_client.upload_blob(data)



