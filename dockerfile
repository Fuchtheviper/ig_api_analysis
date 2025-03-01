FROM apache/airflow:latest

USER root

RUN apt-get update && \
    apt-get -y install git build-essential && \
    apt-get clean

COPY requirements.txt /requirements.txt

USER airflow

RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

ENV PYTHONPATH="/opt/airflow/src:/opt/airflow/dags:/opt/airflow/configs"

USER airflow