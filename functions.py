from model import get_ml_model_columns, get_ml_scaler
from pymongo import MongoClient

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


        



def process_request_data(request_data):
    data = request_data
    model_name = get_model_name(data)
    columns = get_ml_model_columns(model_name=model_name)

    moc = int(data['Moc'])
    przebieg = int(data['Przebieg'])
    rok_produkcji = int(data['Rok produkcji'])
    pojemnosc = int(data['Pojemnosc'])

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
    model_name = data['Marka pojazdu'] + '_' + \
        ''.join(e for e in data['Model pojazdu'] if e.isalnum()) + '.pkl'
    return model_name

def load_vehicle_models(data):
    client = MongoClient('localhost', 27017)
    db = client['formularz']
    collection = db['modele']

    collection = collection.find_one(
        {'Marka pojazdu': data['Marka pojazdu']}
        )
    client.close()

    mapped_make = find_replace(collection['Marka pojazdu'])
    mapped_models = find_replace(collection['Model pojazdu'])
    #print('-' * 150)
    if(type(collection['Model pojazdu']) is list):
        print('to jest lista')
        [find_replace(el) for el in collection['Model pojazdu']]
    

    return {'Marka pojazdu': mapped_make ,
            'Model pojazdu' : mapped_models}

def load_vehicle_version_data(data):
    client = MongoClient('localhost', 27017)
    db = client['formularz']
    collection = db['wersje']
    collection = collection.find_one(
        {'Marka pojazdu': data['Marka pojazdu'],
        'Model pojazdu': data['Model pojazdu']},
    )

    client.close()

    mapped_make = find_replace(collection['Marka pojazdu'])
    mapped_models = find_replace(collection['Model pojazdu'])
    mapped_version = find_replace(collection['Wersja'])
    return {'Marka pojazdu': mapped_make ,
            'Model pojazdu' : mapped_models,
            'Wersja' : mapped_version}


def load_vehicle_makes():
    client = MongoClient('localhost', 27017)
    db = client['formularz']
    collection = db['marki']

    makes = collection.find_one()
    mapped_makes = find_replace(makes['Marki'])

    client.close()

    return mapped_makes

def load_vehicle_data(data):
    client = MongoClient('localhost', 27017)
    db = client['formularz']
    collection = db['auta']
    response = {}
    if data['Wersja'] == '-':
        collection = collection.find_one(
                {'Marka pojazdu': data['Marka pojazdu'],
                'Model pojazdu': data['Model pojazdu']})

        
        for index, el in enumerate(collection):
            if(index == 0):
                continue
            else:
                response[find_replace(el)] = find_replace(collection[el]) 
    else:
        collection = collection.find_one(
                {'Marka pojazdu': data['Marka pojazdu'],
                'Model pojazdu': data['Model pojazdu'],
                'Wersja': data['Wersja']})
        try:
            for index, el in enumerate(collection):
                if(index == 0):
                    continue
                else:
                    response[find_replace(el)] = find_replace(collection[el]) 
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
