#!/bin/sh -x

if [ ! -z "${PGSQL_PASSWORD_FILE}" ]; then
	export PGSQL_PASSWORD=$(cat ${PGSQL_PASSWORD_FILE})
fi

if [ ! -z "${PDNS_API_KEY_FILE}" ]; then
	export PDNS_API_KEY=$(cat ${PDNS_API_KEY_FILE})
fi

PDNS_MASTER=${PDNS_MASTER:-yes}
PDNS_SLAVE=${PDNS_SLAVE:-no}
PDNS_WEBSERVER=${PDNS_WEBSERVER:-no}
PDNS_LOG_LEVEL=${PDNS_LOG_LEVEL:-4}

envsubst < ${PDNS_CONF}.tmpl > ${PDNS_CONF}

if [ ! -z "${SQLITE_DB}" ]; then
	envsubst < ${PDNS_CONF_DIR}/sqlite.conf.tmpl > ${PDNS_CONF_DIR}/sqlite.conf
elif [ ! -z "${PGSQL_HOST}" ]; then
	envsubst < ${PDNS_CONF_DIR}/pgsql.conf.tmpl > ${PDNS_CONF_DIR}/pgsql.conf
fi

unset -v PGSQL_PASSWORD
unset -v PDNS_API_KEY

if [ ! -z "${SQLITE_DB}" ] && [ ! -f "${SQLITE_DB}" ]; then
	sqlite3 ${SQLITE_DB} < ${PDNS_SQL_DIR}/schema.sqlite3.sql
	chown -R pdns:pdns $(dirname ${SQLITE_DB})

	if [ "${PDNS_SLAVE}" == "yes" ]; then
		sqlite3 ${SQLITE_DB} "insert into supermasters values ('${PDNS_MASTER_ADDR}', '${PDNS_MASTER_NAME}', 'admin');"
	fi

elif [ ! -z "${PGSQL_HOST}" ] && [ "${PDNS_SLAVE}" == "yes" ]; then
	psql -h ${PGSQL_HOST} -p ${PGSQL_PORT} -U ${PGSQL_USERNAME} -W "${PGSQL_PASSWORD}" ${PGSQL_DATABASE} 'insert into supermasters values ('${PDNS_MASTER_ADDR}', '${PDNS_MASTER_HOST}', 'admin');'

fi

trap "pdns_control quit" SIGINT SIGTERM
trap ":" SIGHUP
trap "set -x; pdns_control set query-logging yes" USR1
trap "set +x; pdns_control set query-logging no" USR2

pdns_server "$@" &
PID=$!

wait
