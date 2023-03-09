#!/usr/bin/env python3
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any

import requests

from common.common import save_json, load_json_default


@dataclass
class Trader:
    futureUid: Any
    nickName: str
    userPhotoUrl: str
    rank: int
    pnl: float
    roi: float
    positionShared: bool
    twitterUrl: str
    encryptedUid: str
    updateTime: int
    followerCount: int
    twShared: bool
    isTwTrader: bool
    openId: str
    tradeType: str

    def __hash__(self):
        return hash(self.nickName + self.tradeType)

    def __eq__(self, other):
        return self.nickName + self.tradeType == other.nickName + self.tradeType


class Filter:
    key = None

    @classmethod
    def members(cls):
        return filter(lambda x: x.name != "key", cls.__members__.values())


class TradeType(Filter, Enum):
    key = "tradeType"
    USD_M = "PERPETUAL"
    COIN_M = "DELIVERY"


class PeriodType(Filter, Enum):
    key = "periodType"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    TOTAL = "ALL"


class IsTrader(Filter, Enum):
    key = "isTrader"
    CopyTrading = "true"
    ALL = "false"


class IsShared(Filter, Enum):
    key = "isShared"
    YES = "true"
    NO = "false"


class StatisticsType(Filter, Enum):
    key = "statisticsType"
    ROI = "ROI"
    PNL = "PNL"


def unique_filters(*filters):
    """
    Takes any number of filter objects as input and returns a list of unique filters
    (one filter of each type).
    """
    return list({type(f): f for f in filters}.values())


def get_request_body(*filters) -> dict:
    """
    Takes any number of filter objects as input and returns a dictionary representing
    the request body for the Binance API call.
    """
    return {f.key.value: f.value for f in unique_filters(*filters)}


def get_apis_for_all_traders() -> list["API"]:
    """
    Creates and returns a list of API objects for all possible
    combinations of TradeType, IsTrader, PeriodType, StatisticsType.
    """
    apis = []
    for tt in TradeType.members():
        api_trade_type = API(tt)
        for st in StatisticsType.members():
            api_stat_type = api_trade_type(st)
            for it in IsTrader.members():
                api_is_trader = api_stat_type(it)
                for pt in PeriodType.members():
                    api = api_is_trader(pt)
                    apis.append(api)
    return apis


def get_traders(*api: "API"):
    traders = []
    for a in api:
        trade_type = a.requests_body[TradeType.key.value]
        for each in a.requests_post().json()["data"]:
            each["tradeType"] = trade_type
            traders.append(Trader(**each))
    return traders


def get_unique_traders(*api: "API"):
    return list(set(get_traders(*api)))


def parse_traders(*api: "API", file="traders.json"):
    old_traders = [Trader(**d) for d in load_json_default(file, [])]
    old_traders.extend(get_unique_traders(*api))
    save_json(file, list(map(asdict, set(old_traders))), indent="\t")


def parse_all_traders(file="traders.json"):
    return parse_traders(*get_apis_for_all_traders(), file=file)


class API:
    """
    Class for making API calls to the Binance futures leaderboard endpoint. Takes any
    number of filter objects as input and filters the leaderboard data according to
    the specified filters.
    """

    URL = "https://www.binance.com/bapi/futures/v3/public/future/leaderboard/getLeaderboardRank"
    HEADERS = {"content-type": "application/json"}

    DEFAULT_FILTERS = {
        TradeType.USD_M,
        PeriodType.WEEKLY,
        IsTrader.ALL,
        IsShared.YES,
        StatisticsType.ROI,
    }

    def __init__(self, *filters: Filter):
        """
        Initializes an API object with the specified filters. If no filters are specified,
        uses the default filters.
        """
        self.filters = unique_filters(*self.DEFAULT_FILTERS, *filters)

    def __call__(self, *filters: Filter):
        """
        Returns a new API object with the specified filters added to the existing filters.
        """
        return API(*unique_filters(*self.filters, *filters))

    @property
    def requests_body(self):
        """
        Returns the request body for the API call, generated from the current set of filters.
        """
        return get_request_body(*self.filters)

    @property
    def requests_kwargs(self):
        """
        Returns a dictionary containing the arguments to be passed to the `requests.post()`
        function when making the API call. Includes the URL, request body, and headers.
        """
        return dict(
            url=self.URL,
            json=self.requests_body,
            headers=self.HEADERS,
        )

    def requests_post(self, **kwargs):
        """
        Makes a POST request to the Binance API with the current set of filters and any
        additional keyword arguments passed in. Returns the response from the API call.
        """
        k = self.requests_kwargs
        k.update(kwargs)
        return requests.post(**k)


if __name__ == "__main__":
    parse_all_traders(file="traders.json")
