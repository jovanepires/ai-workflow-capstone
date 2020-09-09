import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# flask port
PORT=os.getenv('PORT', 5000)

# model
MODEL_DIR = os.getenv('MODEL_DIR', '/var/www/models')
DATA_DIR_TRAIN = os.getenv('DATA_DIR_TRAIN', '/var/www/data/cs-train')
DATA_DIR_PROD = os.getenv('DATA_DIR_PROD', '/var/www/data/cs-production')
MODEL_VERSION = 0.1
MODEL_VERSION_NOTE = "regression model"
DEFAULT_MODEL = RandomForestRegressor()
