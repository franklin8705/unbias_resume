#****************************#
#Import packages
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


def authenticate_form_client():
    #Resource variables (get from portal)
    endpoint='https://unbiasresume.cognitiveservices.azure.com'
    key= '60a7d355004e491bb60b4d32562bd5e3'
    form_credential = AzureKeyCredential(key)
    form_recognizer_client = FormRecognizerClient(
        endpoint=endpoint,credential=form_credential)
    return form_recognizer_client


def authenticate_text_client():
    endpoint = "https://resumedemo.cognitiveservices.azure.com/"
    key = "5c7482cd4e03480ca132e113eab8c4f6"
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, credential=ta_credential)
    return text_analytics_client


def entity_recognition_caller(client, text):
    category_list=[]
    result = client.recognize_entities(documents = text)[0]
    for entity in result.entities:
        category_list.append(str(entity.category))
    return str(category_list)


#helper function to output coordinates of the bounding box
def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["({}, {})".format(p.x, p.y) for p in bounding_box])


#Create a pandas dataframe with the AFRS output
def content_df(contents,ta_client):
    table_dict={}
    page_list=[]
    pagewth_list=[]
    pageht_list=[]
    wordcount_list=[]
    id_list=[]
    text_list=[]
    box_list=[]
    category_list=[]
    for idx, content in enumerate(contents):
        for line_idx, line in enumerate(content.lines):
            #TODO finish id field
            id_list.append("-".join([str(idx),str(line_idx)]))
            pageht_list.append(content.height)
            pagewth_list.append(content.width)
            page_list.append(idx)
            text_list.append(line.text)
            wordcount_list.append(len(line.words))
            box_list.append(eval("["+format_bounding_box(line.bounding_box)+"]"))
            #Call Text Analytics
            category_list.append(entity_recognition_caller(ta_client,[line.text]))
            
    table_dict['id']=id_list
    table_dict['page_width']=pagewth_list
    table_dict['page_height']=pageht_list
    table_dict['page']=page_list
    table_dict['text']=text_list
    table_dict['box']=box_list
    table_dict['category']=category_list
    return pd.DataFrame(table_dict)


