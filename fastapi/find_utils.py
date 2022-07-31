import os
import tensorflow as tf
import requests
import boto3
import pickle
import requests
import json
import numpy as np
from psycopg2 import sql
from transformers import BertTokenizer
from insert_to_db import Make_Connection


nlp_host=os.environ['nlp_host']
cv_host=os.environ['cv_host']
nlp_port=os.environ['nlp_port']
cv_port=os.environ['cv_port']


IMAGE_SIZE=[512,512]
MAX_LENGTH=180
BATCH_SIZE=32
CV_THRESHOLD=0.46
NLP_THRESHOLD=0.44
TITLE_EMBED_DIM=720
IMAGE_EMBED_DIM=720

def get_title_embeddings(titles):
    INPUT_IDS=np.zeros((len(titles),MAX_LENGTH),dtype=np.int32)
    ATTENTION_MASK=np.zeros((len(titles),MAX_LENGTH),dtype=np.int32)
    TOKEN_TYPE_IDS=np.zeros((len(titles),MAX_LENGTH),dtype=np.int32)
    TOKENIZER=BertTokenizer.from_pretrained("bert_tokenizer",do_lower_case=True)
    tokenized_title=TOKENIZER.batch_encode_plus(titles,padding="max_length",
                                            truncation="longest_first",max_length=MAX_LENGTH)
    INPUT_IDS[:,]=tokenized_title['input_ids']
    ATTENTION_MASK[:,]=tokenized_title['attention_mask']
    TOKEN_TYPE_IDS[:,]=tokenized_title['token_type_ids']
    instances=[]
    INPUT_IDS=INPUT_IDS.tolist()
    ATTENTION_MASK=ATTENTION_MASK.tolist()
    TOKEN_TYPE_IDS=TOKEN_TYPE_IDS.tolist()
    instances={"input_1":[],"input_2":[],"input_3":[]}
    for i in range(len(titles)):
        instances['input_1'].append(INPUT_IDS[i])
        instances['input_2'].append(ATTENTION_MASK[i])
        instances['input_3'].append(TOKEN_TYPE_IDS[i])
    url=f'http://{nlp_host}:{nlp_port}/v1/models/nlp:predict'
    data = json.dumps({"signature_name": "serving_default", "inputs": instances})
    headers = {"content-type": "application/json"}
    json_response = requests.post(url, data=data, headers=headers)
    return np.array(json.loads(json_response.text)['outputs'])


def get_image_embeddings(images):
    img=np.expand_dims(images,axis=0)
    img=img/255.0
    inputs={"input_1":img.tolist()}
    url=f'http://{cv_host}:{cv_port}/v1/models/cv:predict'
    data = json.dumps({"signature_name": "serving_default", "inputs": inputs})
    headers = {"content-type": "application/json"}
    json_response = requests.post(url, data=data, headers=headers)
    return np.array(json.loads(json_response.text)['outputs'])

def FIND_SIMILAR(title,image):
    knn_nlp_host=os.environ['knn_nlp_host']
    knn_nlp_port=os.environ['knn_nlp_port']
    knn_cv_host=os.environ['knn_cv_host']
    knn_cv_port=os.environ['knn_cv_port']
    title_embeds=get_title_embeddings([title]).tolist()
    img_embeds=get_image_embeddings(image).tolist()
    images_idx=[]
    title_idx=[]
    headers = {"content-type": "application/json"}
    data=json.dumps({"inputs":title_embeds})
    response=json.loads(requests.post(url=f"http://{knn_nlp_host}:{knn_nlp_port}/invocations",data=data,headers=headers).text)
    dis,indx=response
    dis,indx=np.array(dis)[0],np.array(indx)[0]
    close_dis_indx=np.where(dis<NLP_THRESHOLD)
    matched_post_idxs=indx[close_dis_indx]
    title_idx.extend(matched_post_idxs)
    ########################################################
    headers = {"content-type": "application/json"}
    data=json.dumps({"inputs":img_embeds})
    response=json.loads(requests.post(url=f"http://{knn_cv_host}:{knn_cv_port}/invocations",data=data,headers=headers).text)
    dis,indx=response
    dis,indx=np.array(dis)[0],np.array(indx)[0]
    close_dis_indx=np.where(dis<CV_THRESHOLD)
    matched_post_idxs=indx[close_dis_indx]
    images_idx.extend(matched_post_idxs)
    return list(set(title_idx).union(set(images_idx)))
    #return list(set(title_idx).intersection(set(images_idx)))

def get_post_names(idxs):
    conn,cursor=Make_Connection()
    q=sql.SQL("""
        select post_names
        from post_info
        where id in ({idxs})
        """).format(idxs=sql.SQL(",").join(sql.Placeholder()*len(idxs)))
    cursor.execute(q,(tuple([int(idx)+1 for idx in idxs])))
    data=cursor.fetchall()
    cursor.close()
    conn.close()
    return [d['post_names'] for d in data]

def get_images_from_s3(post_names):
    bucket_name=os.environ['BucketName']
    s3=boto3.resource("s3")
    bucket=s3.Bucket(bucket_name)
    images=[]
    titles=[]
    for name in post_names:
        data=bucket.Object(f"{name}.pkl").get()['Body'].read()
        loaded_data=pickle.loads(data)
        titles.append(loaded_data['title'])
        images.append(tf.io.decode_jpeg(loaded_data['image_bytes']).numpy().tolist())
    return {"titles":titles,"images":images}

def Retrive_post(title,image):
    idxs=FIND_SIMILAR(title,image)
    if len(idxs)==0:
        return {"titles":None,"images":None}
    else:
        post_names=get_post_names(idxs)
        return get_images_from_s3(post_names)
