# website-haproxy docker image

This image contains the configuration for haproxy used by the website. However, additional features and configuration are merged from the homeland social conduit project. You can see an example of how the final haproxy image is built here:

[https://github.com/homeland-social/deploy/blob/master/docker/haproxy/Dockerfile](https://github.com/homeland-social/deploy/blob/master/docker/haproxy/Dockerfile)

## Using this image

```bash
$ docker run -ti homelandsocial/website-haproxy
```

### Example docker-compose

[https://raw.githubusercontent.com/homeland-social/website/master/docker-compose.yml](https://raw.githubusercontent.com/homeland-social/website/master/docker-compose.yml)

## Volumes

| Path | Description |
| ---- | ----------- |
| `/usr/local/etc/haproxy/certificates/` | Where combined certificates are stored (should be shared with certbot `/etc/certificates`) |
| `/usr/local/etc/haproxy/haproxy.cfg` | Config if you wish to override it |
