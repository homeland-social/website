#!/bin/sh -x

trap exit TERM;

/wait-for -t 0 ${PDNS_HOST}:${PDNS_PORT}

HAPROXY_HOSTS=$(nslookup -type=a ${HAPROXY_HOST} | grep -v 127 | grep Address: | awk ' { printf "%s ", $2 } ' | xargs echo)
for HAPROXY in ${HAPROXY_HOSTS}; do
    /wait-for -t 0 ${HAPROXY}:${HAPROXY_PORT}
done

if [ ! -z "${CERTBOT_HOST}" ] && [ ! -z "${CERTBOT_PORT}" ]; then
    CERTBOT_EXTRA_ARGS="--server https://${CERTBOT_HOST}:${CERTBOT_PORT}/dir ${CERTBOT_EXTRA_ARGS}"
    wait-for ${CERTBOT_HOST}:${CERTBOT_PORT}
fi

CERTBOT_EMAIL=${CERTBOT_EMAIL:-hostmaster@shanty.social}

if [ ! -z "${PDNS_API_KEY_FILE}" ]; then
    PDNS_API_KEY=$(cat ${PDNS_API_KEY_FILE})
fi

cat << EOF > ${CERTBOT_PDNS_CONF}
certbot_dns_powerdns:dns_powerdns_api_url = http://${PDNS_HOST}:${PDNS_PORT}
certbot_dns_powerdns:dns_powerdns_api_key = ${PDNS_API_KEY}
EOF
chmod og-r ${CERTBOT_PDNS_CONF}

unset -v PDNS_API_KEY

while true; do
    . /usr/local/bin/renew-certificates.sh
    sleep 12h &
    wait ${!}
done
