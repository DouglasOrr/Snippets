FROM ubuntu:18.04

# Pre-requisites for LLVM repo

RUN apt-get update \
    && apt-get install -qy \
       wget \
       gnupg \
    && wget -nv -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - \
    && echo 'deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-8 main' >> /etc/apt/sources.list

# Main dependencies

RUN wget https://dl.bintray.com/boostorg/release/1.70.0/source/boost_1_70_0.tar.gz -nv -O /tmp/boost.tar.gz \
    && mkdir /opt/boost \
    && tar -xf /tmp/boost.tar.gz --strip 1 -C /opt/boost \
    && mkdir /opt/catch \
    && wget https://github.com/catchorg/Catch2/releases/download/v2.7.1/catch.hpp -nv -O /opt/catch/catch.hpp

RUN apt-get update \
    && apt-get install -qy \
       clang-8 \
       gdb \
       ninja-build \
       python3 \
       python3-pip \
       llvm-8-dev \
       llvm-8-runtime \
       llvm-8-tools \
    && pip3 install ninja

# Other environment setup

ENV LLVM_HOME=/usr/lib/llvm-8 \
    BOOST_HOME=/opt/boost \
    CATCH_HOME=/opt/catch \
    PATH=$PATH:/usr/lib/llvm-8/bin/
