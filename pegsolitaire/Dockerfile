FROM jupyter/scipy-notebook
COPY . /tmp/build
USER root
RUN apt-get update && apt-get install -qy python3-dev
RUN pip install -r /tmp/build/requirements.txt
USER jovyan
