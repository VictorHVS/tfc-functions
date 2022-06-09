import os
from twelvedata import TDClient

API_KEY = os.environ["API_TWELVEDATA"]
td = TDClient(apikey=API_KEY)


def get_tickers():
    return [
        {'symbol': 'AAPL', 'name': 'Apple Inc', 'currency': 'USD', 'exchange': 'NASDAQ', 'country': 'United States',
         'type': 'Common Stock'}
    ]


def update_price(symbol=None, exchange=None, country=None):
    time_series = td.time_series(symbol=symbol, exchange=exchange, country=country,
                                 interval="1day",
                                 outputsize=8).as_json()

    week = []
    for item in time_series:
        week.append(float(item["close"]))

    price = week[0]
    price_absolute_flutuation = week[0] - week[1]
    price_flutuation = price_absolute_flutuation / week[1] * 100
    return week, price, price_flutuation, price_absolute_flutuation


def execute(context, event):
    pass


for ticker in get_tickers():
    # td.get_profile(symbol=ticker["symbol"], exchange=ticker["exchange"], country=ticker["country"]).as_json()
    week, last_price, price_fluctuation, price_absolute_fluctuation = update_price(symbol=ticker["symbol"],
                                                                                   exchange=ticker["exchange"],
                                                                                   country=ticker["country"])

    print(week, last_price, price_fluctuation, price_absolute_fluctuation)
