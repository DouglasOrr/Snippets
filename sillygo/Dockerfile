FROM ubuntu:14.04
ADD . /code
WORKDIR /code
RUN apt-get -q update && apt-get -qy install \
    git-core                                 \
    libopenblas-dev                          \
    python3                                  \
    python3-pip                              \
    python3-numpy                            \
    python3-scipy                            \
    && apt-get -q clean
RUN pip3 install -r requirements.txt
CMD python -m sillygo.server
