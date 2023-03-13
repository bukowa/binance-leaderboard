#!/usr/bin/env python3
import logging
import os
import sys
from dataclasses import dataclass, asdict

import requests
from requests import JSONDecodeError

from common.common import save_json, new_requests_proxy_setter, load_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def parse_positions(
    file="positions.json", file_traders="traders_with_position.json", proxies=None
):
    proxy_setter = new_requests_proxy_setter(proxies)
    traders = load_json(file_traders)
    positions = []
    for trader in traders:
        api = API(
            uid=trader["encryptedUid"],
            trade_type=trader["tradeType"],
        )

        try:
            logger.info(f"position request: {api.uid} {api.trade_type}")
            resp = api.requests_post(**proxy_setter({}))
            data = resp.json()["data"].get("otherPositionRetList")
        except JSONDecodeError as err:
            logger.info(resp.text)
            raise err
        else:
            if data:
                for d in data:
                    d["uuid"] = trader["encryptedUid"]
                    d["tradeType"] = trader["tradeType"]
                    pos = Position(**d)
                    positions.append(pos)
                    logger.info(f"position result: {pos}")

    save_json(file, [asdict(p) for p in positions], indent="\t")


@dataclass
class Position:
    symbol: str
    entryPrice: float
    markPrice: float
    pnl: float
    roe: float
    updateTime: list
    amount: float
    updateTimeStamp: int
    yellow: bool
    tradeBefore: bool
    leverage: int
    uuid: str
    tradeType: str


class API:
    URL = "https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getOtherPosition"
    HEADERS = {"Cache-Control": "no-cache", "content-type": "application/json"}

    def __init__(self, uid: str, trade_type="PERPETUAL"):
        self.uid = uid
        self.trade_type = trade_type

    @property
    def requests_body(self):
        return {"encryptedUid": self.uid, "tradeType": self.trade_type}

    @property
    def requests_kwargs(self):
        return {
            "url": self.URL,
            "json": self.requests_body,
            "headers": self.HEADERS,
        }

    def requests_post(self, **kwargs):
        defaults = self.requests_kwargs
        defaults.update(kwargs)
        return requests.post(**defaults)

    def requests_data(self, **kwargs):
        return self.requests_post(**kwargs).json()["data"].get("otherPositionRetList")


if __name__ == "__main__":
    _proxies = None
    if len(sys.argv) > 1:
        _proxies = sys.argv[1]
    else:
        if os.path.isfile('proxies.json'):
            _proxies = 'proxies.json'

    # get positions only for good traders
    save_json('good_traders.json', [t for t in load_json('traders.json') if t.get('pnl') and t['pnl'] > 100000], indent='\t')
    parse_positions(
        file="positions.json",
        file_traders="good_traders.json",
        proxies=_proxies,
    )
