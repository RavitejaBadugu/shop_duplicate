"""
This file creates the group kfold split to the data. 
And applies label Encoder to the target Feature.
"""
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GroupKFold
from utils.randomness import *
import argparse
import pickle
import pathlib

def CREATE_FOLD(args):
  df=pd.read_csv(args.data_path)
  encoder=LabelEncoder()
  df['label_group']=encoder.fit_transform(df['label_group'])
  print("label encoding is done")
  if not os.path.isdir("encoders"):
    os.mkdir("encoders")
  with open("encoders/label_group_encoder.pkl","wb") as f:
    pickle.dump(encoder,f)
  df['gfold']=-1
  gfold=GroupKFold(n_splits=5)
  for i,(train,test) in enumerate(gfold.split(df,groups=df['label_group'])):
    df.loc[test,'gfold']=i
  print("created the group kfold")
  if not os.path.isdir("processed_data"):
    os.mkdir("processed_data")
    print("created processed_data directory")
  df.to_csv("processed_data/fold_data.csv",index=False)
  print("group kfold data is stored at processed_data/fold_data.csv")
if __name__=="__main__":
  set_randomness()
  parser=argparse.ArgumentParser(description="create folds")
  parser.add_argument("--data_path",help="path to the data file", type=pathlib.Path,required = True)
  args=parser.parse_args()
  CREATE_FOLD(args)
