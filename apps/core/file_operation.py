import pickle
import os
import shutil
from apps.core.logger import Logger

class FileOperation:

    def __init__(self, run_id, mode):
        self.run_id = run_id
        self.logger = Logger(self.run_id, 'FileOperation', mode)

    def save_model(self, model, file_name):
        try:
            self.logger.info('Saving Models')
            path = os.path.join('apps/models/', file_name)
            if os.path.isdir(path):
                shutil.rmtree('apps/models')
                os.makedirs(path)
            else:
                os.makedirs(path)
            with open(path + '/' + file_name + '.sav',
                      'wb') as f:
                pickle.dump(model, f)
            self.logger.info('Model File ' + file_name + ' saved')
            self.logger.info('End of Save Models')
            return 'success'
        except Exception as e:
            self.logger.exception('Exception raised while Saving Models: %s' % e)
            raise Exception()

    def load_model(self, file_name):
        try:
            self.logger.info('Loading Models')
            with open('apps/models/' + file_name + '/' + file_name + '.sav', 'rb') as f:
                self.logger.info('Model File ' + file_name + ' loaded')
                self.logger.info('End of Load Model')
                return pickle.load(f)
        except Exception as e:
            self.logger.exception('Exception raised while Loading Model: %s' % e)
            raise Exception()
