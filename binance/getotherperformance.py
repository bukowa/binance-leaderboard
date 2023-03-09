#!/usr/bin/env python3
import logging
from dataclasses import dataclass, asdict
from enum import Enum

import requests

from common.common import load_json, save_json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def parse_performance(
    traders_file="traders_with_position.json", file_out="traders_performance.json"
):
    traders = load_json(traders_file)

    performances = []
    for trader in traders:
        api = API(uid=trader["encryptedUid"], trade_type=trader["tradeType"])
        logger.info(f"request: {api.uid} {api.trade_type}")

        data = api.requests_post().json()
        perf = TraderPerformance.from_json(
            uid=trader["encryptedUid"],
            data=data,
        )
        performances.append(asdict(perf))

    save_json(file_out, performances, indent="\t")


class PeriodType(Enum):
    ALL = "ALL"
    YEARLY = "YEARLY"
    EXACT_YEARLY = "EXACT_YEARLY"


class StatisticsType(Enum):
    ROI = "ROI"
    PNL = "PNL"


@dataclass
class Performance:
    periodType: str
    statisticsType: str
    value: float
    rank: int


@dataclass
class TraderPerformance:
    uid: str
    performanceRetList: list[Performance]
    lastTradeTime: int

    @classmethod
    def from_json(cls, uid: str, data: dict):
        data = data["data"]
        return cls(
            uid=uid,
            lastTradeTime=data["lastTradeTime"],
            performanceRetList=[Performance(**p) for p in data["performanceRetList"]],
        )


class API:
    URL = "https://www.binance.com/bapi/futures/v2/public/future/leaderboard/getOtherPerformance"
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, uid: str, trade_type="PERPETUAL"):
        self.uid = uid
        self.trade_type = trade_type

    @property
    def requests_body(self):
        return {
            "tradeType": self.trade_type,
            "encryptedUid": self.uid,
        }

    @property
    def requests_kwargs(self):
        return {
            "url": self.URL,
            "json": self.requests_body,
            "headers": self.HEADERS,
        }

    def requests_post(self):
        return requests.post(**self.requests_kwargs)


if __name__ == "__main__":
    parse_performance(
        traders_file="traders_with_position.json", file_out="traders_performance.json"
    )
