FROM python:latest

MAINTAINER Anton Bagryanov <antibagr@github.com>

RUN useradd -s /bin/bash app

WORKDIR /home/app

COPY requirements.txt /home/app

RUN python3 -m pip install -r requirements.txt --no-cache-dir

USER app
