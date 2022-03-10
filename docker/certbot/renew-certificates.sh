#!/bin/sh -x

update() {
    DOMAIN=${1}
    FULLCHAIN=/etc/letsencrypt/live/${DOMAIN}/fullchain.pem
    PRIVKEY=/etc/letsencrypt/live/${DOMAIN}/privkey.pem

    if [ -f ${FULLCHAIN} -a -f ${PRIVKEY} ]; then
        cat ${FULLCHAIN} ${PRIVKEY} > /etc/certificates/${DOMAIN}.pem
    fi

    CERT=/usr/local/etc/haproxy/certificates/${DOMAIN}.pem

    if [ -f /etc/certificates/${DOMAIN}.pem ]; then
        echo -e "set ssl cert ${CERT} <<\n$(cat /etc/certificates/${DOMAIN}.pem)\n" | \
            socat tcp-connect:${HAPROXY_HOST}:${HAPROXY_PORT} -
        echo "commit ssl cert ${CERT}" | \
            socat tcp-connect:${HAPROXY_HOST}:${HAPROXY_PORT} -
        echo "show ssl cert ${CERT}" | \
            socat tcp-connect:${HAPROXY_HOST}:${HAPROXY_PORT} -
    fi
}

create() {
    DOMAIN=${1}

    certbot certonly \
        --non-interactive --agree-tos --email ${CERTBOT_EMAIL} \
        --authenticator certbot-pdns:auth ${CERTBOT_EXTRA_ARGS} \
        -d ${DOMAIN}

    update ${DOMAIN}
}

for DOMAIN in $(echo ${CERTBOT_SHARED_DOMAINS} | sed "s/,/ /g"); do
    if [ -d /etc/letsencrypt/live/${DOMAIN} ]; then
        certbot renew --authenticator certbot-pdns:auth \
            --cert-name ${DOMAIN} ${CERTBOT_EXTRA_ARGS}

        update ${DOMAIN}

    else
        create ${DOMAIN}

    fi
done
