import requests

api_url = "https://api.binance.com/api/v3"


def get_symbols(params=None):
    return requests.get("%s/exchangeInfo" % api_url, params=params).json()['symbols']


def get_24h(params=None):
    return requests.get("%s/ticker/24hr" % api_url, params=params).json()


def get_order_book(params=None):
    return requests.get("%s/depth" % api_url, params=params).json()
