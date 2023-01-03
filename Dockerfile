FROM python:3.10.9-slim-bullseye

RUN apt-get update && apt-get --no-install-recommends -y install wget && rm -Rf rm -rf /var/lib/apt/lists/*

WORKDIR /
COPY requirements.txt /
RUN pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir -r /requirements.txt

WORKDIR /srv
COPY . /srv/

HEALTHCHECK CMD wget -q -O - --content-on-error http://localhost:8000|grep -qi "not found"

CMD python bot.py
