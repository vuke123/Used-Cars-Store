import logging
import os
class Logger:

    def __init__(self, run_id, log_module, log_file_name, mode=logging.DEBUG):
        self.logger = logging.getLogger(str(log_module) + '_' + str(run_id))
        self.logger.setLevel(mode)
        if log_file_name == 'training':
            #refactor!
            path = os.path.abspath(__file__)
            for _ in range(3):
                path = os.path.dirname(path)
            project_path = path
            log_dir = os.path.join(project_path, 'logs', 'training_logs', f"training_log_{run_id}.log")
            os.makedirs(os.path.dirname(log_dir), exist_ok=True)
            file_handler = logging.FileHandler(log_dir)
        else:
            file_handler = logging.FileHandler('logs/prediction_logs/predict_log_' + str(run_id) + '.log')

        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def info(self, message):
        self.logger.info(message)

    def exception(self, message):
        self.logger.exception(message)