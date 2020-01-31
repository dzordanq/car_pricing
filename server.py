from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from model import get_linear_model, get_polynomial_model, get_polynomial_features
import functions
import numpy as np
import json
import os
from bson.json_util import dumps
import datetime
from bson.objectid import ObjectId


app = Flask(__name__)
CORS(app)


@app.route('/makes', methods=['GET'])
def make():
    data = functions.load_vehicle_makes()
    response = {
        'Marki': data
    }

    return jsonify(response), 200


@app.route('/models', methods=['GET'])
def model():
    data = functions.load_vehicle_models(request.args)
    response = {
        'Marka': data['Marka_pojazdu'],
        'Modele': data['Model_pojazdu']
    }
    return jsonify(response), 200


@app.route('/versions', methods=['GET'])
def version():
    data = functions.load_vehicle_version_data(request.args)
    response = {
        'Marka': data['Marka_pojazdu'],
        'Modele': data['Model_pojazdu'],
        'Wersje': data['Wersja']

    }
    return jsonify(response), 200


@app.route('/vehicle_data', methods=['GET'])
def vehicle_data():
    data = functions.load_vehicle_data(request.args)
    if data['Liczba_pozycji'] < 10:
        print("Nie mozna wycenic pojazdu z powodu zbyt małej liczby danych")
        response = {
            "Komunikat": "Nie mozna wycenic pojazdu z powodu zbyt małej liczby danych"
        }
    else:
        response = {
            'Dane_pojazdu': data
        }
    return jsonify(response), 200


@app.route('/estimated_price', methods=['GET'])
def get_price():
    model_name = functions.get_model_name(request.args)
    X_test = functions.convert_request_data_to_ml_model_data(request.args)

    linear_regressor = get_linear_model(model_name)
    X_linear_test = np.asarray(X_test).reshape(1, -1)

    polynomial_regressor = get_polynomial_model(model_name)
    polynomial_features = get_polynomial_features(model_name)
    X_poly_test = polynomial_features.transform(
        np.asarray(X_test).reshape(1, -1))

    linear_prediction = linear_regressor.predict(X_linear_test)
    polynomial_prediction = polynomial_regressor.predict(X_poly_test)

    data_to_chart = functions.get_data_to_chart(request.args)
    otomoto_url = functions.generate_otomoto_link(request.args)

    response = {
        'Cena regresja liniowa': int(linear_prediction.item()),
        'Cena regresja wielomianowa': int(polynomial_prediction.item()),
        'Url': otomoto_url,
        'Lista': data_to_chart
    }

    # response = {
    #     'Cena' : int(polynomial_prediction.item())
    # }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
