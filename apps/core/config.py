import random
from datetime import datetime

class Config:

    def __init__(self):
        self.training_data_path = 'data/training_data'
        self.training_database = 'used_cars'
        self.prediction_data_path = 'data/prediction_data'
        self.prediction_database = 'used_cars_pp'
        self.raw_data_path = "data/raw_data/train-data.csv"
        self.utils_memory = "apps/utils/Memory.txt"
        self.label_encoder = "apps/utils/LabelEncoder.joblib"
        self.columns = {'year': float, 'mileage': int, 'engine': float, 'power': float, 'kilometers_driven': float,
                        'name': int, 'fuel_type': str, 'transmission': str}

    def run_id(self):
        self.now = datetime.now()
        self.date = self.now.date()
        self.current_time = self.now.strftime("%H%M%S")
        return str(self.date) + "_" + str(self.current_time) + "_" + str(random.randint(100000000, 999999999))
