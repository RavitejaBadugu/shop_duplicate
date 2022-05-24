"""
Data loaders for the models

"""
import albumentations as A
import tensorflow as tf
import numpy as np
from transformers import BertTokenizer

class IMG_DATA_LOADER(tf.keras.utils.Sequence):
  def __init__(self,dataframe,image_size,batch_size,aug,shuffle,inference=False):
    self.data=dataframe
    self.batch_size=batch_size
    self.shuffle=shuffle
    self.image_size=image_size
    self.aug=aug
    self.inference=inference
    self.n=0
    self.max_=self.__len__()
    self.indexes=np.arange(self.data.shape[0])
    self.temp_indexes=np.arange(self.data.shape[0])
    if not self.inference:
      self.on_epoch_end()

  def __len__(self):
    return int(np.ceil(self.data.shape[0]/self.batch_size))
  
  def on_epoch_end(self):
    if self.shuffle:
      np.random.shuffle(self.temp_indexes)
  
  def next(self):
    if self.n>self.max_:
      self.n=0
      result=self.__getitem__(self.n)
      self.n+=1
    else:
      result=self.__getitem__(self.n)
      self.n+=1
    return result
  
  def Augment_images(self,image):
    transformer=A.Compose([A.Rotate(limit=30,p=0.8),
          A.HorizontalFlip(),
          #A.CoarseDropout(max_height=0.25,max_width=0.25,),
          A.ShiftScaleRotate(shift_limit=0.09,scale_limit=0.2,rotate_limit=0),
          A.RandomBrightnessContrast()
          ])
    image=transformer(image=image)['image']
    return image

  def __getitem__(self,batch):
    curr_temp_indexes=self.temp_indexes[batch*self.batch_size:(batch+1)*self.batch_size]
    curr_batch=list(self.indexes[i] for i in curr_temp_indexes)
    IMAGES=np.zeros((len(curr_batch),self.image_size[0],self.image_size[1],3))
    if not self.inference:
      Y=np.zeros((len(curr_batch),))      
    for i,idx in enumerate(curr_batch):
      img_name=self.data.iloc[idx]['image_path']
      labels=self.data.iloc[idx]['label_group']
      img=tf.keras.preprocessing.image.load_img(img_name,target_size=self.image_size)
      img=tf.keras.preprocessing.image.img_to_array(img)/255.0
      if self.aug:
        img=self.Augment_images(img)
      IMAGES[i,]=img
      if not self.inference:
        Y[i,]=labels
    if not self.inference:
      return (IMAGES,Y),Y
    else:
      return IMAGES


class TEXT_DATA_LOADER(tf.keras.utils.Sequence):
  def __init__(self,dataframe,max_length,pre_trained_name,batch_size,shuffle,inference=False):
    self.data=dataframe
    self.batch_size=batch_size
    self.shuffle=shuffle
    self.max_length=max_length
    self.pre_trained_name=pre_trained_name
    self.inference=inference
    self.tokenizer=BertTokenizer.from_pretrained(self.pre_trained_name)
    self.n=0
    self.max_=self.__len__()
    self.indexes=np.arange(self.data.shape[0])
    self.temp_indexes=np.arange(self.data.shape[0])
    if not self.inference:
      self.on_epoch_end()

  def __len__(self):
    return int(np.ceil(self.data.shape[0]/self.batch_size))
  
  def on_epoch_end(self):
    if self.shuffle:
      np.random.shuffle(self.temp_indexes)
  
  def next(self):
    if self.n>self.max_:
      self.n=0
      result=self.__getitem__(self.n)
      self.n+=1
    else:
      result=self.__getitem__(self.n)
      self.n+=1
    return result
  
  def __getitem__(self,batch):
    curr_temp_indexes=self.temp_indexes[batch*self.batch_size:(batch+1)*self.batch_size]
    curr_batch=list(self.indexes[i] for i in curr_temp_indexes)
    INPUT_IDS=np.zeros((len(curr_batch),self.max_length),dtype=np.int32)
    ATTENTION_MASK=np.zeros((len(curr_batch),self.max_length),dtype=np.int32)
    TOKEN_TYPE_IDS=np.zeros((len(curr_batch),self.max_length),dtype=np.int32)
    if not self.inference:
      Y=np.zeros((len(curr_batch),))
    for i,idx in enumerate(curr_batch):
      title=self.data.iloc[idx]['title']
      labels=self.data.iloc[idx]['label_group']
      tokenized_title=self.tokenizer.encode_plus(title,padding="max_length",
                                                truncation="longest_first",max_length=self.max_length)
      
      INPUT_IDS[i,]=tokenized_title['input_ids']
      ATTENTION_MASK[i,]=tokenized_title['attention_mask']
      TOKEN_TYPE_IDS[i,]=tokenized_title['token_type_ids']
      if not self.inference:
        Y[i,]=labels
    if not self.inference:
      return ({"input_ids":INPUT_IDS,"attention_mask":ATTENTION_MASK,
              "token_type_ids": TOKEN_TYPE_IDS},Y),Y
    else:
      return {"input_ids":INPUT_IDS,"attention_mask":ATTENTION_MASK,
              "token_type_ids": TOKEN_TYPE_IDS}

class BOTH_DATA_LOADER(tf.keras.utils.Sequence):
  def __init__(self,dataframe,image_size,batch_size,max_length,text_pre_trained_name,aug,shuffle,inference=False):
    self.data=dataframe
    self.batch_size=batch_size
    self.shuffle=shuffle
    self.inference=inference
    self.image_size=image_size
    self.aug=aug
    self.max_length=max_length
    self.pre_trained_name=text_pre_trained_name
    self.tokenizer=BertTokenizer.from_pretrained(self.pre_trained_name)
    self.n=0
    self.max_=self.__len__()
    self.indexes=np.arange(self.data.shape[0])
    self.temp_indexes=np.arange(self.data.shape[0])
    if not self.inference:
      self.on_epoch_end()

  def __len__(self):
    return int(np.ceil(self.data.shape[0]/self.batch_size))
  
  def on_epoch_end(self):
    if self.shuffle:
      np.random.shuffle(self.temp_indexes)
  
  def next(self):
    if self.n>self.max_:
      self.n=0
      result=self.__getitem__(self.n)
      self.n+=1
    else:
      result=self.__getitem__(self.n)
      self.n+=1
    return result
  
  def Augment_images(self,image):
    transformer=A.Compose([A.Rotate(limit=30,p=0.8),
          A.HorizontalFlip(),
          #A.CoarseDropout(max_height=0.25,max_width=0.25,),
          A.ShiftScaleRotate(shift_limit=0.09,scale_limit=0.2,rotate_limit=0),
          A.RandomBrightnessContrast()
          ])
    image=transformer(image=image)['image']
    return image

  def __getitem__(self,batch):
    curr_temp_indexes=self.temp_indexes[batch*self.batch_size:(batch+1)*self.batch_size]
    curr_batch=list(self.indexes[i] for i in curr_temp_indexes)
    IMAGES=np.zeros((len(curr_batch),self.image_size[0],self.image_size[1],3))
    INPUT_IDS=np.zeros((len(curr_batch),self.max_length),dtype=np.int32)
    ATTENTION_MASK=np.zeros((len(curr_batch),self.max_length),dtype=np.int32)
    TOKEN_TYPE_IDS=np.zeros((len(curr_batch),self.max_length),dtype=np.int32)
    if not self.inference:
      Y=np.zeros((len(curr_batch),))
    for i,idx in enumerate(curr_batch):
      img_name=self.data.iloc[idx]['image_path']
      labels=self.data.iloc[idx]['label_group']
      img=tf.keras.preprocessing.image.load_img(img_name,target_size=self.image_size)
      img=tf.keras.preprocessing.image.img_to_array(img)/255.0
      if self.aug:
        img=self.Augment_images(img)
      IMAGES[i,]=img
      #############################
      title=self.data.iloc[idx]['title']
      tokenized_title=self.tokenizer.encode_plus(title,padding="max_length",
                                                truncation="longest_first",max_length=self.max_length)
      
      INPUT_IDS[i,]=tokenized_title['input_ids']
      ATTENTION_MASK[i,]=tokenized_title['attention_mask']
      TOKEN_TYPE_IDS[i,]=tokenized_title['token_type_ids']
      if not self.inference:
        Y[i,]=labels
    if not self.inference:
      return ({"input_ids":INPUT_IDS,"attention_mask":ATTENTION_MASK,
            "token_type_ids": TOKEN_TYPE_IDS},IMAGES,Y),Y
    else:
      return ({"input_ids":INPUT_IDS,"attention_mask":ATTENTION_MASK,
            "token_type_ids": TOKEN_TYPE_IDS},IMAGES)
