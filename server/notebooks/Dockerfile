FROM python:3.10-slim as build_stage

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /container

COPY requirements.txt /container
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN jupyter nbconvert --to html /container/termidator_unleashed.ipynb

FROM nginx:latest as deploy_stage

COPY --from=build_stage /container/termidator_unleashed.html /usr/share/nginx/html/index.html
COPY --from=build_stage /container/*.png /usr/share/nginx/html/
