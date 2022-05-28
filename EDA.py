"""
The EDA and Cleaning the data.
"""
import numpy as np
import argparse
import pandas as pd
import pathlib
import os
import matplotlib.pyplot as plt
import matplotlib.image as implt


def Visualize(df):
  paths=np.random.choice(df['image_path'].values,size=32,replace=False)
  plt.subplots(8,4,figsize=(30,30))
  for i,path in enumerate(paths):
    plt.subplot(8,4,i+1)
    img=implt.imread(path)
    plt.imshow(img)
  plt.savefig
  if not os.path.isdir("plots"):
    os.mkdir("plots")
  plt.savefig("plots/random_images.jpg")
  if args.check_sizes:
    print("checking height distributions")
    df['height']=df['image_path'].apply(lambda x: implt.imread(path).shape[0])
    df['width']=df['image_path'].apply(lambda x: implt.imread(path).shape[1])
    plt.figure(figsize=(15,10))
    plt.hist(df['height'])
    plt.title("height distributions")
    plt.savefig("plots/height_distributions.jpg")
    print("checking weigth distributions")
    plt.figure(figsize=(15,10))
    plt.hist(df['width'])
    plt.title("weidth distributions")
    plt.savefig("plots/weigth_distributions.jpg")
  

if __name__=="__main__":
  parser=argparse.ArgumentParser(description="EDA and cleaning")
  parser.add_argument("--data_path",help="path to the data file", type=pathlib.Path,required = True)
  parser.add_argument("--images_base_path",help="path to the images", type=pathlib.Path,required = True)
  parser.add_argument("--check_sizes",help="whether to check the distributions of height and width of images", 
                      type=bool)
  args=parser.parse_args()
  df=pd.read_csv(args.data_path)
  df['image_path']=df['image_path']=df['image'].apply(lambda x: os.path.join(args.images_base_path,x))
  if not os.path.isdir("processed_data"):
    os.mkdir("processed_data")
  df.to_csv("processed_data/cleaned_data.csv",index=False)
  Visualize(df)
