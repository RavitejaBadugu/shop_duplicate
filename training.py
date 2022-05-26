"""
It is the training function for different types of models

"""

import argparse
import pathlib
from tabnanny import verbose
import pandas as pd
import tensorflow as tf
from utils.models import *
from utils.randomness import *
from utils.dataloaders import *
from params import HYPERPARAMETERS


def CE(y_true,y_pred):
  '''
  loss function = y*log(y_hat)
  '''
  y_true=tf.cast(y_true,dtype=tf.int32)
  y_true=tf.one_hot(y_true,depth=11014)
  y_true=tf.cast(y_true,dtype=y_pred.dtype)
  ce_loss=y_true*tf.keras.backend.log(y_pred+1e-5)
  batch_loss=tf.reduce_sum(ce_loss,axis=-1)
  return -1*tf.reduce_mean(batch_loss)

def one_cycle(epoch,lr_min=1e-5,lr_max=2e-4):
  if epoch<5:
    lr=(lr_max-lr_min)/5 *(epoch) + lr_min
  elif epoch==5:
    lr=lr_max
  else:
    lr= (lr_max-lr_min) * 0.8**(epoch-5) +lr_min
  return lr

def TRAINING(args):
  df=pd.read_csv(args.data_path)
  for fold in range(5):
    train_data=df.loc[df['gfold']!=fold].drop("gfold",axis=1).reset_index(drop=True)
    test_data=df.loc[df['gfold']==fold].drop("gfold",axis=1).reset_index(drop=True)

    if args.model_type=="image":
      tf.keras.backend.clear_session()
      model=IMAGE_MODEL(image_size=HYPERPARAMETERS["image"]["image_size"],unfreeze_layers_number=HYPERPARAMETERS["image"]['unfreeze'])
      train_dataloader=IMG_DATA_LOADER(dataframe=train_data,image_size=HYPERPARAMETERS["image"]['image_size'],
                                       batch_size=args.batch_size,aug=True,shuffle=True)
      test_dataloader=IMG_DATA_LOADER(dataframe=test_data,image_size=HYPERPARAMETERS["image"]['image_size'],
                                      batch_size=args.batch_size,aug=False,shuffle=False)

    elif args.model_type=="text":
      tf.keras.backend.clear_session()
      model=TEXT_MODEL(pre_trained_name=HYPERPARAMETERS["text"]["pre_trained_name"],max_length=HYPERPARAMETERS["text"]["max_length"])
      train_dataloader=TEXT_DATA_LOADER(dataframe=train_data,max_length=HYPERPARAMETERS["text"]["max_length"],
                                        pre_trained_name=HYPERPARAMETERS["text"]["pre_trained_name"],batch_size=args.batch_size,shuffle=True)
      test_dataloader=TEXT_DATA_LOADER(dataframe=test_data,max_length=HYPERPARAMETERS["text"]["max_length"],
                                       pre_trained_name=HYPERPARAMETERS["text"]["pre_trained_name"],batch_size=args.batch_size,shuffle=False)

    else:
      tf.keras.backend.clear_session()
      model=COMBINE_MODEL(max_length=HYPERPARAMETERS["text"]["max_length"],image_size=HYPERPARAMETERS["image"]["image_size"],
                          unfreeze_layers_number=HYPERPARAMETERS["image"]['unfreeze'])
      train_dataloader=BOTH_DATA_LOADER(dataframe=train_data,batch_size=args.batch_size,
                                        image_size=HYPERPARAMETERS["image"]['image_size'],
                                        max_length=HYPERPARAMETERS["text"]["max_length"],
                                        text_pre_trained_name=HYPERPARAMETERS["text"]["pre_trained_name"],aug=True,shuffle=True)
      test_dataloader=BOTH_DATA_LOADER(dataframe=test_data,batch_size=args.batch_size,
                                       image_size=HYPERPARAMETERS["image"]['image_size'],
                                       max_length=HYPERPARAMETERS["text"]["max_length"],
                                       text_pre_trained_name=HYPERPARAMETERS["text"]["pre_trained_name"],aug=False,shuffle=False)
      
    #model.compile("Adam",loss=CE)
    if args.model_type=="text":
      model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=3e-5),
                    loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                    metrics=[tf.keras.metrics.SparseCategoricalAccuracy()])
    else:
      model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
                    loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                    metrics=[tf.keras.metrics.SparseCategoricalAccuracy()])
    up_down=tf.keras.callbacks.LearningRateScheduler(lambda epoch: one_cycle(epoch),verbose=1)
    reduce_plat=tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss",mode="min",
                                                    patience=5,verbose=1,cooldown=2,
                                                    min_lr=1e-6)
    early=tf.keras.callbacks.EarlyStopping(monitor="val_loss",mode="min",verbose=1,patience=10)
    saver=tf.keras.callbacks.ModelCheckpoint(filepath=args.save_model_path+f"{fold}.h5",
                                             monitor="val_loss",mode="min",save_best_only=True,
                                             save_weights_only=True,verbose=1)
    if fold==0:
      print(model.summary())
    model.fit(train_dataloader,validation_data=test_dataloader,epochs=args.epochs,
              callbacks=[early,saver,up_down] if args.lr_callback=="one_cycle" \
                         else [early,saver,reduce_plat] if args.lr_callback=="reduce_lr_plateau" \
              else [early,saver]
              )
    
    print(f"model training for {fold} is done")
    del model
    import gc
    gc.collect()
  

if __name__=="__main__":
  parser=argparse.ArgumentParser(description="training the models")
  parser.add_argument("--data_path",help="path to the data file", type=pathlib.Path,required = True)
  parser.add_argument("--model_type",help="type of model", choices=["image","text","both"],type=str,required = True)
  parser.add_argument("--batch_size",help="batch size for the model", type=int, default=32,required = True)
  parser.add_argument("--save_model_path",help="model path along with name where to save it", type=str,required = True)
  parser.add_argument("--epochs",help="number of epochs", type=int,default=30,required = True)
  parser.add_argument("--lr_callback",help="type of lr scheduler", choices=["one_cycle","reduce_lr_plateau","None"],
                      required=True,type=str)
  args=parser.parse_args()
  set_randomness()
  TRAINING(args)
