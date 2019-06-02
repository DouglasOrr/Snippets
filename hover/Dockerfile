FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -qy \
       build-essential \
       clang-7 \
       clang-tools-7 \
       ffmpeg \
       git-core \
       python3 \
       python3-dev \
       python3-pip \
       swig \
       wget

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY tools/build_box2d.sh /tmp/
RUN /tmp/build_box2d.sh /opt/box2d
RUN git clone https://github.com/pybind/pybind11.git /opt/pybind11 --branch v2.2.4

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8
