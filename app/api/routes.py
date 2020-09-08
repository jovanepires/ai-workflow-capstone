import os
import pickle
import json

from flask import request, current_app as app
from flask import render_template, send_file, Response
from app.data_ingestion.data_repository import DataRepository


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

@app.route('/docs', methods=['GET'])
def docs():
    return render_template('swagger.html')

@app.route('/swagger.yaml', methods=['GET'])
def swagger_file():
    return send_file('../../swagger.yaml')

@app.route('/train', methods=['POST'])
def model_train():
    items = []
    return Response(json_stream(items), mimetype='application/json')

@app.route('/predict', methods=['POST'])
def model_predict():
    items = []
    return Response(json_stream(items), mimetype='application/json')

@app.route('/logs/', methods=['GET'])
@app.route('/logs/<filename>', methods=['GET'])
def model_logs(filename=''):
    items = []

    if not filename:
        items.append('file')

    return Response(json_stream(items), mimetype='application/json')

@app.route('/data', methods=['GET'])
def data():
    repository = DataRepository()
    result = repository.connect_db().list().to_json(orient="records")
    items = json.loads(result)

    return Response(json_stream(items), mimetype='application/json')