from apps.core.logger import Logger
from sklearn.model_selection import train_test_split
from apps.core.file_operation import FileOperation
from apps.tunning.cluster import KMeansCluster
from xgboost import XGBRegressor
import apps.utils.utils as ut
import apps.db.config as db

class TrainModel:

    def __init__(self, run_id, data_path, raw_data, utils, label, training_path, training_db, columns):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, 'TrainModel', 'training')
        self.fileOperation = FileOperation(self.run_id, 'training')
        self.raw_data = raw_data
        self.utils_memory = utils
        self.label_encoder = label
        self.training_path = training_path
        self.columns = columns
        self.training_db = training_db

    def training_model(self):
        try:
            self.logger.info('Start of Training')
            self.logger.info('Run_id:' + str(self.run_id))

            self.logger.info('Start of reading dataset...')
            preprocess_model = ut.Utils(self.run_id, self.raw_data, 'INFO',
                                        self.utils_memory, self.label_encoder, self.columns)

            self.data = preprocess_model.preprocess_raw_data()

            if 'Unnamed: 0' in self.data.columns:
                self.data.drop(columns='Unnamed: 0', inplace=True)

            self.cluster = KMeansCluster(self.run_id)
            self.logger.info('End of reading dataset...')
            self.logger.info('Start of splitting features and label ...')

            self.X = self.data.drop(labels='Price',
                                    axis=1)

            self.y = self.data['Price']
            self.logger.info('End of splitting features and label ...')

            self.logger.info('Saving to database')

            self.columns['price'] = float
            self.columns['normalized_kilometers'] = self.columns['kilometers_driven']
            self.columns.pop('kilometers_driven', None)

            pg_db = db.DatabaseOperation(self.run_id, self.training_path, 'training', self.columns)
            pg_db.create_table(self.training_db, "uc_training_data")
            pg_db.insert_data(self.training_db, "uc_training_data", self.data)

            number_of_clusters = self.cluster.elbow_plot(self.X)

            self.X = self.cluster.create_clusters(self.X, number_of_clusters)
            self.X['Labels'] = self.y
            list_of_clusters = self.X['Cluster'].unique()
            for i in list_of_clusters:
                cluster_data = self.X[self.X['Cluster'] == i]

                cluster_features = cluster_data.drop(['Labels', 'Cluster'], axis=1)
                cluster_label = cluster_data['Labels']

                x_train, x_test, y_train, y_test = train_test_split(cluster_features, cluster_label, test_size=0.2,
                                                                    random_state=0)
                best_model_name, best_model = self.train_XGBRegressor(x_train, y_train)

                self.fileOperation.save_model(best_model, best_model_name + str(i))

            self.logger.info('End of Training')
        except Exception:
            self.logger.exception('Unsuccessful End of Training')
            raise Exception

    def train_XGBRegressor(self, x_train, y_train):
        model = XGBRegressor(objective='reg:squarederror', enable_categorical=False, learning_rate=0.1, max_depth=5,
                             n_estimators=100, tree_method='hist', categorical_feature='auto')
        model.fit(x_train, y_train)
        self.logger.info('Model successfully trained on XGBRegressor')
        return "XGBRegressor", model
