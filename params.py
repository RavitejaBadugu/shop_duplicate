
import yaml
with open("params.yaml") as f:
  HYPERPARAMETERS=yaml.safe_load(f)

HYPERPARAMETERS['image']['image_size']=tuple(int(x) for x in HYPERPARAMETERS['image']['image_size'][1:-1].split(","))
HYPERPARAMETERS['image']['unfreeze']=int(HYPERPARAMETERS['image']['unfreeze'])
HYPERPARAMETERS['text']['max_length']=int(HYPERPARAMETERS['text']['max_length'])
