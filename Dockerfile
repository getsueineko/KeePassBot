FROM python:3.8.5-slim-buster

RUN apt-get update \
    && apt-get upgrade \
    && apt-get autoremove \
    && mkdir -p /opt/AppKeePass

WORKDIR /opt/AppKeePass

COPY ./code/. .

RUN pip install -r requirements.txt

CMD [ "python", "app.py" ]
