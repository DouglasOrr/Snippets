FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -qy \
       clang-7 \
       llvm-7-dev \
       llvm-7-runtime \
       llvm-7-tools

ENV PATH=$PATH:/usr/lib/llvm-7/bin/
