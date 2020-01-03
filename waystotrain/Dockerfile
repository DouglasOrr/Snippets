FROM nvidia/cuda:10.2-cudnn7-runtime-ubuntu18.04

RUN apt-get update \
    && apt-get install -qy \
       python3.7 \
       python3-pip

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
