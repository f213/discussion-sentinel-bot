FROM python:3.10.2-slim-bullseye

WORKDIR /
COPY requirements.txt /
RUN pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir -r /requirements.txt

WORKDIR /srv
COPY . /srv/

CMD python bot.py
