from flask import Flask, Response, request, send_from_directory
from flask_cors import CORS, cross_origin
from wsgiref import simple_server
from apps.core.config import Config
from apps.training.train import TrainModel
from apps.prediction.predict import PredictModel
import apps.utils.utils as ut
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages.human import HumanMessage

app = Flask(__name__)
CORS(app)

@app.route('/openai_service', methods=['POST'])

def openai_endpoint():

    #load_dotenv(dotenv_path=".env")
    #llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')
    #print(llm([HumanMessage(content="What is capital of Botswana?")]))

    return Response('OpenAI connection endpoint not working properly. Payed subscription is needed')

@app.route('/training', methods=['GET','POST'])
@cross_origin()

def training_endpoint():
    config = Config()
    run_id = config.run_id()
    train_model = TrainModel(run_id, config.training_data_path, config.raw_data_path, config.utils_memory, config.label_encoder, config.training_data_path, config.training_database, config.columns)
    train_model.training_model()
    return Response('Training endpoint')

@app.route('/')
@cross_origin()

def empty_endpoint():
    return Response('Backend server is alive!')

@app.route('/predict', methods=['GET', 'POST'])
@cross_origin()

def predict_endpoint():
    config = Config()
    run_id = config.run_id()
    data_path = config.prediction_data_path
    try:
        request_data = request.get_json()
        print(request_data)
    except Exception as e:
        return Response(f'{e}')
    prediction = PredictModel(run_id, data_path, request_data)
    prediction_response = prediction.predict()
    return Response(f'Prediction --> {prediction_response}')

if __name__ == '__main__':
    #app.run()
    host = '0.0.0.0'
    port = 80
    httpd = simple_server.make_server(host, port, app)
    httpd.serve_forever()


