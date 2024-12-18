FROM python:3.13.1-alpine3.21
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apk add tzdata
RUN ln -s /usr/share/zoneinfo/America/New_York /etc/localtime
