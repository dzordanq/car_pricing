import pickle
import os
import numpy as np
import pandas as pd
import pickle


script_path = os.path.dirname(os.path.abspath(__file__))


def get_linear_model(model_name):
    with open(os.path.join(script_path, 'Regresja pliki', 'Regresja liniowa', model_name), 'rb') as f:
        regressor = pickle.loads(f.read())
    # regressor = pickle.load(open(os.path.join(script_path,'Regresja pliki','Regresja liniowa', model_name), 'rb'))
    return regressor


def get_polynomial_model(model_name):
    with open(os.path.join(script_path, 'Regresja pliki', 'Regresja wielomianowa', model_name), 'rb') as f:
        regressor = pickle.loads(f.read())
    #regressor = pickle.load(open(os.path.join(script_path,'Regresja pliki','Regresja wielomianowa', model_name), 'rb'))
    return regressor


def get_polynomial_features(model_name):
    with open(os.path.join(script_path, 'Regresja pliki', 'Regresja wielomianowa cechy', model_name), 'rb') as f:
        features = pickle.loads(f.read())
    #features = pickle.load(open(os.path.join(script_path,'Regresja pliki','Regresja wielomianowa cechy', model_name), 'rb'))
    return features


def get_ml_model_columns(model_name):
    with open(os.path.join(script_path, 'Regresja pliki', 'Nazwy kolumn', model_name), 'rb') as f:
        df = pickle.loads(f.read())
    columns = df.tolist()
    return columns


def get_ml_scaler(scaler_name):
    with open(os.path.join(script_path, 'Regresja pliki', 'Scaler', scaler_name), 'rb') as f:
        scaler = pickle.loads(f.read())
    return scaler
