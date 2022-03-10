FROM python:3-alpine3.15

ARG CERTBOT_VERSION=1.24.0
ENV CERTBOT_VERSION=${CERTBOT_VERSION}

ENV CERTBOT_PDNS_CONF=/etc/letsencrypt/certbot-pdns.json

ADD ./docker/certbot/entrypoint.sh /entrypoint.sh
ADD ./docker/certbot/renew-certificates.sh /usr/local/bin/
RUN wget https://raw.githubusercontent.com/eficode/wait-for/master/wait-for

RUN chmod +x /wait-for
RUN chmod +x /entrypoint.sh
RUN chmod +x /usr/local/bin/renew-certificates.sh

VOLUME /etc/letsencrypt /var/lib/letsencrypt
WORKDIR /opt/certbot

RUN wget -O certbot-${CERTBOT_VERSION}.tar.gz https://github.com/certbot/certbot/archive/v${CERTBOT_VERSION}.tar.gz && \
    tar xf certbot-${CERTBOT_VERSION}.tar.gz

# Install certbot runtime dependencies
RUN apk add --no-cache --virtual .certbot-deps \
        libffi \
        libssl1.1 \
        openssl \
        ca-certificates \
        binutils

# Install certbot from sources
RUN apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing/ envsubst && \
    apk add --no-cache socat && \
    apk add --no-cache --virtual .build-deps \
        gcc \
        linux-headers \
        openssl-dev \
        musl-dev \
        libffi-dev \
        python3-dev \
        cargo \
    && python certbot-${CERTBOT_VERSION}/tools/pipstrap.py \
    && python certbot-${CERTBOT_VERSION}/tools/pip_install.py --no-cache-dir \
            --editable certbot-${CERTBOT_VERSION}/acme \
            --editable certbot-${CERTBOT_VERSION}/certbot \
    && pip3 install certbot-pdns \
    && apk del .build-deps

ENTRYPOINT [ "/entrypoint.sh" ]
