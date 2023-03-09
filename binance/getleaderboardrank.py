import json
import os
from enum import Enum
from typing import Any

import requests
from dataclasses import dataclass, asdict


@dataclass
class Trader:
    """
    {'futureUid': None,
     'nickName': 'Anonymous User-3ded25',
     'userPhotoUrl': '',
     'rank': 816,
     'pnl': 948.743831,
     'roi': 0.934421,
     'positionShared': True,
     'twitterUrl': None,
     'encryptedUid': '35CF2A53D1B9BFD0F948DE7359AED978',
     'updateTime': 1678233600000,
     'followerCount': 10,
     'twShared': True,
     'isTwTrader': True,
     'openId': 'zoh752p'}
    """
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

    def __hash__(self):
        return hash(self.nickName)

    def __eq__(self, other):
        return self.nickName == other.nickName


class Filter:
    key = None

    @classmethod
    def members(cls):
        return filter(lambda x: x.name != 'key', cls.__members__.values())


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


def get_apis_for_all_traders() -> list['API']:
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


def get_traders(*api: 'API'):
    traders = []
    for a in api:
        traders.extend([Trader(**r) for r in a.requests_post().json()['data']])
    return traders


def get_unique_traders(*api: 'API'):
    return list(set(get_traders(*api)))


def parse_traders(*api: 'API', file='traders.json'):
    traders_json = []

    if os.path.isfile(file):
        with open(file, 'r') as f:
            traders_json = json.load(f)

    traders_rank = [Trader(**d) for d in traders_json]
    traders_rank.extend(get_unique_traders(*api))

    with open(file, 'w') as f:
        json.dump(list(map(asdict, set(traders_rank))), f, indent='\t')


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


if __name__ == '__main__':
    parse_traders(*get_apis_for_all_traders(), file="traders.json")
