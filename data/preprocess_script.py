import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder
df = pd.read_csv("Processed_training_data.csv")
label_encoder = LabelEncoder()
categorical_columns = ['fuel_type_cng','fuel_type_diesel','fuel_type_lpg','fuel_type_petrol','transmission_automatic','transmission_manual']
for col in categorical_columns:
    df[col] = label_encoder.fit_transform(df[col])

df.to_csv("Processed_training_data.csv", index=False)

current_directory = os.getcwd()
file_path = "training_data/cleaned_used_cars.csv"
data_path = os.path.join(current_directory, file_path)
data = pd.read_csv(data_path)
unique_strings = data["Brand"].unique().tolist()
print("Unique strings from column 'Brand':")
print(unique_strings)
print(len(unique_strings))