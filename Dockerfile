FROM python:3.8.5-slim-buster

WORKDIR /opt/AppKeePass

COPY src/requirements.txt .
    
RUN pip install -r requirements.txt

COPY src/ .

CMD [ "python", "app.py" ]
