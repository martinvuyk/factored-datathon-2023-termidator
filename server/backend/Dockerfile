FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /container

COPY requirements.txt /container
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .
