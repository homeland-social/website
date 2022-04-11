# website-dns

This image contains powerdns configured via environment variables. You can set up a slave and / or master server using postgres or sqlite.

## Environment variables

Note that you should define `SQLITE_DB` or `PGSQL_*` not both.

| Name | Description | Default |
| ------ | ----------- | ------- |
| `SQLITE_DB` | Sqlite database path, should be located on a persistent volume | |
| `PGSQL_HOST` | Postgres server address | |
| `PGSQL_DATABASE` | Postgres database name | |
| `PGSQL_USERNAME` | Postgres username | |
| `PGSQL_PASSWORD` | Postgres password | |
| `PGSQL_PASSWORD_FILE` | Same as previous, for use with docker secrets | |
| `PDNS_MASTER` | Act as master dns server; `yes` or `no` | `no` |
| `PDNS_SLAVE` | Act as slave dns server; `yes` or `no` | `no` |
| `PDNS_WEBSERVER` | Start api server; `yes` or `no` | `no` |
| `PDNS_WEBSERVER_HOST` | Address to bind api server to | |
| `PDNS_WEBSERVER_PORT` | Port to bind api server to | 8081 |
| `PDNS_WEBSERVER_ACL` | Hosts to allow api access from, ip address or cidr (should allow certbot) | |
| `PDNS_API_KEY` | API key, should match one configured for certbot | |
| `PDNS_API_KEY_FILE` | Same as previous, for use with docker secrets | |
| `PDNS_AXFR_DISABLE` | Disallow zone transfers; `yes` or `no`, should be enabled on slave | `yes` |
| `PDNS_AXFR_ACL` | Allow zone transfers from given ip address or cidr, should be slave's address | |
| `PDNS_LOG_LEVEL` | Integer value between 1-6, see powerdns docs | |

