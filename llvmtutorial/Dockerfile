FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -qy \
       wget \
       gnupg

RUN wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - \
    && echo 'deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-8 main' >> /etc/apt/sources.list

RUN apt-get update \
    && apt-get install -qy \
       clang-8 \
       gdb \
       llvm-8-dev \
       llvm-8-runtime \
       llvm-8-tools

ENV PATH=$PATH:/usr/lib/llvm-8/bin/
