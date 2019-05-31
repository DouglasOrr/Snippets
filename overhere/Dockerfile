FROM jupyter/scipy-notebook:df4a9681f19c

USER root

RUN apt-get update && apt-get install -qy \
    ffmpeg

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

USER jovyan
