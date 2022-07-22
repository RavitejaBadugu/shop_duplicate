import os
import requests
import cv2
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

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
            response=requests.post(f"http://{host}:{port}/find",files={"file":image.read()},params={'title':title})
            data=response.json()
        titles=data['titles']
        images=data['images']
        if titles is not None and images is not None:
            images=[cv2.cvtColor(np.array(img,dtype=np.uint8),cv2.COLOR_BGR2RGB) for img in images]
        else:
            st.success("We don't have such duplicate")
        if titles is not None:
            if len(titles)>1:
                st.success(f"we found {len(titles)} duplicates. Below are few duplicates")
                st.image(images, use_column_width=True, caption=titles)
            else:
                st.success(f"we found {len(titles)} duplicate")
                st.image(images, use_column_width=True, caption=titles)
    else:
        if title!="":
            st.error('please upload the image')
        else:
            st.error('please enter the text')