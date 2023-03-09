from dataclasses import dataclass, asdict
from enum import Enum

import requests


class PeriodType(Enum):
    ALL = 'ALL'
    YEARLY = 'YEARLY'
    EXACT_YEARLY = 'EXACT_YEARLY'


class StatisticsType(Enum):
    ROI = 'ROI'
    PNL = 'PNL'


@dataclass
class Performance:
    periodType: str
    statisticsType: str
    value: float
    rank: int


@dataclass
class TraderPerformance:
    performanceRetList: list[Performance]
    lastTradeTime: int

    @classmethod
    def from_json(cls, data: dict):
        data = data['data']
        return cls(
            lastTradeTime=data['lastTradeTime'],
            performanceRetList=[Performance(**p) for p in data['performanceRetList']]
        )


class API:
    URL = 'https://www.binance.com/bapi/futures/v2/public/future/leaderboard/getOtherPerformance'
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, uid: str, trade_type='PERPETUAL'):
        self.uid = uid
        self.trade_type = trade_type

    @property
    def requests_body(self):
        return {
            'tradeType': self.trade_type,
            'encryptedUid': self.uid,
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
    r = API('44D4C25384E64DA0D49E8FE6F21B9706').requests_post()
    p = TraderPerformance.from_json(r.json())
