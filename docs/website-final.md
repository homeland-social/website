# website-final

This image contains the website frontend (vue.js) backend (django) and static files. Everything is served by uWSGI and meant to be behind a proxy. Haproxy is used for this purpose. Several additional commands are supported.

## Environment variables

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

## Command `migrate`

Runs Django migrations.

## Command `celery`

Runs celery job worker.

In addition to the above settings, you can define the following celery-specific options.

### Environment variables

| Name | Description | Default |
| ------ | ----------- | ------- |
| `CELERY_BEAT_SCHEDULER` | Celery beat scheduler to use | |

## Command `beat`

Runs celery beat scheduler.

In addition to the above settings, you can define the following celery-specific options.

### Environment variables

| Name | Description | Default |
| ------ | ----------- | ------- |
| `CELERY_BEAT_SCHEDULER` | Celery beat scheduler to use | |

