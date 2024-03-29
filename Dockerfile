FROM python:3.8.12-slim-buster

WORKDIR /AppKeePass

COPY src/ .

RUN groupadd -r app \
  && useradd -r -s /bin/sh -g app app \
  && chown -R app:app /AppKeePass \
  && pip install -r requirements.txt

USER app

CMD [ "python", "app.py" ]
