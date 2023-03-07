FROM ubuntu
ARG SQUID_VERSION=5.2-1ubuntu4

RUN apt update
RUN apt install -y \
    apache2-utils \
    squid=$SQUID_VERSION \
    && rm -rf /var/lib/apt/lists/*

COPY squid.conf /etc/squid/squid.conf
EXPOSE 3128

COPY squid.entrypoint.sh /sbin/squid.entrypoint.sh
ENTRYPOINT ["/sbin/squid.entrypoint.sh"]
