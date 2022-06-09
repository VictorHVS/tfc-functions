import os

from twelvedata import TDClient

API_KEY = os.environ["API_TWELVEDATA"]
td = TDClient(apikey=API_KEY)

tickers = [
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


def setup_ticker(ticker):
    profile = td.get_profile(symbol=ticker["symbol"], exchange=ticker["exchange"], country=ticker["country"]).as_json()
    week, last_price, price_fluctuation, price_absolute_fluctuation = update_price(symbol=ticker["symbol"],
                                                                                   exchange=ticker["exchange"],
                                                                                   country=ticker["country"])

    last_week_day = "2021-12-30"
    candle_1d = td.time_series(symbol=ticker['symbol'],
                               exchange=ticker['exchange'],
                               country=ticker['country'],
                               interval="15min",
                               start_date=last_week_day).as_json()

    last_week = "2021-12-20"
    candle_1w = td.time_series(symbol=ticker['symbol'],
                               exchange=ticker['exchange'],
                               country=ticker['country'],
                               interval="15min",
                               start_date=last_week).as_json()

    last_semester = "2021-06-01"
    candle_6m = td.time_series(symbol=ticker['symbol'],
                               exchange=ticker['exchange'],
                               country=ticker['country'],
                               interval="1day",
                               start_date=last_semester).as_json()

    last_semester = "2019-01-01"
    candle_max = td.time_series(symbol=ticker['symbol'],
                                exchange=ticker['exchange'],
                                country=ticker['country'],
                                interval="1day",
                                start_date=last_semester).as_json()

    print(candle_1d)
    print(candle_1w)
    print(candle_6m)
    print(candle_max)


setup_ticker(tickers[0])
