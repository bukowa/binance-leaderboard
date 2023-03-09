import json
from typing import Any

from more_itertools import chunked
import requests
from dataclasses import dataclass, asdict

DEBUG = False


@dataclass
class TraderPositionStatus:
    encryptedUid: str
    positionShared: bool
    hasPosition: bool
    lastTradeTime: int
    tradeType: str
    futureUid: Any = None


def get_position_statuses(file='traders.json'):
    trade_types = ['PERPETUAL', 'DELIVERY']

    with open(file) as f:
        traders = json.load(f)

    position_statuses = []
    for tt in trade_types:
        uuids = [t['encryptedUid'] for t in traders if t['tradeType'] == tt]

        for batch in chunked(uuids, 20):
            for d in API(*batch).requests_post().json()['data']:
                d['tradeType'] = tt
                position_statuses.append(TraderPositionStatus(**d))

    return position_statuses


def get_traders_with_position(file='traders.json'):
    trade_types = ['PERPETUAL', 'DELIVERY']

    with open(file) as f:
        traders = json.load(f)

    position_statuses = get_position_statuses(file)

    desired_traders = []
    for tt in trade_types:
        uuids_with_positions = {
            x.encryptedUid for x in filter(lambda x: all([x.hasPosition, x.positionShared, x.tradeType == tt]), position_statuses)
        }
        desired_traders.extend(filter(lambda t: t['encryptedUid'] in uuids_with_positions, traders))

    return desired_traders


def save_traders_with_position():
    with open('traders_with_position.json', 'w') as f:
        json.dump(get_traders_with_position(), f, indent='\t')


class API:
    URL = 'https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getPositionStatus'
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, *uuid: str, trade_type="PERPETUAL"):
        self.uuids = uuid
        self.trade_type = trade_type

    @property
    def requests_body(self):
        return {
            'tradeType': self.trade_type,
            'encryptedUidList': list(self.uuids),
        }

    @property
    def requests_kwargs(self):
        return {
            'url': self.URL,
            'json': self.requests_body,
            'headers': self.HEADERS,
        }

    def requests_post(self):
        return requests.post(**self.requests_kwargs)


if __name__ == '__main__':
    save_traders_with_position()

