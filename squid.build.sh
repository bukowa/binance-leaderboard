#!/bin/bash
set -e

tag=${DOCKER_TAG:-"dockersquidproxybinanceleaderboardtest"}
docker build --tag=$tag -f squid.Dockerfile .

if [[ "$1" == "copy" ]]
then
  docker run -d --name=$tag $tag
  docker cp $tag:/etc/squid/squid.conf .
  docker rm -f $tag
fi

if [[ "$1" == "run" ]]
then
  docker run --rm -it -p 3128:3128 --entrypoint=/bin/bash $tag
fi

if [[ "$1" == "test" ]]
then
  set -x
  docker run --rm -it -p 3128:3128 \
    -e SQUID_USER=1 -e SQUID_PASS=2 $tag
fi

if [[ "$1" == push ]]
then
  docker tag ${tag} bukowa/squidproxy
  docker push bukowa/squidproxy
fi

