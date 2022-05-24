"""
Below we have models for image, text and combined models and arcface layer

"""
import math
import tensorflow as tf
from tensorflow.keras.layers import Dense,Input,Layer
from tensorflow.keras.models import Model
from tensorflow.keras.applications import EfficientNetB4
from transformers import TFBertModel,TFRobertaModel,TFAlbertModel,TFXLNetModel


class ARCFACE_LAYER(Layer):
  def __init__(self,m=0.5,s=60,n_classes=11014):
    super(ARCFACE_LAYER,self).__init__()
    self.m=m
    self.s=s
    self.sin_m=tf.sin(m)
    self.cos_m=tf.cos(m)
    self.n_classes=n_classes
    self.threshold = tf.cos(math.pi - m)
    self.mm = tf.math.sin(math.pi - m) * m
  
  def build(self,input_shape):
    prev_layer_units=input_shape[0][1]
    self.w=self.add_weight(shape=(prev_layer_units,self.n_classes),trainable=True)

  def get_config(self):
    config=super().get_config()
    config.update({"m":0.5,
                   "s":60,
                   "n_classes":11014})
    return config


  def call(self,inputs):
    prev_layer,y=inputs
    y=tf.cast(y,dtype=tf.int32)
    y_hot=tf.one_hot(y,self.n_classes)
    y_hot=tf.cast(y_hot,dtype=tf.float32)
    w_norm=tf.linalg.l2_normalize(self.w,axis=0)
    x_norm=tf.linalg.l2_normalize(prev_layer,axis=1)
    cos_theta=tf.linalg.matmul(x_norm,w_norm)
    cos_theta=tf.keras.backend.clip(cos_theta,-1+1e-5,1-1e-5)
    sin_theta=tf.sqrt(1-tf.pow(cos_theta,tf.cast(2,dtype=tf.float32)))
    cos_theta_m=(cos_theta*self.cos_m)-(sin_theta*self.sin_m)
    cos_theta_m=tf.where(cos_theta_m>self.cos_m,cos_theta_m,cos_theta-self.mm)
    final=self.s*((y_hot*cos_theta_m)+((1-y_hot)*cos_theta))
    return final
  


def IMAGE_MODEL(image_size,unfreeze_layers_number):
  tf.keras.backend.clear_session()
  pre_trained=EfficientNetB4(include_top=False,weights="imagenet",input_shape=(image_size[0],image_size[1],3))
  ins=Input((),name="label_input")
  for i,layer in enumerate(pre_trained.layers):
    if i>=unfreeze_layers_number:
      if not layer.name.endswith("bn"):
        pre_trained.layers[i].trainable=True
      else:
        pre_trained.layers[i].trainable=False
    else:
      pre_trained.layers[i].trainable=False
  x=pre_trained.layers[-1].output
  x=tf.keras.layers.GlobalMaxPooling2D()(x)
  x=Dense(512)(x)
  arc_layer=ARCFACE_LAYER()
  x=arc_layer([x,ins])
  outs=tf.keras.layers.Softmax()(x)
  model=Model(inputs=(pre_trained.input,ins),outputs=outs)
  return model

def TEXT_MODEL(pre_trained_name,max_length):
  tf.keras.backend.clear_session()
  input_ids=Input((max_length,),dtype=tf.int32)
  attention_mask=Input((max_length,),dtype=tf.int32)
  token_type_ids=Input((max_length,),dtype=tf.int32)
  ins=Input((),name="label_input")
  pre_trained=TFBertModel.from_pretrained(pre_trained_name,output_hidden_states=True)
  pre_outputs=pre_trained({"input_ids":input_ids,"attention_mask":attention_mask,
                  "token_type_ids":token_type_ids})
  hidden_layers=[]
  for i in range(4):
    hidden_layers.append(pre_outputs['hidden_states'][-i])
  x=tf.keras.layers.Concatenate()(hidden_layers)[:,0,:]
  x=Dense(512)(x)
  arc_layer=ARCFACE_LAYER()
  x=arc_layer([x,ins])
  outs=tf.keras.layers.Softmax()(x)
  model=Model(inputs=({"input_ids":input_ids,"attention_mask":attention_mask,
                 "token_type_ids":token_type_ids},ins),outputs=outs)
  return model

def COMBINE_MODEL(max_length,image_size,unfreeze_layers_number):
  tf.keras.backend.clear_session()
  input_ids=Input((max_length,),dtype=tf.int32)
  attention_mask=Input((max_length,),dtype=tf.int32)
  token_type_ids=Input((max_length,),dtype=tf.int32)
  ins=Input((),name="label_input")
  text_trained=TFBertModel.from_pretrained("bert-base-uncased",output_hidden_states=True)
  text_outputs=text_trained({"input_ids":input_ids,"attention_mask":attention_mask,
                  "token_type_ids":token_type_ids})
  hidden_layers=[]
  for i in range(4):
    hidden_layers.append(text_outputs['hidden_states'][-i])
  x1=tf.keras.layers.Concatenate()(hidden_layers)[:,0,:]
  ################
  img_trained=DenseNet201(include_top=False,weights="imagenet",input_shape=(image_size[0],image_size[1],3))
  for i,layer in enumerate(img_trained.layers):
    if i>=unfreeze_layers_number:
      if not layer.name.endswith("bn"):
        img_trained.layers[i].trainable=True
      else:
        img_trained.layers[i].trainable=False
    else:
      img_trained.layers[i].trainable=False
  x2=img_trained.layers[-1].output
  x2=tf.keras.layers.GlobalMaxPooling2D()(x2)
  ################
  x=tf.keras.layers.Concatenate()([x1,x2])
  x=Dense(512)(x)
  arc_layer=ARCFACE_LAYER()
  x=arc_layer([x,ins])
  outs=tf.keras.layers.Softmax()(x)
  model=Model(inputs=({"input_ids":input_ids,"attention_mask":attention_mask,
                 "token_type_ids":token_type_ids},
                 img_trained.input,ins),outputs=outs)
  return model
