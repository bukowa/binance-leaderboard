import dataclasses
import time
from dataclasses import dataclass

import requests, json
from requests import JSONDecodeError

HEADERS = {
    "Cache-Control": "no-cache",
}

BODY = {
    "encryptedUid": "",
    "tradeType": "PERPETUAL",
}

API = "https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getOtherPosition"


with open('traders.json', 'r') as f:
    traders = json.load(f)


def get_body(uuid: str, typefilter: str) -> dict:
    d = BODY.copy()
    d["encryptedUid"] = uuid
    if typefilter == "UM":
        d['tradeType'] = 'PERPETUAL'
    if typefilter == 'CM':
        d['tradeType'] = 'DELIVERY'
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

for uuid, v in traders.items():
    r = requests.post(API, json=get_body(uuid, v), headers=HEADERS)
    print(f"{uuid}: {v}")
    time.sleep(5)
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

with open('positions.json', 'w') as f:
    json.dump(positions, f, indent='\t')

