import requests
import os
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
import pandas as pd, numpy as np

#Resource variables (get from portal)
endpoint='https://unbiasresume.cognitiveservices.azure.com'
key= '60a7d355004e491bb60b4d32562bd5e3'

#Define client
form_recognizer_client = FormRecognizerClient(endpoint=endpoint,credential=AzureKeyCredential(key))

#define data urls
trainingDataUrl = "https://hackforthecultureblob.blob.core.windows.net/?sv=2019-12-12&ss=bfqt&srt=sco&sp=rwdlacupx&se=2020-07-29T04:29:19Z&st=2020-07-28T20:29:19Z&spr=https,http&sig=Z6YMfjTWBl1oXsubTqZkD1KAGXZs%2FVYAfsF3bELEyv0%3D"
formUrl_af="https://hackforthecultureblob.blob.core.windows.net/resumedemo/train/A Franklin Resume 2020.pdf"
formUrl = "https://hackforthecultureblob.blob.core.windows.net/resumedemo/train/Invoice_1.pdf"
receiptUrl = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-receipt.png"

poller = form_recognizer_client.begin_recognize_content_from_url(formUrl)
contents = poller.result()

#helper function to output coordinates of the bounding box
def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["({}, {})".format(p.x, p.y) for p in bounding_box])



def content_df(contents):
    table_dict={}
    page_list=[]
    wordcount_list=[]
    id_list=[]
    text_list=[]
    box_list=[]
    height_list=[]
    width_list=[]
    for idx, content in enumerate(contents):
        for line_idx, line in enumerate(content.lines):
            #TODO finish id field
            id_list.append("-".join([str(idx),str(line_idx)]))
            page_list.append(idx)
            text_list.append(line.text)
            wordcount_list.append(len(line.words))
            box_list.append(eval("["+format_bounding_box(line.bounding_box)+"]"))
            
    table_dict['id']=id_list
    table_dict['page']=page_list
    table_dict['text']=text_list
    table_dict['box']=box_list
    return pd.DataFrame(table_dict)


        
testdf=content_df(contents)       
testdf.head()

#checkout box
testdf['box'][0]
type(testdf['box'][0])
#Note: [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
height=abs(testdf['box'][0][2][1]-testdf['box'][0][0][1])
width=abs(testdf['box'][0][1][0]-testdf['box'][0][0][0])
height
width











# for idx, content in enumerate(contents):
#     print("----Recognizing content from page #{}----".format(idx))
#     print("Has width: {} and height: {}, measured with unit: {}".format(
#         content.width,
#         content.height,
#         content.unit
#     ))
#     for table_idx, table in enumerate(content.tables):
#         print("Table # {} has {} rows and {} columns".format(table_idx, table.row_count, table.column_count))
#         for cell in table.cells:
#             print("...Cell[{}][{}] has text '{}' within bounding box '{}'".format(
#                 cell.row_index,
#                 cell.column_index,
#                 cell.text,
#                 format_bounding_box(cell.bounding_box)
#             ))
#     for line_idx, line in enumerate(content.lines):
#         print("Line # {} has word count '{}' and text '{}' within bounding box '{}'".format(
#             line_idx,
#             len(line.words),
#             line.text,
#             format_bounding_box(line.bounding_box)
#         ))
#     print("----------------------------------------")
