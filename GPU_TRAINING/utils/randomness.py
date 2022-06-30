import os
import numpy as np
import random as rn
import tensorflow as tf
import pandas as pd

def set_randomness():
  '''
  Sets the randomness in the code. But still during training we may have
  randomness because we use GPU.

  '''
  os.environ['PYTHONHASHSEED']="42"
  rn.seed(42)
  np.random.seed(42)
  tf.random.set_seed(42)
