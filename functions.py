from model import get_ml_model_columns, get_ml_scaler, get_linear_model, get_polynomial_features, get_polynomial_model
from pymongo import MongoClient
import urllib.parse
import datetime
import numpy as np
from urllib.parse import urlencode
import pandas as pd
import re

client = MongoClient("localhost", 27017)

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
                  'ó': 'o',
                  '(': '',
                  ')': ''}

    if(type(arg1) is list):
        return [find_replace(el) for el in arg1]
    elif(type(arg1) is str):
        for item in arg1:
            if item in dictionary.keys():
                arg1 = arg1.replace(item, dictionary[item])
        return arg1
    else:
        return arg1


def convert_request_data_to_ml_model_data(requestArgs):
    model_name = get_model_name(requestArgs)
    columns = get_ml_model_columns(requestArgs)
    # TODO if electric
    data_to_model = [0] * len(columns)
    # Loop to fill list with 1 on certain place
    for i in requestArgs:
        if requestArgs[i] in columns:
            index = columns.index(requestArgs[i])
            data_to_model[index] = 1

    # Scaler
    scaled_data = scale_data(model_name, requestArgs)
    data_to_model[0:4] = scaled_data

    return data_to_model


def get_model_name(requestArgs):
    try:
        wersja = requestArgs['Wersja']
    except:
        wersja = None
    if wersja:
        model_name = requestArgs['Marka_pojazdu'] + '_' + ''.join(
            e for e in requestArgs['Model_pojazdu'] if e.isalnum()) + '_' + ''.join(
            e for e in requestArgs['Wersja'] if e.isalnum()) + '.pkl'
    else:
        model_name = requestArgs['Marka_pojazdu'] + '_' + ''.join(
            e for e in requestArgs['Model_pojazdu'] if e.isalnum()) + '.pkl'

    return model_name


def load_vehicle_makes():
    # 
    db = client['formularz']
    collection = db['marki']
    makes = collection.find_one()

    makes = makes['Marki']
    makes.sort()

    return makes


def load_vehicle_models(requestArgs):  
    db = client['formularz']
    collection = db['modele']
    collection = collection.find_one(
        {'Marka pojazdu': requestArgs['Marka_pojazdu']}
    )


    make = collection['Marka pojazdu']
    models = collection['Model pojazdu']
    models.sort()

    return {'Marka_pojazdu': make,
            'Model_pojazdu': models}


def load_vehicle_version_data(requestArgs):
    
    db = client['formularz']
    collection = db['wersje']
    collection = collection.find_one(
        {'Marka pojazdu': requestArgs['Marka_pojazdu'],
         'Model pojazdu': requestArgs['Model_pojazdu']},
    )


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
    
    db = client['formularz']
    collection = db['auta2']
    response = {}
    if requestArgs['Wersja'] == '-':
        collection = collection.find_one(
            {'Marka pojazdu': requestArgs['Marka_pojazdu'],
             'Model pojazdu': requestArgs['Model_pojazdu']})
        for index, el in enumerate(collection):
            if(index == 0):
                continue
            else:
                if el == 'Pojemność skokowa':
                    if collection[el] == []:
                        key = f'{find_replace(el)}'
                    else:
                        key = f'{find_replace(el)} ({min(collection[el])}-{max(collection[el])})'
                    response[key] = collection[el]
                    continue
                response[find_replace(el)] = collection[el]
    else:
        collection = collection.find_one(
            {'Marka pojazdu': requestArgs['Marka_pojazdu'],
             'Model pojazdu': requestArgs['Model_pojazdu'],
             'Wersja': requestArgs['Wersja']})
        for index, el in enumerate(collection):
            if(index == 0):
                continue
            else:
                if el == 'Pojemność skokowa':
                    key = f'{find_replace(el)} ({min(collection[el])}-{max(collection[el])})'
                    response[key] = collection[el]
                    continue
                response[find_replace(el)] = collection[el]
    return response

def get_min_max_capacity(requestArgs):
    
    db = client['formularz']
    collection = db['auta2']
    
    if requestArgs['Wersja'] == '-':
        collection = collection.find_one(
            {'Marka pojazdu': requestArgs['Marka_pojazdu'],
             'Model pojazdu': requestArgs['Model_pojazdu']})
    else:
        collection = collection.find_one(
            {'Marka pojazdu': requestArgs['Marka_pojazdu'],
             'Model pojazdu': requestArgs['Model_pojazdu'],
             'Wersja': requestArgs['Wersja']})
    
    if collection['Pojemność min'] is None and collection['Pojemność max'] is None:
        return 0, 0
    else:
        return collection['Pojemność min'], collection['Pojemność max']


# Generate data to year / price chart
def create_year_price_data_to_graph(requestArgs):
    db = client['otomoto']
    collection = db['Car']
    year_price_list = []
    
    
    if requestArgs['Wersja'] is not '-':
        try: 
            match = re.search(r"\(\d{4}.\d{4}\)", requestArgs['Wersja']).group()
            match = match.split(match[5])
            year_min = int(match[0][1:])
            year_max = int(match[1][:-1])
        except:
            match = re.search(r"\(\d{4}", requestArgs['Wersja']).group()
            year_min = int(match[1:])
            year_max = None
        year_list = sorted(set(pd.DataFrame(list(collection.find({'Marka pojazdu': requestArgs['Marka_pojazdu'],
                                                                  'Model pojazdu': requestArgs['Model_pojazdu'],
                                                                  'Wersja': requestArgs['Wersja']},
                                                                 {'Rok produkcji': True,
                                                                  '_id': False})))['Rok produkcji']))
        if year_max is not None:
            year_list = list(filter(lambda x: int(x) >= year_min and int(x) <= year_max , year_list))
        else: 
            year_list = list(filter(lambda x: int(x) >= year_min, year_list))
        for year in year_list:
            price_list = pd.DataFrame(list(collection.find({'Marka pojazdu': requestArgs['Marka_pojazdu'],
                                                            'Model pojazdu': requestArgs['Model_pojazdu'],
                                                            'Wersja': requestArgs['Wersja'],
                                                            'Rok produkcji': year},
                                                           {'Cena': True,
                                                            '_id': False})))
            mean_price = int(np.mean(price_list))
            year_price_list.append([year, mean_price])
    else:
        year_list = sorted(set(pd.DataFrame(list(collection.find({'Marka pojazdu': requestArgs['Marka_pojazdu'],
                                                                  'Model pojazdu': requestArgs['Model_pojazdu']},
                                                                 {'Rok produkcji': True,
                                                                  '_id': False})))['Rok produkcji']))

        for year in year_list:
            price_list = pd.DataFrame(list(collection.find({'Marka pojazdu': requestArgs['Marka_pojazdu'],
                                                            'Model pojazdu': requestArgs['Model_pojazdu'],
                                                            'Rok produkcji': year},
                                                           {'Cena': True,
                                                            '_id': False})))
            mean_price = int(np.mean(price_list))
            year_price_list.append([year, mean_price])

    return year_price_list

# Generate data to mileage / price chart
def create_mileage_year_data_to_graph(requestArgs):
    
    db = client['otomoto']
    collection = db['Car']
    year_mileage_list = []
    


    if requestArgs['Wersja'] is not '-':
        try: 
            match = re.search(r"\(\d{4}.\d{4}\)", requestArgs['Wersja']).group()
            match = match.split(match[5])
            year_min = int(match[0][1:])
            year_max = int(match[1][:-1])
        except:
            match = re.search(r"\(\d{4}", requestArgs['Wersja']).group()
            year_min = int(match[1:])
            year_max = None
        year_list = sorted(set(pd.DataFrame(list(collection.find({'Marka pojazdu': requestArgs['Marka_pojazdu'],
                                                                  'Model pojazdu': requestArgs['Model_pojazdu'],
                                                                  'Wersja': requestArgs['Wersja']},
                                                                 {'Rok produkcji': True,
                                                                  '_id': False})))['Rok produkcji']))

        if year_max is not None:
            year_list = list(filter(lambda x: int(x) >= year_min and int(x) <= year_max , year_list))
        else: 
            year_list = list(filter(lambda x: int(x) >= year_min, year_list))
        for year in year_list:
            mileage_list = list(pd.DataFrame(list(collection.find({'Marka pojazdu': requestArgs['Marka_pojazdu'],
                                                                    'Model pojazdu': requestArgs['Model_pojazdu'],
                                                                    'Rok produkcji': year},
                                                           {'Przebieg': True,
                                                            '_id': False})))['Przebieg'])
            mileage_list = [int(el.replace(' ', '')
                            .replace('k','')
                            .replace('m', '')) for el in mileage_list if type(el) is str]
            mean_mileage = int(np.mean(mileage_list))
            year_mileage_list.append([year, mean_mileage])
    else:
        year_list = sorted(set(pd.DataFrame(list(collection.find({'Marka pojazdu': requestArgs['Marka_pojazdu'],
                                                                  'Model pojazdu': requestArgs['Model_pojazdu']},
                                                                 {'Rok produkcji': True,
                                                                  '_id': False})))['Rok produkcji']))

        for year in year_list:
            mileage_list = list(pd.DataFrame(list(collection.find({'Marka pojazdu': requestArgs['Marka_pojazdu'],
                                                                    'Model pojazdu': requestArgs['Model_pojazdu'],
                                                                    'Rok produkcji': year},
                                                           {'Przebieg': True,
                                                            '_id': False})))['Przebieg'])
            mileage_list = [int(el.replace(' ', '')
                            .replace('k','')
                            .replace('m', '')) for el in mileage_list if type(el) is str]
            mean_mileage = int(np.mean(mileage_list))
            year_mileage_list.append([year, mean_mileage])

    return year_mileage_list

def calculate_mean_price(requestArgs):
    
    db = client['otomoto']
    collection = db['Car']
    price_list = []
    
    if requestArgs['Wersja'] is not '-':
        price_list = sorted(set(pd.DataFrame(list(collection.find({'Marka pojazdu': requestArgs['Marka_pojazdu'],
                                                                  'Model pojazdu': requestArgs['Model_pojazdu'],
                                                                  'Wersja': requestArgs['Wersja']},
                                                                 {'Cena': True,
                                                                  '_id': False})))['Cena']))
    else:
        price_list = sorted(set(pd.DataFrame(list(collection.find({'Marka pojazdu': requestArgs['Marka_pojazdu'],
                                                                  'Model pojazdu': requestArgs['Model_pojazdu']},
                                                                 {'Cena': True,
                                                                  '_id': False})))['Cena']))
    mean_price = int(np.mean(price_list))
    return mean_price

def create_year_price_regression_data_to_graph(requestArgs):
    year_list = sorted(get_model_year_list(requestArgs))
    model_name = get_model_name(requestArgs)
    data_to_graph = []
    requestArgs = dict(requestArgs)

    if requestArgs['Estymator'] == 'Regresja liniowa':
        for year in year_list:
            requestArgs['Rok_produkcji'] = year
            X_test = convert_request_data_to_ml_model_data(requestArgs)
            
            linear_regressor = get_linear_model(model_name)
            X_linear_test = np.asarray(X_test).reshape(1, -1)
            linear_prediction = linear_regressor.predict(X_linear_test)
            data_to_graph.append([year, int(linear_prediction.item())])
    else:
        for year in year_list:
            requestArgs['Rok_produkcji'] = year
            X_test = convert_request_data_to_ml_model_data(requestArgs)
            
            polynomial_regressor = get_polynomial_model(model_name)
            polynomial_features = get_polynomial_features(model_name)
            X_poly_test = polynomial_features.transform(
                np.asarray(X_test).reshape(1, -1))
            polynomial_prediction = polynomial_regressor.predict(X_poly_test)
            data_to_graph.append([str(year), int(polynomial_prediction.item())])
        
    return data_to_graph


def get_model_year_list(requestArgs):
    
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
        [[moc, pojemnosc, przebieg, rok_produkcji]]).tolist()

    return scaled_data[0]


def generate_otomoto_url(requestArgs):
    url = "https://www.otomoto.pl/osobowe/"
    make = find_replace(requestArgs['Marka_pojazdu'].lower()).replace('_', '-')
    model = find_replace(
        requestArgs['Model_pojazdu'].lower()).replace('_', '-')
    start_year = f"od-{requestArgs['Rok_produkcji']}"

    fuel_dict = {'Benzyna': 'petrol',
                 'Diesel': 'diesel',
                 'Benzyna+LPG': 'petrol-lpg',
                 'Elektryczny': 'electric',
                 'Hybrydowy': 'hybrid'}

    transmission_dict = {'Na przednie koła': 'front-wheel',
                         'Na tylne koła': 'rear-wheel',
                         'Napęd 4x4': 'all-wheel-lock'}

    url = url + urljoin(make, model, start_year, '?')

    getVars = {'search[filter_float_year:to]': requestArgs['Rok_produkcji'],
               'search[filter_float_mileage:from]': int(int(requestArgs['Przebieg']) * 0.75),
               'search[filter_float_mileage:to]': int(int(requestArgs['Przebieg']) * 1.25),
               'search[filter_float_engine_capacity:from]': int(int(requestArgs['Pojemnosc']) * 0.95),
               'search[filter_float_engine_capacity:to]': int(int(requestArgs['Pojemnosc']) * 1.05),
               'search[filter_enum_fuel_type][0]': fuel_dict[requestArgs['Rodzaj_paliwa']],
               'search[filter_float_engine_power:from]': int(int(requestArgs['Moc']) * 0.8),
               'search[filter_float_engine_power:to]': int(int(requestArgs['Moc']) * 1.2),
               #'search[filter_enum_transmission][0]': transmission_dict[requestArgs['Naped']],
               'search[order]': 'created_at:desc'
               #'search[brand_program_id][0]': '',
               # 'search[country]' : ''
               }
    url = url + urlencode(getVars)
    return url

def get_capacity_range():
    None
    

def linear_prediction(requestArgs):
    model_name = get_model_name(requestArgs)
    X_test = convert_request_data_to_ml_model_data(requestArgs)

    linear_regressor = get_linear_model(model_name)
    X_test = np.asarray(X_test).reshape(1, -1)
   
    linear_prediction = linear_regressor.predict(X_test)
    return int(linear_prediction.item())

def polynomial_prediction(requestArgs):
    model_name = get_model_name(requestArgs)
    X_test = convert_request_data_to_ml_model_data(requestArgs)
    
    polynomial_regressor = get_polynomial_model(model_name)
    polynomial_features = get_polynomial_features(model_name)
    X_test = polynomial_features.transform(np.asarray(X_test).reshape(1, -1))
    
    polynomial_prediction = polynomial_regressor.predict(X_test)
    return int(polynomial_prediction.item())
    
    
    
def urljoin(*args):
    return "/".join(map(lambda x: str(x).rstrip('/'), args))
