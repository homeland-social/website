#!/bin/sh -x

update() {
    DOMAIN=${1}
    FULLCHAIN=/etc/letsencrypt/live/${DOMAIN}/fullchain.pem
    PRIVKEY=/etc/letsencrypt/live/${DOMAIN}/privkey.pem
    CERT=/usr/local/etc/haproxy/certificates/${DOMAIN}.pem

    if [ -f ${FULLCHAIN} -a -f ${PRIVKEY} ]; then
        cat ${FULLCHAIN} ${PRIVKEY} > /etc/certificates/${DOMAIN}.pem
    fi

    if [ -f /etc/certificates/${DOMAIN}.pem ]; then
        for HAPROXY in $(echo ${HAPROXY_HOSTS} | sed "s/,/ /g"); do
            echo -e "set ssl cert ${CERT} <<\n$(cat /etc/certificates/${DOMAIN}.pem)\n" | socat tcp-connect:${HAPROXY}:${HAPROXY_PORT} -
            echo "commit ssl cert ${CERT}" | socat tcp-connect:${HAPROXY}:${HAPROXY_PORT} -
            echo "show ssl cert ${CERT}" | socat tcp-connect:${HAPROXY}:${HAPROXY_PORT} -
        done
    fi
}

create() {
    DOMAIN=${1}
    PREFIX=${2}
    CERT=/usr/local/etc/haproxy/certificates/${DOMAIN}.pem

    if [ ! -f "${CERT}" ]; then
        for HAPROXY in $(echo ${HAPROXY_HOSTS} | sed "s/,/ /g"); do
            echo -e "new ssl cert ${CERT}" | socat tcp-connect:${HAPROXY}:${HAPROXY_PORT} -
        done
    fi

    certbot certonly \
        --non-interactive --agree-tos --email ${CERTBOT_EMAIL} \
        --authenticator certbot-dns-powerdns:dns-powerdns \
        --certbot-dns-powerdns:dns-powerdns-credentials ${CERTBOT_PDNS_CONF} \
        -d "${PREFIX}.${DOMAIN},${DOMAIN}" \
        --cert-name ${DOMAIN} ${CERTBOT_EXTRA_ARGS}

    update ${DOMAIN}
}

renew() {
    DOMAIN=${1}
    PREFIX=${2}

    if [ -d /etc/letsencrypt/live/${DOMAIN} ]; then
        certbot renew \
            --authenticator certbot-dns-powerdns:dns-powerdns \
            --certbot-dns-powerdns:dns-powerdns-credentials ${CERTBOT_PDNS_CONF} \
            --cert-name ${DOMAIN} ${CERTBOT_EXTRA_ARGS}

    else
        create ${DOMAIN} "${PREFIX}"

    fi

    update ${DOMAIN}
}

for DOMAIN in $(echo ${CERTBOT_DOMAINS} | sed "s/,/ /g"); do
    renew ${DOMAIN} www
done

for DOMAIN in $(echo ${CERTBOT_SHARED_DOMAINS} | sed "s/,/ /g"); do
    renew ${DOMAIN} '*'
done
