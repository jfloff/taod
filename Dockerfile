FROM jfloff/alpine-python:3.4

RUN apk add --update sqlite \
    && rm /var/cache/apk/*

RUN pip install redis

CMD /bin/bash
