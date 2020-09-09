import os
import pickle
import json
import pandas as pd

from flask import request, current_app as app
from flask import render_template, send_file, Response
from app.data_ingestion.data_repository import DataRepository
from app.logger import logger


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
def model_train():
    return {'status': 'success'}, 200

@app.route('/predict', methods=['POST'])
def model_predict():
    items = []
    return Response(json_stream(items), mimetype='application/json')

@app.route('/logs/', methods=['GET'])
@app.route('/logs/<filename>', methods=['GET'])
def model_logs(filename=''):
    path = os.path.dirname(os.path.abspath(logger._logger))
    items = os.listdir(path)

    if filename in list(items):
        log_file = os.path.join(path, filename)
        items = json.loads(pd.read_csv(log_file).to_json(orient="records"))

    return Response(json_stream(items), mimetype='application/json')

@app.route('/data', methods=['GET'])
def data():
    repository = DataRepository()
    result = repository.connect_db().list().to_json(orient="records")
    items = json.loads(result)

    return Response(json_stream(items), mimetype='application/json')