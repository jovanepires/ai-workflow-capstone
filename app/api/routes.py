import os
import pickle
import json
import threading
import pandas as pd

from flask import request, current_app as app
from flask import render_template, send_file, Response
from app.data_ingestion.data_repository import DataRepository
from app.logger import logger
from app.model import model_predict, model_train, model_load
from settings import DATA_DIR_TRAIN


def json_stream(items):
    glue = ''
    yield '['
    for item in items:
        yield glue + str(json.dumps(item))
        glue = ','
    yield ']'

@app.route('/', methods=['GET'])
def status():
    return {'status': 'success'}, 200

@app.route('/train', methods=['POST'])
def app_model_train():
    """
    basic predict function for the API
    """

    ## check for request data
    if not request.json:
        return {"status": "ERROR: API (train): did not receive request data"}, 200

    ## set the test flag
    test = False
    if 'mode' in request.json and request.json['mode'] == 'test':
        test = True

    print("... training model")
    # worker_thread = threading.Thread(target=model_train, args=([], DATA_DIR_TRAIN, test))
    # worker_thread.start()
    model = model_train(DATA_DIR_TRAIN, test=test)
    print("... training complete")
    return {'status': 'success'}, 200

@app.route('/predict', methods=['POST'])
def app_model_predict():
    """
    basic predict function for the API
    """
    if not request.json:
        return {"status": "ERROR: API (predict): did not receive request data"}, 200

    if 'query' not in request.json:
        return {"status": "ERROR API (predict): received request, but no 'query' found within"}, 200

    if 'type' not in request.json:
        print("WARNING API (predict): received request, but no 'type' was found assuming 'numpy'")
        query_type = 'numpy'

    ## set the test flag
    test = False
    if 'mode' in request.json and request.json['mode'] == 'test':
        test = True

    ## extract the query
    query = request.json['query']

    if request.json['type'] == 'dict':
        pass
    else:
        return {"status": "ERROR API (predict): only dict data types have been implemented"}, 200

    country = query['country']
    year = query['year']
    month = query['month']
    day = query['day']

    ## load model
    all_data, all_models = model_load()

    model = all_models[country]

    if not model:
        return {"status": "ERROR: model is not available"}, 200

    result = model_predict(country=country,
                            year=year,
                            month=month,
                            day=day,
                            all_models=all_models,
                            all_data=all_data,
                            test=test)

    result = json.loads(pd.DataFrame.from_dict(result)\
                 .to_json(orient="records"))

    return Response(json_stream(result), mimetype='application/json')

@app.route('/logs/', methods=['GET'])
@app.route('/logs/<filename>', methods=['GET'])
def app_model_logs(filename=''):
    path = os.path.dirname(os.path.abspath(logger._logger))
    items = os.listdir(path)

    if filename in list(items):
        log_file = os.path.join(path, filename)
        items = json.loads(pd.read_csv(log_file).to_json(orient="records"))

    return Response(json_stream(items), mimetype='application/json')

@app.route('/data', methods=['GET'])
def app_data():
    repository = DataRepository()
    result = repository.connect_db().list().to_json(orient="records")
    items = json.loads(result)

    return Response(json_stream(items), mimetype='application/json')