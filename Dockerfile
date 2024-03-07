FROM python:3.8.10

WORKDIR /user/src/app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "python",  "main.py"]