FROM alpine

RUN apk update
RUN apk add \
    apache2-utils \
    squid \
    bash

COPY squid.conf /etc/squid/squid.conf
EXPOSE 3128

COPY squid.entrypoint.sh /sbin/squid.entrypoint.sh
ENTRYPOINT ["/sbin/squid.entrypoint.sh"]
