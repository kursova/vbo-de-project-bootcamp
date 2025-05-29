FROM spark:3.5.3-java17

USER root

WORKDIR /app

RUN mkdir -p /home/spark/.ivy2/cache && chown spark:spark /home/spark/.ivy2 && chown spark:spark /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY iceberg_nessie.py .