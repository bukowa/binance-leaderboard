#!/bin/bash
set -e

: "${SQUID_USER:?}"; : "${SQUID_PASS:?}"
htpasswd -c -b /etc/squid/passwd "$SQUID_USER" "$SQUID_PASS" &> /dev/null

set -x
squid -f /etc/squid/squid.conf -NCd 1 "$@"
