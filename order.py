import requests

HEADERS = {
    "Cache-Control": "no-cache",
}

BODY = {
    "encryptedUid": "",
    "tradeType": "PERPETUAL",
}

API = "https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getOtherPosition"

USERS = {
    "RealCryptrader": "765D3AE81B476C4EB14970053C6B8EC3",
}

def get_body(uuid: str) -> dict:
    d = BODY.copy()
    d["encryptedUid"] = uuid
    return d


for k, v in USERS.items():
    r = requests.post(API, json=get_body(v), headers=HEADERS)
    print(f"{k}: {r.json()})")
