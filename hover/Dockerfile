FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -qy \
       build-essential \
       ffmpeg \
       libbox2d-dev \
       python3.7 \
       python3-pip \
       swig

RUN rm /usr/bin/python3 ; ln -s python3.7 /usr/bin/python3
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8
