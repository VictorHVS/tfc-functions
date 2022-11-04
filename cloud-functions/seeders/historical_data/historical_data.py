import csv
import os

import pandas as pd
import yfinance as yf

from seeders.model import TimeSeries

periods_intervals = [
    {
        "period": "1d",
        "interval": "30m"
    },
    {
        "period": "5d",
        "interval": "60m"
    },
    # {
    #     "period": "1mo",
    #     "interval": "1d"
    # },
    {
        "period": "ytd",
        "interval": "1d"
    },
]


def time_series_to_dict(symbol, period="1d"):
    df = pd.read_csv(f'{os.path.dirname(__file__)}/time_series/{symbol}_{period}.csv', delimiter=";")
    return df.to_dict(orient='records')


def stock_list():
    df = pd.read_csv(f'{os.path.dirname(__file__)}/stocks.csv', delimiter=";")
    return df.to_dict(orient='records')


def fetch_data_frame(symbol, period="1d", interval="30min"):
    return yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers=symbol,

        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        period=period,

        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval=interval,

        # group by ticker (to access via data['SPY'])
        # (optional, default is 'column')
        group_by='ticker',

        # adjust all OHLC automatically
        # (optional, default is False)
        auto_adjust=True,

        # download pre/post regular market hours data
        # (optional, default is False)
        prepost=False,

        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads=True,

        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy=None
    ).to_dict(orient='index')


def has_header(filename):
    try:
        pd.read_csv(filename, encoding='ISO-8859-1')
        return True
    except:
        return False


def check_register(filename, key):
    try:
        result = pd.read_csv(filename, delimiter=";") \
            .query(f'datetime == "{key}"') \
            .to_dict(orient='records') \
            .__len__()

        return result > 0
    except:
        return False


def save_historical_data():
    stocks = stock_list()

    count = 0
    total = len(stocks)
    for stock in stocks:
        folder_name = "{parent}/time_series/".format(parent=os.path.dirname(__file__))
        count += 1
        print("###====================================================================================###")
        print(stock["symbol"], count, "de", total)
        for period in periods_intervals:
            print(period)
            filename = f"{folder_name}{stock['symbol']}_{period['interval']}.csv"
            with open(filename, 'a', encoding='utf-8') as csvfile:
                fieldnames = (
                    "uuid",
                    "datetime",
                    "timezone",
                    "stock_uuid",
                    "interval",
                    "currency",
                    "exchange_uuid",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                )
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")

                if not has_header(filename):
                    writer.writeheader()

                df = fetch_data_frame(
                    symbol=f"{stock['symbol']}{stock['exchange']}",
                    period=period['period'],
                    interval=period['interval']
                )

                print(f"total of records: {len(df.items())}")
                for key in df:
                    if check_register(filename=filename, key=key):
                        continue

                    item = df[key]
                    time_serie = TimeSeries(
                        uuid=int(key.value / 1_000_000),
                        datetime=key,
                        timezone="America/Sao_Paulo",
                        stock_uuid=f"{stock['symbol']}{stock['exchange']}",
                        interval=period['interval'],
                        currency=stock['currency'],
                        exchange_uuid=stock['exchange'],
                        open=item["Open"],
                        close=item["Close"],
                        high=item["High"],
                        low=item["Low"],
                        volume=item["Volume"],
                    )
                    writer.writerow(time_serie.to_dict())


if __name__ == '__main__':
    save_historical_data()
