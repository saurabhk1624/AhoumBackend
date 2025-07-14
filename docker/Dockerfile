FROM python:3.11-alpine

RUN apk --no-cache update && \
    apk add --no-cache gcc git python3-dev


ENV PYTHONUNBUFFERED 1
WORKDIR /ahoum

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN adduser --disabled-password ahoum && \
    chown -R ahoum:ahoum /ahoum && \
    chown -R 755 /ahoum

EXPOSE 8000 8003

USER ahoum