#****************************#
import pandas as pd, numpy as np

#helper function to output coordinates of the bounding box
def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["({}, {})".format(p.x, p.y) for p in bounding_box])

#Create a pandas dataframe with the AFRS output
def content_df(contents):
    table_dict={}
    page_list=[]
    pagewth_list=[]
    pageht_list=[]
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
            pageht_list.append(content.height)
            pagewth_list.append(content.width)
            page_list.append(idx)
            text_list.append(line.text)
            wordcount_list.append(len(line.words))
            box_list.append(eval("["+format_bounding_box(line.bounding_box)+"]"))
            
    table_dict['id']=id_list
    table_dict['page_width']=pagewth_list
    table_dict['page_height']=pageht_list
    table_dict['page']=page_list
    table_dict['text']=text_list
    table_dict['box']=box_list
    return pd.DataFrame(table_dict)


