from model import get_ml_model_columns, get_ml_scaler, get_linear_model, get_polynomial_features, get_polynomial_model
from pymongo import MongoClient
import urllib.parse
import datetime
import numpy as np


def find_replace(arg1):
    dictionary = {' ': '_',
                  'Š': 'S',
                  'ł': 'l',
                  'ë': 'e',
                  'Ż': 'Z',
                  'ż': 'z',
                  'ś': 's',
                  'ć': 'c',
                  'ę': 'e',
                  'ó': 'o'}

    if(type(arg1) is list):
        return [find_replace(el) for el in arg1]
    # is the item in the dict?
    elif(type(arg1) is str):
        for item in arg1:
            # iterate by keys
            if item in dictionary.keys():
                # look up and replace
                arg1 = arg1.replace(item, dictionary[item])
                # return updated string
        return arg1
    else:
        return arg1


def convert_request_data_to_ml_model_data(requestArgs):
    model_name = get_model_name(requestArgs)
    columns = get_ml_model_columns(model_name=model_name)

    data_to_model = [0] * (len(columns) - 4)
    # Loop to fill list with 1 on certain place
    for i in requestArgs:
        if requestArgs[i] in columns:
            index = columns.index(requestArgs[i])
            data_to_model[index] = 1

    # Scaler
    scaled_data = scale_data(model_name, requestArgs)
    data_to_model += scaled_data

    return data_to_model


def fill_data_to_model():

    return None


def get_model_name(requestArgs):
    model_name = requestArgs['Marka_pojazdu'] + '_' + \
        ''.join(
            e for e in requestArgs['Model_pojazdu'] if e.isalnum()) + '.pkl'

    return model_name


def load_vehicle_makes():
    client = MongoClient('localhost', 27017)
    db = client['formularz']
    collection = db['marki']
    makes = collection.find_one()
    client.close()

    makes = makes['Marki']
    makes.sort()

    return makes


def load_vehicle_models(requestArgs):
    client = MongoClient('localhost', 27017)
    db = client['formularz']
    collection = db['modele']
    collection = collection.find_one(
        {'Marka pojazdu': requestArgs['Marka_pojazdu']}
    )
    client.close()

    make = collection['Marka pojazdu']
    models = collection['Model pojazdu']
    models.sort()

    return {'Marka_pojazdu': make,
            'Model_pojazdu': models}


def load_vehicle_version_data(requestArgs):
    client = MongoClient('localhost', 27017)
    db = client['formularz']
    collection = db['wersje']
    collection = collection.find_one(
        {'Marka pojazdu': requestArgs['Marka_pojazdu'],
         'Model pojazdu': requestArgs['Model_pojazdu']},
    )

    client.close()

    make = collection['Marka pojazdu']
    model = collection['Model pojazdu']
    version = collection['Wersja']
    version.sort()

    if(type(version[0]) is float):  # tymczasowo
        version = ['-']
    return {'Marka_pojazdu': make,
            'Model_pojazdu': model,
            'Wersja': version}


def load_vehicle_data(requestArgs):
    client = MongoClient('localhost', 27017)
    db = client['formularz']
    collection = db['auta']
    response = {}
    if requestArgs['Wersja'] == '-':
        collection = collection.find_one(
            {'Marka pojazdu': requestArgs['Marka_pojazdu'],
             'Model pojazdu': requestArgs['Model_pojazdu']})
        for index, el in enumerate(collection):
            if(index == 0):
                continue
            else:
                response[find_replace(el)] = collection[el]
    else:
        collection = collection.find_one(
            {'Marka pojazdu': requestArgs['Marka_pojazdu'],
             'Model pojazdu': requestArgs['Model_pojazdu'],
             'Wersja': requestArgs['Wersja']})
        for index, el in enumerate(collection):
            try:
                for index, el in enumerate(collection):
                    if(index == 0):
                        continue
                    else:
                        response[find_replace(el)] = collection[el]
            except TypeError:
                print('Database returned None -> Function load_vehicle_data')
    client.close()
    return response


def make_dataset_to_create_chart(requestArgs):
    year_list = sorted(get_model_year_list(requestArgs))
    model_name = get_model_name(requestArgs)
    data_to_chart = []
    requestArgs = dict(requestArgs)
    
    for year in year_list:
        requestArgs['Rok_produkcji'] = year
        X_test = convert_request_data_to_ml_model_data(requestArgs)

        linear_regressor = get_linear_model(model_name)
        X_linear_test = np.asarray(X_test).reshape(1, -1)

        polynomial_regressor = get_polynomial_model(model_name)
        polynomial_features = get_polynomial_features(model_name)
        X_poly_test = polynomial_features.transform(
            np.asarray(X_test).reshape(1, -1))

        linear_prediction = linear_regressor.predict(X_linear_test)
        polynomial_prediction = polynomial_regressor.predict(X_poly_test)
        
        data_to_chart.append([year, int(linear_prediction.item())])
        data_to_chart.append([year, int(polynomial_prediction.item())])
    return data_to_chart


def get_model_year_list(requestArgs):
    client = MongoClient('localhost', 27017)
    db = client['formularz']
    collection = db['auta']
    if requestArgs['Wersja'] == '-':
        collection = collection.find_one(
            {'Marka pojazdu': requestArgs['Marka_pojazdu'],
             'Model pojazdu': requestArgs['Model_pojazdu']})
    else:
        collection = collection.find_one(
            {'Marka pojazdu': requestArgs['Marka_pojazdu'],
             'Model pojazdu': requestArgs['Model_pojazdu'],
             'Wersja': requestArgs['Wersja']})

    return collection['Rok produkcji']


def scale_data(model_name, requestArgs):
    moc = int(requestArgs['Moc'])
    przebieg = int(requestArgs['Przebieg'])
    pojemnosc = int(requestArgs['Pojemnosc'])
    rok_produkcji = int(requestArgs['Rok_produkcji'])

    scaler = get_ml_scaler(model_name)
    scaled_data = scaler.transform(
        [[moc, przebieg, pojemnosc, rok_produkcji]]).tolist()

    return scaled_data[0]
# [0, rok_produkcji, przebieg, pojemnosc, moc, 0, 0, 0, # Male ,Miejskie, Coupe
#                          0, 1, 0, 1, 0, 0, # Kombi, Kompakt, Sedan, Benzyna, Benzyna+Gaz, Diesel
#                          0, 0, 0, 1, 0, # Wersja 1,2,2,3,4
#                          0, 0, 0, 1]


# "data":{"Marka pojazdu":"Mazda",
#         "Moc":"150",
#         "Oferta od":"Osoby prywatnej",
#         "Pojemnosc":"1800",
#         "Przebieg":"77000",
#         "Rok produkcji":"2015",
#         "Silnik":"Silnik_Benzyna",
#         "Skrzynia biegow":"Skrzynia_Automatyczna bezstopniowa (CVT)",
#         "Typ auta":"Typ_Coupe",
#         "Wersja":"Wersja_III (2013-)"}
