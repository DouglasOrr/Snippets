FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -qy \
       build-essential \
       clang-7 \
       clang-tools-7 \
       ffmpeg \
       git-core \
       ninja-build \
       python3 \
       python3-dev \
       python3-pip \
       swig \
       wget

COPY tools/build_box2d.sh /tmp/
RUN /tmp/build_box2d.sh /opt/box2d \
    && git clone https://github.com/pybind/pybind11.git /opt/pybind11 --branch v2.2.4

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8

RUN mkdir -p /opt/web \
    && wget -nv https://code.jquery.com/jquery-3.4.1.min.js -O /opt/web/jquery.js \
    && wget -nv https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css -O /opt/web/bootstrap.css
