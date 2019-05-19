FROM jupyter/scipy-notebook
USER root

RUN apt-get update \
    && apt-get install -qy \
       build-essential \
       ffmpeg \
       libbox2d-dev \
       swig

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
