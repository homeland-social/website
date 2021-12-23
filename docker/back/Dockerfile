FROM python:3-alpine

ADD ./back /app

ADD ./docker/back/wait-for /wait-for
ADD ./docker/back/entrypoint.sh /entrypoint.sh

RUN chmod +x /wait-for
RUN chmod +x /entrypoint.sh

WORKDIR /app
RUN pip install pipenv && \
    apk add --no-cache build-base libpq libpq-dev python3-dev && \
    pipenv install --system && \
    apk del build-base libpq-dev python3-dev

ENTRYPOINT [ "/entrypoint.sh" ]
