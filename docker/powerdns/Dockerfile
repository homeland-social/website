FROM alpine:3.15 AS build

ARG PDNS_VERSION=4.5.2

ENV PDNS_CONF=/etc/pdns.conf
ENV PDNS_CONF_DIR=/etc/pdns.d
ENV PDNS_SQL_DIR=/var/lib/pdns

ADD ./docker/powerdns/entrypoint.sh /entrypoint.sh
ADD ./docker/powerdns/pdns.conf.tmpl /etc/
RUN mkdir -p ${PDNS_CONF_DIR}
RUN mkdir -p ${PDNS_SQL_DIR}

RUN wget https://raw.githubusercontent.com/eficode/wait-for/master/wait-for
RUN chmod +x /wait-for
RUN chmod +x /entrypoint.sh
RUN wget https://raw.githubusercontent.com/PowerDNS/pdns/master/modules/gsqlite3backend/schema.sqlite3.sql -O ${PDNS_SQL_DIR}/schema.sqlite3.sql

RUN apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing/ envsubst && \
    apk add --no-cache build-base lua lua-dev libcrypto1.1 libssl1.1 \
                       openssl-dev boost boost-dev postgresql-client libpq-dev \
                       libcurl curl-dev sqlite sqlite-dev coreutils && \
    mkdir /build && cd /build && \
    wget https://downloads.powerdns.com/releases/pdns-${PDNS_VERSION}.tar.bz2 && \
    tar xjf pdns-${PDNS_VERSION}.tar.bz2 && \
    cd pdns-${PDNS_VERSION} && \
    ./configure --prefix=/ --with-modules="bind gpgsql gsqlite3 random" && \
    make -j 8 && \
    make install && \
    apk del build-base lua-dev openssl-dev boost-dev libpq-dev curl-dev sqlite-dev && \
    rm -rf /build

RUN adduser -Ds /bin/false pdns pdns

EXPOSE 53/tcp 53/udp

ENTRYPOINT [ "/entrypoint.sh" ]
