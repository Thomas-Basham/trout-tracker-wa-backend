FROM python:3.11-alpine

RUN pip install --upgrade pip


RUN apk update
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    python3-dev \
    build-base

WORKDIR /
COPY api /api
COPY web_scraper /web_scraper
COPY .env /

# venv
ENV VIRTUAL_ENV=/venv

# python setup
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# upgrade pip
RUN /${VIRTUAL_ENV}/bin/python -m pip install --upgrade pip
RUN pip install -r web_scraper/requirements.txt


CMD python -m web_scraper.scraper
