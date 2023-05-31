FROM python:3-alpine

RUN pip install --upgrade pip


RUN apk update

WORKDIR /
COPY front_end /front_end
COPY back_end /back_end
COPY .env /

# venv
ENV VIRTUAL_ENV=/venv

# python setup
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# upgrade pip
RUN /${VIRTUAL_ENV}/bin/python -m pip install --upgrade pip
RUN pip install -r back_end/requirements.txt


CMD python -m back_end.scraper
