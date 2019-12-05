import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


dataset = pd.read_csv('otomoto-wybrane-dane-imputed-processed.csv')
dataset = dataset.drop(dataset.columns[0], axis=1)

# Pobranie wszystikch marek i modeli
marki = list(set(dataset['Marka pojazdu']))

for marka in marki:
    modele = list(
        set(dataset.loc[(dataset['Marka pojazdu'] == marka)]['Model pojazdu']))
    for model in modele:
        # Blok 1
        input('Blok 1')
        input('Blok 2')
        # Pobranie danych danej marki i modelu
        DaneMarki_i_Modelu = dataset.loc[(dataset['Marka pojazdu'] == marki[3]) & (
            dataset['Model pojazdu'] == modele[10])]
        y = DaneMarki_i_Modelu.iloc[:, [0]].values
        DaneMarki_i_Modelu = DaneMarki_i_Modelu.drop(
            dataset.columns[0], axis=1)
        DaneMarki_i_Modelu.isnull().sum()

        # Zamiana danych tekstowych na numeryczne
        cols = ['Oferta od', 'Marka pojazdu', 'Model pojazdu', 'Wersja', 'Napęd', 'Rodzaj paliwa',
                'Skrzynia biegów', 'Stan', 'Typ']

        dataset_encoded = pd.DataFrame()
        for index, col in enumerate(cols):
            dummies = pd.get_dummies(DaneMarki_i_Modelu[col])
            dataset_encoded = pd.concat([dataset_encoded, dummies], axis=1)
        dataset_encoded.reset_index(drop=True, inplace=True)
        # dataset_encoded = dataset_encoded.drop(dataset_encoded.columns[0], axis=1)

        # Przeskalowanie danych
        from sklearn.preprocessing import StandardScaler

        data_to_scale = DaneMarki_i_Modelu[[
            'Moc', 'Przebieg', 'Pojemność skokowa', 'Rok produkcji']]
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data_to_scale)
        scaled_data = pd.DataFrame(scaled_data)
        scaled_data.columns = ['Moc', 'Przebieg',
                               'Pojemność skokowa', 'Rok produkcji']

        # Polaczenie danych binarnych ze znormalizowanymi
        dataset_encoded_and_scalled = pd.concat(
            [dataset_encoded, scaled_data], axis=1)
        X = dataset_encoded_and_scalled.iloc[:, :].values

        # Fitting Simple Linear Regression to the data
        from sklearn.linear_model import LinearRegression
        regressor = LinearRegression()
        regressor.fit(X, y)

        # Pickle machine learning model
        import pickle
        pickle.dump(regressor, open('{0}_{1}.pkl'.format(marka, model), 'wb'))
