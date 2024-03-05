import pandas as pd
import json
import joblib
import os
from sklearn.preprocessing import LabelEncoder
import numpy as np


def data_validation(data, columns):
    columns['price'] = float
    columns['normalized_kilometers'] = self.columns['kilometers_driven']
    columns.pop('kilometers_driven', None)

    df = pd.read_csv(data)
    data_columns = {column.lower() for column in df.columns}

    for key, expected_type in columns.items():
        if key not in data_columns:
            raise ValueError(f"There are missing required column: {key}")

    return


def preprocess_raw_data(path, utils_memory, label_encoder_path):
    storage = {}
    df = pd.read_csv(os.path.join(os.getcwd(), path))
    df['Name'] = df['Name'].apply(lambda x: ' '.join(x.split()[:2]))

    if "Location" in df:
        columns_to_drop = ['New_Price', 'Seats', 'Location', 'Owner_Type']

        df.drop(columns=columns_to_drop, inplace=True)
        df.dropna(subset=df.columns.difference(['New_Price']), inplace=True)

    df['Mileage'] = df.apply(lambda row: convert_to_kmpl(float(row['Mileage'].split(" ")[0]), row['Fuel_Type'])
    if isinstance(row['Mileage'], str) and row['Mileage'].split(" ")[1] == 'km/kg'
    else row['Mileage'], axis=1)

    df['Power'] = df['Power'].apply(convert_to_float)

    df['Engine'] = df['Engine'].apply(lambda x: float(x.split()[0]) if pd.notna(x) else None)
    df['Mileage'] = df['Mileage'].apply(lambda x: float(x.split()[0]) if pd.notna(x) else None)
    # df = df[~(df['New_Price'].astype(str).str.contains('Cr'))]

    df[['Brand', 'Model']] = df['Name'].str.split(n=1, expand=True)
    df = df.drop(columns=['Name'])

    max_value = df['Mileage'].max()
    min_value = df['Mileage'].min()

    storage["Mileage_Max"] = max_value
    storage["Mileage_Min"] = min_value

    df['Mileage'] = (df['Mileage'] - min_value) / (max_value - min_value)

    max_value = df['Kilometers_Driven'].max()
    min_value = df['Kilometers_Driven'].min()

    storage["Kilometers_Driven_Max"] = max_value
    storage["Kilometers_Driven_Min"] = min_value

    df['Normalized_Kilometers'] = (df['Kilometers_Driven'] - min_value) / (max_value - min_value)

    df = df.drop(columns=['Kilometers_Driven'])

    max_value = df['Year'].max()
    min_value = df['Year'].min()
    df['Year'] = (df['Year'] - min_value) / (max_value - min_value)
    storage["Year_Max"] = max_value
    storage["Year_Min"] = min_value

    df = df.drop(columns=['Model'])
    df = pd.get_dummies(df, columns=['Fuel_Type'])
    df = pd.get_dummies(df, columns=['Transmission'])
    max_value = df['Power'].max()
    min_value = df['Power'].min()
    df['Power'] = (df['Power'] - min_value) / (max_value - min_value)  # using MinMaxScaler instead
    storage["Power_Max"] = max_value
    storage["Power_Min"] = min_value

    max_value = df['Engine'].max()
    min_value = df['Engine'].min()
    df['Engine'] = (df['Engine'] - min_value) / (max_value - min_value)
    storage["Engine_Max"] = max_value
    storage["Engine_Min"] = min_value

    df['Brand'] = df['Brand'].astype('category')

    label_encoder_path = os.path.join(os.getcwd(), label_encoder_path)

    label_encoders = {}

    categorical_columns = ['Brand']

    for col in categorical_columns:
        label_encoder = LabelEncoder()
        label_encoder.fit(df[col])
        label_encoders[col] = label_encoder

    for col in categorical_columns:
        df[col] = label_encoders[col].transform(df[col])

    utils_memory = os.path.join(os.getcwd(), utils_memory)

    with open(utils_memory, "w") as file:
        json.dump(storage, file, default=convert)

    joblib.dump(label_encoders, label_encoder_path)

    return df


def convert(o):
    if isinstance(o, np.int64):
        return int(o)  # Convert np.int64 to Python int
    elif isinstance(o, np.float64):
        return float(o)  # Convert np.float6


def preprocess_predict_data(data, utils_memory, label_encoder):
    data['year'] = data['year'].astype(int)
    data['power'] = data['power'].astype(float)
    data['normalized_kilometers'] = data['normalized_kilometers'].astype(float)
    data['engine'] = data['engine'].astype(float)
    data['mileage'] = data['mileage'].astype(float)

    data['mileage'] = (data['mileage'] - utils_memory["Mileage_Max"]) / (
                utils_memory["Mileage_Max"] - utils_memory["Mileage_Min"])
    data['year'] = (data['year'] - utils_memory["Year_Max"]) / (utils_memory["Year_Max"] - utils_memory["Year_Min"])
    data['normalized_kilometers'] = (data['normalized_kilometers'] - utils_memory["Kilometers_Driven_Max"]) / (
                utils_memory["Kilometers_Driven_Max"] - utils_memory["Kilometers_Driven_Min"])
    data['power'] = (data['power'] - utils_memory["Power_Max"]) / (
                utils_memory["Power_Max"] - utils_memory["Power_Min"])
    data['engine'] = (data['engine'] - utils_memory["Engine_Max"]) / (
                utils_memory["Engine_Max"] - utils_memory["Engine_Min"])
    label_encoder_ = joblib.load(label_encoder)
    data['brand'] = label_encoder_["Brand"].transform(data['brand'])
    if 'Unnamed: 0' in data.columns:
        data.drop(columns='Unnamed: 0', inplace=True)

    return data


def convert_to_kmpl(fuel_consumption, fuel_type):
    fuel_densities = {'CNG': 0.67, 'Diesel': 0.84, 'Petrol': 0.74, 'LPG': 0.54}

    if fuel_type not in fuel_densities:
        print("Invalid fuel type. Please choose from CNG, Diesel, or Petrol.")
        return None

    kmpl = fuel_consumption / fuel_densities[fuel_type]
    return str(kmpl) + " kmpl"


def convert_to_float(x):
    try:
        return float(x.split()[0])
    except (ValueError, AttributeError):
        return None
