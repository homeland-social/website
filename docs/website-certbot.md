# website-certbot

This image contains integration between letsencrypt and our haproxy image. This allows all configured domains to utilize SSL automatically.

## Using this image

```bash
$ docker run -ti homelandsocial/website-certbot
```

### Example docker-compose

[https://raw.githubusercontent.com/homeland-social/website/master/docker-compose.yml](https://raw.githubusercontent.com/homeland-social/website/master/docker-compose.yml)

## Environment variables

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

## Volumes

| Path | Description |
| ---- | ----------- |
| `/etc/certificates` | Where combined certificates are stored for haproxy |
| `/etc/letsencrypt/live` | Where certbot state is stored |
