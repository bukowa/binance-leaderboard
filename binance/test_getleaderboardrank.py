from unittest.mock import patch, Mock

from .getleaderboardrank import PeriodType, StatisticsType, API, TradeType


@patch("requests.post")
def test_requests_post(mock_post):
    api = API()
    response = Mock()
    response.status_code = 200
    mock_post.return_value = response
    api.requests_post()
    mock_post.assert_called_once_with(
        url=API.URL,
        json={
            "tradeType": "PERPETUAL",
            "periodType": "WEEKLY",
            "isTrader": "false",
            "isShared": "true",
            "statisticsType": "ROI",
        },
        headers=API.HEADERS,
    )


@patch("requests.post")
def test_requests_post2(mock_post):
    api = API(PeriodType.MONTHLY)
    api = api(StatisticsType.PNL)
    api = api(TradeType.COIN_M)
    response = Mock()
    response.status_code = 200
    mock_post.return_value = response
    api.requests_post()
    mock_post.assert_called_once_with(
        url=API.URL,
        json={
            "tradeType": "DELIVERY",
            "periodType": "MONTHLY",
            "isTrader": "false",
            "isShared": "true",
            "statisticsType": "PNL",
        },
        headers=API.HEADERS,
    )
