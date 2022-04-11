![docker image](https://github.com/homeland-social/website/actions/workflows/docker-image.yml/badge.svg) [![Documentation Status](https://readthedocs.org/projects/homeland-social-website/badge/?version=latest)](https://homeland-social-website.readthedocs.io/en/latest/?badge=latest) ![Docker Pulls](https://img.shields.io/docker/pulls/homelandsocial/website-final) ![Docker Image Version (latest by date)](https://img.shields.io/docker/v/homelandsocial/website-final)
# www.homeland-social.com

Website for [www.homeland-social.com](https://www.homeland-social.com/)

This repository contains all of the source code and configuration for the homeland social website. You can make pull requests here to release new features or fix bugs. You can also use this code or the docker images to run your own copy of this website.

## Run your own site

The easiest way to run your own copy of this site is to utilize the docker images.

An example stack file is located below. 

[https://github.com/homeland-social/deploy/blob/master/docker/homeland-social.yml](https://github.com/homeland-social/deploy/blob/master/docker/homeland-social.yml)

This stack file makes use of the following images, as well as some supporting services such as redis, postgres etc. The Homeland social conduit project also provides a number of images that are integrated with the website.

[https://github.com/homeland-social/conduit/](https://github.com/homeland-social/conduit/)

### website-final

This image contains the website frontend (vue.js) backend (django) and static files. Everything is served by uWSGI and meant to be behind a proxy. Haproxy is used for this purpose. Several additional commands are supported.

#### Environment variables

| Name | Description | Default |
| ------ | ----------- | ------- |
| `DJANGO_DB_NAME` | Postgres database name | `shanty` |
| `DJANGO_DB_HOST` | Postgres server address | `db` |
| `DJANGO_DB_USER` | Postgres user name | `shanty` |
| `DJANGO_DB_PASSWORD` | Postgres password | |
| `DJANGO_DB_PASSWORD_FILE` | Same as previous, for use with docker secrets | |
| `DJANGO_REDIS_HOST` | Redis server address | `redis` |
| `DJANGO_REDIS_PORT` | Redis server port | `6379` |
| `DJANGO_HOST` | Address to bind to | `0.0.0.0` |
| `DJANGO_PORT` | Port to bind to | `8000` |
| `DJANGO_ALLOWED_HOSTS` | Valid domains to use with django, comma separated | `localhost` |
| `DJANGO_DEBUG` | Enable django debug mode `true` or `false` | `false` |
| `DJANGO_SECRET_KEY` | Django secret key | |
| `DJANGO_SECRET_KEY_FILE` | Same as previous, for use with docker secrets | |
| `DJANGO_EMAIL_BACKEND` | Email backend to use | `django.core.mail.backends.console.EmailBackend` |
| `DJANGO_MAILJET_API_KEY` | Mailjet api key when using `django_mailjet.backends.MailjetBackend` backend | |
| `DJANGO_MAILJET_API_KEY_FILE` | Same as previous, for use with docker secrets | |
| `DJANGO_MAILJET_API_SECRET` | Mailjet api key when using `django_mailjet.backends.MailjetBackend` backend | |
| `DJANGO_MAILJET_API_SECRET_FILE` | Same as previous, for use with docker secrets | |
| `DJANGO_RECAPTCHA_SECRET_KEY` | Recaptcha api key | |
| `DJANGO_RECAPTCHA_SECRET_KEY_FILE` | Same as previous, for use with docker secrets | |

Several additional commands are supported. These will run something other than the uWSGI webserver (the default command).

#### Command `migrate`

Runs Django migrations.

#### Command `celery`

Runs celery job worker.

In addition to the above settings, you can define the following celery-specific options.

##### Environment variables

| Name | Description | Default |
| ------ | ----------- | ------- |
| `CELERY_BEAT_SCHEDULER` | Celery beat scheduler to use | |

#### Command `beat`

Runs celery beat scheduler.

In addition to the above settings, you can define the following celery-specific options.

##### Environment variables

| Name | Description | Default |
| ------ | ----------- | ------- |
| `CELERY_BEAT_SCHEDULER` | Celery beat scheduler to use | |

### website-haproxy

This image contains the configuration for haproxy used by the website. However, additional features and configuration are merged from the homeland social conduit project. You can see an example of how the final haproxy image is built here:

[https://github.com/homeland-social/deploy/blob/master/docker/haproxy/Dockerfile](https://github.com/homeland-social/deploy/blob/master/docker/haproxy/Dockerfile)

#### Volumes

| Path | Description |
| ---- | ----------- |
| `/usr/local/etc/haproxy/certificates/` | Where combined certificates are stored (should be shared with certbot `/etc/certificates`) |
| `/usr/local/etc/haproxy/haproxy.cfg` | Config if you wish to override it |

### website-certbot

This image contains integration between letsencrypt and our haproxy image. This allows all configured domains to utilize SSL automatically.

#### Environment variables

| Name | Description | Default |
| ------ | ----------- | ------- |
| `HAPROXY_HOST` | Container / service name for haproxy | `haproxy` |
| `HAPROXY_PORT` | Port used for admin socket, see haproxy.cfg | `9999` |
| `PDNS_HOST` | Container / service name for dns master | `haproxy` |
| `PDNS_PORT` | Port used for powerdns api | `8081` |
| `PDNS_API_KEY` | powerdns api key | |
| `PDNS_API_KEY_FILE` | Same as previous, used with docker secrets | |
| `CERTBOT_EMAIL` | Email address for letsencrypt account | |
| `CERTBOT_DOMAINS` | Domains to obtain certificates for, comma separated | |
| `CERTBOT_SHARED_DOMAINS` | Domains to obtain wildcard certificates for, comma separated | |
| `CERTBOT_EXTRA_ARGS` | Any extra arguments to pass to certbot | |

#### Volumes

| Path | Description |
| ---- | ----------- |
| `/etc/certificates` | Where combined certificates are stored for haproxy |
| `/etc/letsencrypt/live` | Where certbot state is stored |

### website-dns

This image contains powerdns configured via environment variables. You can set up a slave and / or master server using postgres or sqlite.

#### Environment variables

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

## Pull requests

Make a pull request in the usual way. Once merged, new docker images will be automatically published. However, deploys to the website are handled in another repository [https://github.com/homeland-social/deploy/](https://github.com/homeland-social/deploy/).