from fastapi import FastAPI,UploadFile,File
from find_utils import Retrive_post
import cv2
import numpy as np
from fastapi.responses import JSONResponse
app=FastAPI()

@app.get("/ping")
async def Welcome():
    return {"msg":"working"}

@app.post("/find")
async def FIND_ME(title: str,file: UploadFile = File(...)):
    img=np.frombuffer(file.file.read(),dtype=np.uint8)
    img=cv2.cvtColor(cv2.imdecode(img,flags=1),cv2.COLOR_BGR2RGB)
    img=cv2.resize(img,(512,512))
    output=Retrive_post(title,img)
    return JSONResponse(output)
