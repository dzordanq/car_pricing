import pymongo
from pymongo import MongoClient
from model import get_ml_model_columns, get_ml_scaler


client = MongoClient('localhost', 27017)
db = client['formularz']
collection = db['auta']

audi_A3 = {'Model pojazdu': 'Audi',
        'Marka pojazdu': 'A3',
        'Wersja': ['8L', '8P', '8V']}

audi_A4 = {'Model pojazdu': 'Audi',
        'Marka pojazdu': 'A4',
        'Wersja': ['B5', 'B6', 'B7', 'B8']}

Audi_A3_cols = get_ml_model_columns('Audi_A3.pkl')

existing_document = collection.find_one(audi_A3)
if not existing_document:
    collection.insert_one(audi_A3)
else:
    collection.insert_one(audi_A4)
    

