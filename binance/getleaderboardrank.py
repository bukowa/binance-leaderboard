from enum import Enum
import requests


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


def get_request_body(*filters):
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
