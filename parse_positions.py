import dataclasses
import os
import random
import time
from dataclasses import dataclass
from pathlib import Path
import requests, json
from requests import JSONDecodeError

BASE_PATH = Path(__file__).resolve().parent
PROXIES_PATH = BASE_PATH / "proxies.json"

HEADERS = {
    "Cache-Control": "no-cache",
}

BODY = {
    "encryptedUid": "",
    "tradeType": "PERPETUAL",
}

API = "https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getOtherPosition"


traders = {}
with open('traders.json', 'r') as f:
    traders = json.load(f)


proxy_list = []
if PROXIES_PATH.exists():
    with open('proxies.json') as f:
        proxy_list = json.load(f)


def get_body(uuid: str, trade_type: str) -> dict:
    d = BODY.copy()
    d["encryptedUid"] = uuid
    d["tradeType"] = trade_type
    return d


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

positions = []

for v in traders:
    request_kwargs = dict(
        url=API, json=get_body(v['encryptedUid'], v['tradeType']), headers=HEADERS
    )
    # request with proxies
    if proxy_list:
        request_kwargs['proxies'] = {
            'http': random.choice(proxy_list),
            'https': random.choice(proxy_list),
        }

    print(f"{v['encryptedUid']}: {v}: {request_kwargs}")
    r = requests.post(**request_kwargs)

    try:
        data = r.json()['data'].get("otherPositionRetList")
    except JSONDecodeError as err:
        print(r, r.text)
        raise err
    if data:
        for d in data:
            d['uuid'] = uuid
            positions.append(
                dataclasses.asdict(Position(**d))
            )

    if not proxy_list:
        time.sleep(5)

with open('positions.json', 'w') as f:
    json.dump(positions, f, indent='\t')

