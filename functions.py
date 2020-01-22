from model import get_ml_model_columns, get_ml_scaler
from pymongo import MongoClient
import urllib.parse
import datetime


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


def process_request_data(data):
    model_name = get_model_name(data)
    # print(model_name)
    columns = get_ml_model_columns(model_name=model_name)
    moc = int(data['Moc'])
    przebieg = int(data['Przebieg'])
    pojemnosc = int(data['Pojemnosc'])
    rok_produkcji = int(data['Rok_produkcji'])
    

    # Columns for specified car model
    # print('Columns przed', columns)
    # columns[4] = '1'  # jak nie ma Wersji pojazdu to wypełnia '1'
    # print('Columns po ->', columns)
    data_to_model = [0] * (len(columns) - 4)
    # Loop to fill list with 1 on certain place
    for i in data:
        if data[i] in columns:
            index = columns.index(data[i])
            data_to_model[index] = 1

    # Scaler
    scaler = get_ml_scaler(model_name)
    scaled_data = scaler.transform(
        [[moc, przebieg, pojemnosc, rok_produkcji]]).tolist()

    data_to_model += scaled_data[0]

    return data_to_model


def fill_data_to_model():

    return None


def get_model_name(data):
    model_name = data['Marka_pojazdu'] + '_' + \
        ''.join(e for e in data['Model_pojazdu'] if e.isalnum()) + '.pkl'

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


def load_vehicle_models(data):
    client = MongoClient('localhost', 27017)
    db = client['formularz']
    collection = db['modele']
    collection = collection.find_one(
        {'Marka pojazdu': data['Marka_pojazdu']}
    )
    client.close()

    make = collection['Marka pojazdu']
    models = collection['Model pojazdu']
    models.sort()

    return {'Marka_pojazdu': make,
            'Model_pojazdu': models}


def load_vehicle_version_data(data):
    client = MongoClient('localhost', 27017)
    db = client['formularz']
    collection = db['wersje']
    collection = collection.find_one(
        {'Marka pojazdu': data['Marka_pojazdu'],
         'Model pojazdu': data['Model_pojazdu']},
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


def load_vehicle_data(data):
    client = MongoClient('localhost', 27017)
    db = client['formularz']
    collection = db['auta']
    response = {}
    if data['Wersja'] == '-':
        collection = collection.find_one(
            {'Marka pojazdu': data['Marka_pojazdu'],
             'Model pojazdu': data['Model_pojazdu']})
        for index, el in enumerate(collection):
            if(index == 0):
                continue
            else:
                response[find_replace(el)] = collection[el]
    else:
        collection = collection.find_one(
            {'Marka pojazdu': data['Marka_pojazdu'],
             'Model pojazdu': data['Model_pojazdu'],
             'Wersja': data['Wersja']})
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
