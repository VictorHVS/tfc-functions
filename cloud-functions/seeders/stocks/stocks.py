import csv
import json
import os

import pandas as pd
import yfinance as yf

_header = (
    "symbol", "shortName", "currency", "exchange", "sector", "industry", "website", "longBusinessSummary",
    "logo_url", "city", "state", "country"
)

filename = f'{os.path.dirname(__file__)}/company_stock_info.csv'
symbols_with_error = f'{os.path.dirname(__file__)}/symbols_with_error.csv'


def extract_to_dict():
    df = pd.read_csv(f'{os.path.dirname(__file__)}/stocks.csv', delimiter=";")
    return df.query('mic_code == "BVMF"').to_dict(orient='records')


def populate_csv_file():
    with open(filename, 'a', encoding='utf-8') as csvfile:
        fieldnames = _header

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        stocks = extract_to_dict()
        counter = 0
        for stock in stocks:
            counter += 1

            print(f"checking {stock['symbol']}")
            stock_saved = pd.read_csv(filename, delimiter=";") \
                .query(f'symbol == "{stock["symbol"]}"') \
                .to_dict(orient='records') \
                .__len__()

            stock_with_error = pd.read_csv(symbols_with_error, delimiter=";") \
                .query(f'symbol == "{stock["symbol"]}"') \
                .to_dict(orient='records') \
                .__len__()

            if stock_saved or stock_with_error:
                continue

            info = yf.Ticker(f"{stock['symbol']}.SA").info
            try:
                doc = {
                    'symbol': stock['symbol'],
                    'shortName': info['shortName'],
                    'currency': info['currency'],
                    'exchange': info['exchange'],
                    'sector': info['sector'],
                    'industry': info['industry'],
                    'website': info['website'],
                    'longBusinessSummary': info['longBusinessSummary'],
                    'city': info['city'],
                    'state': info['state'],
                    'logo_url': info['logo_url'],
                    'country': info['country']
                }
                writer.writerow(doc)
                print(counter, stock['symbol'], 'with success')
            except Exception as err:
                print(counter, stock['symbol'], 'with error', err)
                with open(symbols_with_error, 'a', encoding='utf-8') as csverrorfile:
                    rescue_writer = csv.DictWriter(csverrorfile, fieldnames=['symbol', 'field'], delimiter=";")
                    rescue_writer.writerow({'symbol': stock['symbol'], 'field': err})


def stocks_to_json():
    df = pd.read_csv(filename, delimiter=";")
    return json.loads(df.to_json(orient='records'))


if __name__ == '__main__':
    print(stocks_to_json())
    # populate_csv_file()
