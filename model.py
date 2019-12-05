import pickle
import os
import numpy as np
import pandas as pd
import pickle
# shift + alf + f  -> auto reformat code


def get_ml_model(model_name):
    """
    Models:
        mazdy_model.pkl
        grande_punto_model.pkl
    """
    path = r"C:\Users\Kamil\Desktop\Machine_Learning_AZ_Template_Folder\otomoto\otomoto_wszystkie_dane\Regresja pliki\Modele regresji"
    regressor = pickle.load(open(os.path.join(path, model_name), 'rb'))
    return regressor


def get_ml_model_columns(model_name):
    """
    Columns:
        punta.pkl
    """
    path = r"C:\Users\Kamil\Desktop\Machine_Learning_AZ_Template_Folder\otomoto\otomoto_wszystkie_dane\Regresja pliki\Nazwy kolumn"
    with open(os.path.join(path, model_name), 'rb') as f:
        df = pickle.loads(f.read())
    columns = df.tolist()
    return columns


def get_ml_scaler(scaler_name):
    """
    Scalers:
        grande_punto_scaler.pkl
    """
    path = r"C:\Users\Kamil\Desktop\Machine_Learning_AZ_Template_Folder\otomoto\otomoto_wszystkie_dane\Regresja pliki\Scaler"
    with open(os.path.join(path, scaler_name), 'rb') as f:
        scaler = pickle.loads(f.read())
    return scaler

# test = get_ml_model_columns(model_name='punta.pkl')
# print(test)
# regressor = get_ml_model()
# X_test = np.asarray([0, 2016, 105000, 1598, 105, 0, 0, 0,
#                      0, 1, 0, 1, 0, 0, 1, 0,
#                      0, 0, 0, 0, 0, 0, 1]).reshape(1, -1)
# pred = regressor.predict(X_test).item(0)
# print(type(X_test))
# print(int(pred))
