#!/usr/bin/env python
# coding: utf-8

import yfinance as yf
from twelvedata import TDClient
from twelvedata.http_client import DefaultHttpClient

import requests # to get image from the web
import shutil


API_URL = 'https://api.twelvedata.com'
td = TDClient(apikey="1777123baf4e4cd2af3dbe16460361d6")


def list_all():
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


def get_ticker_info(symbol):
    """Coletar todas as informações disponíveis sobre uma ação específica e retornar

    Args:
        symbol (str): Código identificador da ação. 
        EXP: FLRY3.SA

    Returns:
        [dict]: dicionário de informações do ticker
        EXP: 
        {
            "zip":"04344-903",
            "sector":"Healthcare",
            "fullTimeEmployees":15000,
            "longBusinessSummary":"Fleury S.A., together with its subsidiaries, provides medical services in the diagnostic, treatment, and clinical analysis, health management, and medical care areas in Brazil. The company operates through three segments: Diagnostic Medicine, Integrated Medicine, and Dental. It offers laboratory and image exam, diagnostic information, check-up and reference laboratory, dental imaging exam, dental radiology, and diagnostic imaging services. As of December 31, 2019, the company had 245 patient service centers and 24 operations in hospitals under the Fleury, Labs a+, Felippe Mattoso, Lafe, a+SP, Campana, Weinman, a+, Serdil, a+ and Diagmax, IRN/ CPC, Diagnosson a+, and Inlab brand names. Fleury S.A. was founded in 1926 and is headquartered in SÃ£o Paulo, Brazil.",
            "city":"SÃ£o Paulo",
            "state":"SP",
            "country":"Brazil",
            "website":"http://ri.fleury.com.br",
            "address1":"Avenida General Valdomiro de Lima, 508",
            "industry":"Medical Instruments & Supplies",
            "currentPrice":24.3,
            "currentRatio":0.992,
            "financialCurrency":"BRL",
            "shortName":"FLEURY      ON      NM",
            "longName":"Fleury S.A.",
            "exchangeTimezoneName":"America/Sao_Paulo",
            "exchangeTimezoneShortName":"BRT",
            "quoteType":"EQUITY",
            "symbol":"FLRY3.SA",
            "ask":24.32,
            "volume":0,
            "bid":24.31,
            "dividendYield":0.0355,
            "bidSize":0,
            "dayHigh":0,
            "logo_url":"https://logo.clearbit.com/ri.fleury.com.br"
        }
    """
    ticker = yf.Ticker(symbol)
    return ticker.get_info()


def download_icon(symbol):
    """  
    A crawler from: https://pro.clear.com.br/src/assets/symbols_icons/FLRY.png
    # TODO
    caso não dê, baixar de: https://portal.novafutura.com.br/views/img/Carteira/FLRY3.png
    """

    name = symbol[:4]
    r = requests.get(f"https://pro.clear.com.br/src/assets/symbols_icons/{name}.png", stream = True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
        
        # Open a local file with wb ( write binary ) permission.
        with open(f"icons/{name}.png",'wb') as f:
            shutil.copyfileobj(r.raw, f)
            
        print('Sucess: ', symbol)
    else:
        print('Failed', symbol)


def mass_icon_download():
    tickers = set()

    for ticker in list_all():
        tickers.add(ticker['symbol'][:4])
    
    for ticker in tickers:
        download_icon(ticker)

    return tickers