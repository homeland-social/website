FROM haproxytech/haproxy-alpine:2.6

ADD ./docker/haproxy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["haproxy", "-f", "/usr/local/etc/haproxy/haproxy.cfg"]
