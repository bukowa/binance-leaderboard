from .common import new_requests_proxy_setter


def test_new_requests_proxy_setter():
    proxies = ["http://1:1"]
    f = new_requests_proxy_setter(proxies)
    k = {"foo": "bar"}
    assert f(k) == {
        "foo": "bar",
        "proxies": {
            "http": "http://1:1",
            "https": "http://1:1",
        },
    }
