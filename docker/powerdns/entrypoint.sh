#!/bin/sh -x

PDNS_CONF=/etc/pdns.conf

# Defaults
PGSQL_HOST=${PGSQL_HOST:-localhost}
PGSQL_DATABASE=${PGSQL_DATABASE:-pdns}
PGSQL_USERNAME=${PGSQL_USERNAME:-pdns}
PGSQL_PASSWORD=${PGSQL_PASSWORD:-pdns}
PGSQL_DNSSEC=${PGSQL_DNSSEC:-yes}

envsubst < ${PDNS_CONF}.tmpl > ${PDNS_CONF}

unset -v PGSQL_PASSWORD

trap "pdns_control quit" SIGINT SIGTERM
trap ":" SIGHUP
trap "set -x; pdns_control set query-logging yes" USR1
trap "set +x; pdns_control set query-logging no" USR2

pdns_server "$@" &
PID=$!

wait
