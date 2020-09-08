import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# flask port
PORT=os.getenv('PORT', 5000)

# model
MODEL_DIR = os.getenv('MODEL_DIR', '/var/www/models')
DATA_DIR = os.getenv('DATAPATH', '/var/www/cs-train')
MODEL_VERSION = 0.1
MODEL_VERSION_NOTE = "regression model"
DEFAULT_MODEL = RandomForestRegressor()
DEFAULT_PARAM_GRID = {
    'rf__criterion': ['mse','mae'],
    'rf__n_estimators': [10,15,20,25]
}
DEFAULT_SCALER=StandardScaler()