#!/bin/bash
name='binance-leaderboard'
docker rm -f $name || true
docker run -d -p 4991:4444 --name=$name -e SE_NODE_MAX_SESSIONS=12 --shm-size="2g" selenium/standalone-chrome
