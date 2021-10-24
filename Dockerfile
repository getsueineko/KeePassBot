FROM python:3.8.12-slim-buster

WORKDIR /opt/AppKeePass

RUN groupadd --gid 1000 appuser \
  && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser \
  && pip install -r requirements.txt

COPY src/requirements.txt .
    
RUN pip install -r requirements.txt

COPY src/ .

USER appuser

CMD [ "python", "app.py" ]
