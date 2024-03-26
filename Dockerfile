FROM python:3.12.2-alpine3.19
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apk add tzdata
RUN ln -s /usr/share/zoneinfo/America/New_York /etc/localtime
