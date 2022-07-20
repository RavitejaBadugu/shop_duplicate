import os
import requests
import numpy as np
import streamlit as st
import tensorflow as tf

host=os.environ['host']
port=os.environ['port']

st.write('''
In this page please provide your post title and image both are requried. Then press find button.
Then, we will show you the similar posts we have.
''')

title=st.text_area(label="enter the title of the post")
image=st.file_uploader(label="upload the image",type=['png', 'jpg'],accept_multiple_files=False)

find_me=st.button("find")

if find_me:
    if title!="" and image is not None:
        with st.spinner("we are processing"):
            img_list=np.frombuffer(image.read(),dtype=np.uint8).tolist()
            fastapi_data={"title": title,"image":img_list}
            response=requests.post("http://{host}:{port}/find",json=fastapi_data,headers={"Content-Type":"application/json"})
            response=response.json()
        titles=response['titles']
        images=response['images']
        if titles is not None and images is not None:
            images=list(tf.reshape(img,(512,512,3)) for img in images)
            st.image(images, use_column_width=True, caption=titles)
        else:
            st.error("We faced a issue internally. Sorry 😢")
        
    else:
        if title!="":
            st.error('please upload the image')
        else:
            st.error('please enter the text')