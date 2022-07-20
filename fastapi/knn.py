import numpy as np
from sklearn.neighbors import NearestNeighbors
import mlflow
import mlflow.sklearn
from tqdm import tqdm
from find_utils import get_image_embeddings,get_title_embeddings
import pandas as pd
import boto3
import os


bucket_name=os.environ['BucketName']

class Model(NearestNeighbors):
    def __init__(self):
        super().__init__(n_neighbors=2,metric="cosine")
    def predict(self,data):
        return self.kneighbors(data)


def train_knn(df):
    total=16
    df['image_path']=df['image'].apply(lambda x: f"train_images/{x}")
    Image_Embeddings=np.zeros((total,720))
    Title_Embeddings=np.zeros((total,720))
    batch_size=8
    n_iters=int(np.ceil(total/batch_size))
    for i in tqdm(range(n_iters)):
        paths=df.iloc[i*batch_size:(i+1)*batch_size]["image_path"].values
        titles=df.iloc[i*batch_size:(i+1)*batch_size]["title"].values
        Image_Embeddings[i*batch_size:(i+1)*batch_size,]=get_image_embeddings(paths)
        Title_Embeddings[i*batch_size:(i+1)*batch_size,]=get_title_embeddings(titles)
    knn=Model()
    knn.fit(Image_Embeddings)
    mlflow.sklearn.log_model(knn, "image_knn")
    del knn,Image_Embeddings
    import gc
    gc.collect()
    knn=Model()
    knn.fit(Title_Embeddings)
    mlflow.sklearn.log_model(knn, "title_knn")
    del knn,Title_Embeddings
    import gc
    gc.collect()


if __name__=="__main__":
    df=pd.read_csv("train.csv")
    train_knn(df)
    #aws s3 cp mlruns s3://shop-duplicate-bucket/ --recursive