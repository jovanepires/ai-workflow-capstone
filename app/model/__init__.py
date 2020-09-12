import time,os,re,csv,sys,uuid,joblib
import getopt,pickle
import numpy as np
import pandas as pd

from datetime import date, datetime, timedelta
from collections import defaultdict
from sklearn import svm
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from fbprophet import Prophet

from app.data_ingestion import data_utils
from app.logger import logger 
from app.data_ingestion.data_repository import DataRepository
from settings import *


def _model_train(df, country, test=False):
    """
    example funtion to train model
    
    The 'test' flag when set to 'True':
        (1) subsets the data and serializes a test version
        (2) specifies that the use of the 'test' log file 
    """


    ## start timer for runtime
    time_start = time.time()

    train_size = int(len(df) * 0.75)
    df_train, df_test = df[0:train_size], df[train_size:len(df)]
        
    model = Prophet()
    model.fit(df_train)

    forecast = model.predict(df_test.drop(columns="y"))
    y_pred = forecast['yhat']
    y_test = df_test['y']
    eval_rmse =  round(np.sqrt(mean_squared_error(y_test, y_pred)))
    
    ## retrain using all data
    model = Prophet()
    model.fit(df)

    model_name = re.sub("\.","_",str(MODEL_VERSION))

    if test:
        saved_model = os.path.join(MODEL_DIR,
                                   "test-{}-{}.joblib".format(country, model_name))
        print("... saving test version of model: {}".format(saved_model))
    else:
        saved_model = os.path.join(MODEL_DIR,
                                   "sl-{}-{}.joblib".format(country, model_name))
        print("... saving model: {}".format(saved_model))
        
    joblib.dump(model, saved_model)

    m, s = divmod(time.time()-time_start, 60)
    h, m = divmod(m, 60)
    runtime = "%03d:%02d:%02d"%(h, m, s)

    ## update log
    logger.get_logger(country, 'train').info(\
                country=country,
                data_shape=df.shape,\
                eval_test={'rmse': eval_rmse},\
                runtime=runtime,\
                model_version=MODEL_VERSION,\
                test=False)
  

def model_train(country="all",test=False):
    """
    funtion to train model given a df
    
    'mode' -  can be used to subset data essentially simulating a train
    """
    
    if not os.path.isdir(MODEL_DIR):
        os.mkdir(MODEL_DIR)

    if test:
        print("... test flag on")
        print("...... subseting data")
        print("...... subseting countries")
        
    ## fetch formatted data
    repository = DataRepository()
    data = repository.connect_db().list_revenues(country=country)
    data['ts'] = pd.to_datetime(data['date'], unit='ms')
    train = data[['ts', 'revenue']]
    train.columns = ['ds', 'y']

    ## train a different model for each data sets
    countries = repository.connect_db().list_countries()['name'].values
    for c in list([*countries, 'all']):
        c_id = re.sub("\s+","_",c.lower())
        _model_train(train, c_id, test=test)
    
def model_load(prefix='sl',country='all', training=True):
    """
    example function to load model
    
    The prefix allows the loading of different models
    """
    
    models = [f for f in os.listdir(MODEL_DIR) if re.search("sl",f)]

    if len(models) == 0:
        raise Exception("Models with prefix '{}' cannot be found did you train?".format(prefix))

    all_models = {}
    for model in models:
        all_models[re.split("-",model)[1]] = joblib.load(os.path.join(MODEL_DIR, model))
        
    return all_models[country]

def model_predict(model, country, year, month, day, test=False):
    """
    example function to predict from model
    """

    ## start timer for runtime
    time_start = time.time()

    ## input checks
    repository = DataRepository()
    countries = repository.connect_db().list_countries()['name'].values
    countries = [re.sub("\s+","_",c.lower()) for c in countries]
    if country not in countries:
        raise Exception("ERROR (model_predict) - model for country '{}' could not be found".format(country))

    for d in [year,month,day]:
        if re.search("\D",d):
            raise Exception("ERROR (model_predict) - invalid year, month or day")
    
    ## generate target period
    data = repository.connect_db().list_revenues(country=country)
    today_date = pd.to_datetime(max(data['date'].values)).date()
    target_date = date(int(year), int(month), int(day))
    delta = target_date - today_date
    date_list = [target_date - timedelta(days=x) for x in range(delta.days)]
    future = pd.DataFrame({"ds": date_list})
    sys.stdout.flush()

    ## make prediction and gather data for log entry
    forecast = model.predict(future)
    y_pred = forecast[forecast['ds'] == target_date.strftime("%Y-%m-%d")]['yhat'].values[0]
    
    m, s = divmod(time.time()-time_start, 60)
    h, m = divmod(m, 60)
    runtime = "%03d:%02d:%02d"%(h, m, s)

    ## update predict log
    logger.get_logger(country, 'predict').info(country=country,\
                y_pred=y_pred,\
                y_proba=None,\
                target_date=target_date,\
                runtime=runtime,\
                model_version=MODEL_VERSION,\
                test=test)
    
    result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'trend']]
    result['country_id'] = country

    repository = DataRepository()
    repository.connect_db().drop_table(repository._predictions_table)
    repository.connect_db().insert_predictions(result)

    return result


if __name__ == "__main__":

    """
    basic test procedure for model.py
    """

    ## train the model
    print("TRAINING MODELS")
    data_dir = DATA_DIR_TRAIN
    model_train(data_dir,test=True)

    ## load the model
    print("LOADING MODELS")
    model = model_load()
    print("... models loaded: ",",".join(['all']))

    ## test predict
    country='all'
    year='2018'
    month='01'
    day='05'
    result = model_predict(model, country, year, month, day)
    print(result)