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
            'Komunikat': 'Wycena pojazdu nie jest możliwa z powodu zbyt małej liczby pojazdów w bazie danych'
            #'Liczba pozycji w bazie danych': data['Liczba_pozycji']
        }
    else:
        response = {
            'Dane_pojazdu': data
        }
    return jsonify(response), 200


@app.route('/vehicle', methods=['GET'])
def vehicle():
    year_price_data = functions.create_year_price_data_to_graph(request.args)
    year_mileage_data = functions.create_mileage_year_data_to_graph(request.args)
    mean_price = functions.calculate_mean_price(request.args)
    capacity_min, capacity_max = functions.get_min_max_capacity(request.args)
    response = {
        'Srednia cena': mean_price,
        'Rok produkcji - cena': year_price_data,
        'Rok produkcji - przebieg': year_mileage_data,
        'Pojemnosc' : {
            'min': capacity_min,
            'max': capacity_max
        }
    }
    return jsonify(response), 200


@app.route('/estimated_price', methods=['GET'])
def get_price():
    prediction = 0
    if request.args['Estymator'] == 'Regresja liniowa':
        prediction = functions.linear_prediction(request.args)
    elif request.args['Estymator'] == 'Regresja wielomianowa':
        prediction = functions.polynomial_prediction(request.args)
        
    year_price_data = functions.create_year_price_data_to_graph(request.args)
    year_price_data_prediction = functions.create_year_price_regression_data_to_graph(request.args)

    otomoto_url = functions.generate_otomoto_url(request.args)

    response = {
        'Cena': prediction,
        'Lista baza danych': year_price_data,
        'Lista predykcje': year_price_data_prediction,
        'Url': otomoto_url
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
