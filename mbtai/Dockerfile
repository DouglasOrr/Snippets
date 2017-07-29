FROM ubuntu:15.10
ADD . /code
WORKDIR /code
RUN apt-get -q update && apt-get -qy install \
    python3                                  \
    python3-pip                              \
    python3-numpy                            \
    && apt-get -q clean
RUN pip3 install -r requirements.txt
CMD python -m mbtai.server
