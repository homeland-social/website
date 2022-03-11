#!/bin/sh

CERT_DIR=/usr/local/etc/haproxy/certificates
DEFAULT_CERT=${CERT_DIR}/default.pem

if [ ! -f ${CERT_DIR}/default.pem ]; then
	openssl req -x509 -newkey rsa:2048 -keyout ${DEFAULT_CERT} -out ${CERT_DIR}/ca.pem -days 90 -nodes -subj '/CN=*/O=Temp SSL Cert/C=US'
	cat ${CERT_DIR}/ca.pem >> ${DEFAULT_CERT}
	rm -f ${CERT_DIR}/ca.pem
fi

./docker-entrypoint.sh "${@}"
