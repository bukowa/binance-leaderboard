import json
import os
import random
from typing import Callable, Union

TRADE_TYPES = ("PERPETUAL", "DELIVERY")


def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


def load_json_default(filename, default, **kwargs):
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            return json.load(f, **kwargs)
    return default


def save_json(filename, obj, **kwargs):
    with open(filename, "w") as f:
        json.dump(obj, f, **kwargs)


def load_proxies_from_file(filename="proxies.json"):
    return load_json(filename)


def requests_set_proxies(proxies: list[str], request_kwargs):
    """
    proxies in format; http://login:pass@ip:port
    """
    if proxies:
        request_kwargs.update(
            dict(
                proxies={
                    "http": random.choice(proxies),
                    "https": random.choice(proxies),
                }
            )
        )
    return request_kwargs


def new_requests_proxy_setter(proxies="proxies.json") -> Callable[[dict], dict]:
    """
    returns function used to set proxies for requests kwargs
    """

    if not proxies:
        return lambda x: {}

    if isinstance(proxies, str):
        proxies = load_proxies_from_file(proxies)
    elif isinstance(proxies, list):
        ...
    else:
        raise Exception("invalid proxies type")

    def func(kwargs):
        return requests_set_proxies(proxies, kwargs)

    return func
