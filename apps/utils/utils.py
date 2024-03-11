from apps.core.logger import Logger
import apps.utils.data_utils as ut

class Utils:
    def __init__(self, run_id, data_path, mode, utils_memory, label_encoder, columns):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, 'Preprocessor', mode)
        self.utils_memory = utils_memory
        self.label_encoder = label_encoder
        self.columns = columns

    def preprocess_raw_data(self):
        try:
            ut.data_validation(self.data_path, self.columns)
            df = ut.preprocess_raw_data(self.data_path, self.utils_memory, self.label_encoder)
            df = df.dropna()
            if 'Unnamed: 0' in df.columns:
                df.drop(columns='Unnamed: 0', inplace=True)
        except SyntaxError as e:
            print(f"Syntax error occurred: {e}")
            df = None
        return df

    def preprocess_predict_data(self, df):
        df['normalized_kilometers'] = df['kilometers_driven']
        df.pop('kilometers_driven')
        df = ut.preprocess_predict_data(df, self.utils_memory, self.label_encoder)
        return df

    def complete_columns(self, data):
        columns_to_create = [
            'fuel_type_CNG', 'fuel_type_Diesel', 'fuel_type_LPG', 'fuel_type_Petrol',
            'transmission_Automatic', 'transmission_Manual'
        ]
        sorted_keys = [key for key in self.columns.keys()]

        for column in columns_to_create:
            if column not in data.columns:
                data[column] = 0

        return data[sorted_keys]

class ValidationError(SyntaxError):
    def __init__(self, message="Data form that represent used car should be correctly filled."):
        self.message = message
        super().__init__(message)

