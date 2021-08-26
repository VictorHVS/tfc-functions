#!/usr/bin/env python
# coding: utf-8

from twelvedata import TDClient
from twelvedata.http_client import DefaultHttpClient


API_URL = 'https://api.twelvedata.com'
td = TDClient(apikey="1777123baf4e4cd2af3dbe16460361d6")


def test_get_stocks_list():
    """[summary]
    [
        {
            "symbol":"TRAD3",
            "name":"TC Traders Club S.A.",
            "currency":"BRL",
            "exchange":"Bovespa",
            "country":"Brazil",
            "type":"EQUITY"
        },

        {
            "symbol":"TORD11",
            "name":"Tordesilhas Ei Fundo De Investimento Imobiliario",
            "currency":"BRL",
            "exchange":"Bovespa",
            "country":"Brazil",
            "type":"Common"
        }
    ]

    Returns:
        [type]: [description]
    """
    return td.get_stocks_list(exchange='Bovespa').as_json()
    # print(td.get_stock_exchanges_list().as_json())


def get_tickers():
    pass
    # {{BASE_URL}}/exchanges/BVMF/tickers?access_key={{API_KEY}}&limit=1757


list = test_get_stocks_list()
print(list)
