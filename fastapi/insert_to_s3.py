import tensorflow as tf
from tqdm import tqdm
import cv2
import boto3
import os
import pandas as pd
import pickle
bucket_name=os.environ['BucketName']

def conversion(dataframe):
    s3=boto3.client("s3")
    dataframe['image_path']=dataframe['image'].apply(lambda x: f"train_images/{x}")
    for i in tqdm(range(dataframe.shape[0])):
        title=dataframe.loc[i,"title"]
        posting_id=dataframe.loc[i,"posting_id"]
        image=dataframe.loc[i,"image_path"]
        post={}
        post['title']=title
        img=tf.keras.preprocessing.image.load_img(image,target_size=(512,512))
        img=tf.keras.preprocessing.image.img_to_array(img)
        img=cv2.imencode('.jpg', img, (cv2.IMWRITE_JPEG_QUALITY, 94))[1].tostring()
        post['image_bytes']=img
        with open(f"{posting_id}.pkl","wb") as f:
            pickle.dump(post,f)
        with open(f"{posting_id}.pkl","rb") as f:
            s3.upload_fileobj(f,bucket_name,f"{posting_id}.pkl")
        os.remove(f"{posting_id}.pkl")


if __name__=="__main__":
    df=pd.read_csv("train.csv")
    conversion(df)

    