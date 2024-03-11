from apps.core.logger import Logger
import pandas as pd
import joblib
import apps.utils.utils as ut
import json

class PredictModel:

    def __init__(self, run_id, data_path, request_data):
        self.run_id = run_id
        self.data_path = data_path
        self.request_data = request_data
        self.logger = Logger(self.run_id, 'Predict', 'predict')
        self.column_names = {"year": "FLOAT", "mileage": "INTEGER", "engine": "FLOAT", "power": "FLOAT",
                             "brand": "TEXT", "kilometers_driven": "FLOAT",
                             "fuel_type_CNG": "BOOLEAN", "fuel_type_Diesel": "BOOLEAN", "fuel_type_LPG": "BOOLEAN",
                             "fuel_type_Petrol": "BOOLEAN",
                             "transmission_Automatic": "BOOLEAN", "transmission_Manual": "BOOLEAN"}
        self.utils_memory = "apps/utils/Memory.txt"
        self.label_encoder = "apps/utils/LabelEncoder.joblib"

    def predict(self):
        self.logger.info('Start of Training')
        self.logger.info('Run_id:' + str(self.run_id))
        kmeans = joblib.load(f'apps/models/KMeans/KMeans.sav')
        data_list = [self.request_data]
        data = pd.DataFrame(data_list)
        columns_to_encode = ['fuel_type', 'transmission']
        with open(self.utils_memory, 'r') as file:
            utils_memory_data = file.read()

        utils_memory_dict = json.loads(utils_memory_data)
        preprocess_model = ut.Utils(self.run_id, self.data_path, 'INFO', utils_memory_dict, self.label_encoder, self.column_names)

        data = pd.get_dummies(data, columns=columns_to_encode)
        data = preprocess_model.complete_columns(data)

        data = preprocess_model.preprocess_predict_data(data)
        self.y_kmeans = kmeans.predict(data)
        xgbregressor = joblib.load(f'apps/models/XGBRegressor{self.y_kmeans[0]}/XGBRegressor{self.y_kmeans[0]}.sav')
        prediction = xgbregressor.predict(data.iloc[:, :])
        prediction = prediction * 100000 * 0.011 #lakh - rupees - eur

        return prediction
    # except Exception as e:
    # self.logger.exception('Exception raised while Predicting value:' + str(e))
    # raise Exception()
