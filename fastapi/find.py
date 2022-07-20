from fastapi import FastAPI
from base_models import Find_Input_Schema,Find_Output_Schema
from find_utils import Retrive_post

app=FastAPI()

@app.post("/find",response_model=Find_Output_Schema)
async def FIND_ME(input_data: Find_Input_Schema):
    data=input_data.dict()
    title,image=data['title'],data['image']
    output=Retrive_post(title,image)
    if output is not None:    
        titles,images=output
    else:
        titles,images=None,None
    return {"titles":titles,"images":images}
    