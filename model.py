import pickle
import os
import numpy as np
import pandas as pd
import pickle
# shift + alf + f  -> auto reformat code

script_path = os.path.dirname(os.path.abspath(__file__))

def get_ml_model(model_name):
    """
    Models:
        mazdy_model.pkl
        grande_punto_model.pkl
    """
    regressor = pickle.load(open(os.path.join(script_path,'Regresja pliki','Modele regresji', model_name), 'rb'))
    return regressor


def get_ml_model_columns(model_name):
    with open(os.path.join(script_path,'Regresja pliki','Nazwy kolumn', model_name), 'rb') as f:
        df = pickle.loads(f.read())
    columns = df.tolist()
    return columns


def get_ml_scaler(scaler_name):
    with open(os.path.join(script_path,'Regresja pliki','Scaler', scaler_name), 'rb') as f:
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


