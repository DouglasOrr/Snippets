FROM nvidia/cuda:9.1-devel-ubuntu16.04

RUN apt-get -qq update && apt-get -qq -y install curl bzip2 \
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh \
    && conda update conda
    && conda install -y xeus-cling notebook -c QuantStack -c conda-forge

ENV PATH /opt/conda/bin:$PATH
