from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from model import get_ml_model
import functions
import numpy as np
import json
import os
from bson.json_util import dumps
import datetime
from bson.objectid import ObjectId


app = Flask(__name__)
CORS(app)


# class JSONEncoder(json.JSONEncoder):
#     ''' extend json-encoder class'''
#     def default(self, o):
#         if isinstance(o, ObjectId):
#             return str(o)
#         if isinstance(o, datetime.datetime):
#             return str(o)
#         return json.JSONEncoder.default(self, o)


#app.json_encoder = JSONEncoder


@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('templates', 'main.html')


@app.before_first_request
def startup():
    None


@app.route('/marki', methods=['GET'])
def make():
    data = functions.load_vehicle_makes()
    response = {
        'Marki': data
    }
    
    return jsonify(response), 200

@app.route('/model', methods=['GET'])
def model():
    data = functions.load_vehicle_models(request.args)
    response = {
        'Marka': data['Marka_pojazdu'],
        'Modele': data['Model_pojazdu']
    }
    return jsonify(response), 200

@app.route('/wersja', methods=['GET'])
def version():
    data = functions.load_vehicle_version_data(request.args)
    response = {
        'Marka': data['Marka_pojazdu'],
        'Modele': data['Model_pojazdu'],
        'Wersje': data['Wersja']

    }
    return jsonify(response), 200

@app.route('/dane_pojazdu', methods=['GET'])
def vehicle_data():
    data = functions.load_vehicle_data(request.args)

    response = {
        'Dane_pojazdu' : data
    }
    return jsonify(response), 200


@app.route('/Oszacowana_cena', methods=['GET'])
def get_price():
    X_test = functions.process_request_data(request.args)
    regressor = get_ml_model(functions.get_model_name(request.args))

    X_test = np.asarray(X_test).reshape(1, -1)
    #print('X_test ->', len(X_test[0]))
    #print('Regressor coef ->', len(regressor.coef_[0]))

    prediction = regressor.predict(X_test)

    response = {
        'Cena': int(prediction.item()),
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
# wlaczyc maximiliana jak robi we flasku
