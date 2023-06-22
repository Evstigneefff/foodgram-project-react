FROM python:3.7-slim
WORKDIR /app
RUN apt-get update && apt-get -y install libpq-dev gcc && pip install psycopg2
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
