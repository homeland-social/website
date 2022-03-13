#!/bin/sh -x

trap exit TERM;

/wait-for -t 0 ${PDNS_HOST}:${PDNS_PORT}
/wait-for -t 0 ${HAPROXY_HOST}:${HAPROXY_PORT}

if [ ! -z "${CERTBOT_HOST}" ] && [ ! -z "${CERTBOT_PORT}" ]; then
    CERTBOT_EXTRA_ARGS="--server https://${CERTBOT_HOST}:${CERTBOT_PORT}/dir ${CERTBOT_EXTRA_ARGS}"
    wait-for ${CERTBOT_HOST}:${CERTBOT_PORT}
fi

CERTBOT_EMAIL=${CERTBOT_EMAIL:-hostmaster@shanty.social}

if [ ! -z "${PDNS_API_KEY_FILE}" ]; then
    PDNS_API_KEY=$(cat ${PDNS_API_KEY_FILE})
fi

cat << EOF > ${CERTBOT_PDNS_CONF}
{
  "api-key": "${PDNS_API_KEY}",
  "base-url": "http://${PDNS_HOST}:${PDNS_PORT}/api/v1",
  "axfr-time": 5,
  "verify-cert": "False"
}
EOF

unset -v PDNS_API_KEY

while true; do
    . /usr/local/bin/renew-certificates.sh
    sleep 12h &
    wait ${!}
done
