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
            "phone":"55 11 5014 7200",
            "state":"SP",
            "country":"Brazil",
            "companyOfficers":[

            ],
            "website":"http://ri.fleury.com.br",
            "maxAge":1,
            "address1":"Avenida General Valdomiro de Lima, 508",
            "fax":"55 11 5014 7425",
            "industry":"Medical Instruments & Supplies",
            "address2":"Jabaquara",
            "ebitdaMargins":0.27162,
            "profitMargins":0.12558,
            "grossMargins":0.32108003,
            "operatingCashflow":936259968,
            "revenueGrowth":1.049,
            "operatingMargins":0.22238001,
            "ebitda":985603968,
            "targetLowPrice":"None",
            "recommendationKey":"none",
            "grossProfits":809729000,
            "freeCashflow":373194240,
            "targetMedianPrice":"None",
            "currentPrice":24.3,
            "earningsGrowth":"None",
            "currentRatio":0.992,
            "returnOnAssets":0.094060004,
            "numberOfAnalystOpinions":"None",
            "targetMeanPrice":"None",
            "debtToEquity":135.712,
            "returnOnEquity":0.2755,
            "targetHighPrice":"None",
            "totalCash":606268032,
            "totalDebt":2386268928,
            "totalRevenue":3628612096,
            "totalCashPerShare":1.916,
            "financialCurrency":"BRL",
            "revenuePerShare":11.437,
            "quickRatio":0.922,
            "recommendationMean":"None",
            "exchange":"SAO",
            "shortName":"FLEURY      ON      NM",
            "longName":"Fleury S.A.",
            "exchangeTimezoneName":"America/Sao_Paulo",
            "exchangeTimezoneShortName":"BRT",
            "isEsgPopulated":false,
            "gmtOffSetMilliseconds":"-10800000",
            "quoteType":"EQUITY",
            "symbol":"FLRY3.SA",
            "messageBoardId":"finmb_22988815",
            "market":"br_market",
            "annualHoldingsTurnover":"None",
            "enterpriseToRevenue":2.61,
            "beta3Year":"None",
            "enterpriseToEbitda":9.608,
            "52WeekChange":-0.037420392,
            "morningStarRiskRating":"None",
            "forwardEps":1.23,
            "revenueQuarterlyGrowth":"None",
            "sharesOutstanding":316968992,
            "fundInceptionDate":"None",
            "annualReportExpenseRatio":"None",
            "totalAssets":"None",
            "bookValue":5.553,
            "sharesShort":"None",
            "sharesPercentSharesOut":"None",
            "fundFamily":"None",
            "lastFiscalYearEnd":1609372800,
            "heldPercentInstitutions":0.36978,
            "netIncomeToCommon":455692000,
            "trailingEps":1.431,
            "lastDividendValue":"None",
            "SandP52WeekChange":0.28769124,
            "priceToBook":4.376013,
            "heldPercentInsiders":0.4246,
            "nextFiscalYearEnd":1672444800,
            "yield":"None",
            "mostRecentQuarter":1625011200,
            "shortRatio":"None",
            "sharesShortPreviousMonthDate":"None",
            "floatShares":315441697,
            "beta":1.041114,
            "enterpriseValue":9469630464,
            "priceHint":2,
            "threeYearAverageReturn":"None",
            "lastSplitDate":"None",
            "lastSplitFactor":"None",
            "legalType":"None",
            "lastDividendDate":"None",
            "morningStarOverallRating":"None",
            "earningsQuarterlyGrowth":"None",
            "priceToSalesTrailing12Months":2.1226702,
            "dateShortInterest":"None",
            "pegRatio":"None",
            "ytdReturn":"None",
            "forwardPE":19.756096,
            "lastCapGain":"None",
            "shortPercentOfFloat":"None",
            "sharesShortPriorMonth":"None",
            "impliedSharesOutstanding":"None",
            "category":"None",
            "fiveYearAverageReturn":"None",
            "previousClose":24.18,
            "regularMarketOpen":0,
            "twoHundredDayAverage":25.751915,
            "trailingAnnualDividendYield":0.025971878,
            "payoutRatio":0.5098,
            "volume24Hr":"None",
            "regularMarketDayHigh":0,
            "navPrice":"None",
            "averageDailyVolume10Day":2188733,
            "regularMarketPreviousClose":24.18,
            "fiftyDayAverage":24.046858,
            "trailingAnnualDividendRate":0.628,
            "open":0,
            "toCurrency":"None",
            "averageVolume10days":2188733,
            "expireDate":"None",
            "algorithm":"None",
            "dividendRate":0.86,
            "exDividendDate":1628035200,
            "circulatingSupply":"None",
            "startDate":"None",
            "regularMarketDayLow":0,
            "currency":"BRL",
            "trailingPE":16.981133,
            "regularMarketVolume":0,
            "lastMarket":"None",
            "maxSupply":"None",
            "openInterest":"None",
            "marketCap":7702346240,
            "volumeAllCurrencies":"None",
            "strikePrice":"None",
            "averageVolume":1789992,
            "dayLow":0,
            "ask":24.32,
            "askSize":0,
            "volume":0,
            "fiftyTwoWeekHigh":29.81,
            "fromCurrency":"None",
            "fiveYearAvgDividendYield":2.98,
            "fiftyTwoWeekLow":0,
            "bid":24.31,
            "tradeable":false,
            "dividendYield":0.0355,
            "bidSize":0,
            "dayHigh":0,
            "regularMarketPrice":24.3,
            "logo_url":"https://logo.clearbit.com/ri.fleury.com.br"
        }
    """
    ticker = yf.Ticker(symbol)
    return ticker.info


def download_icon(symbol):
    """  
    A crawler from: https://pro.clear.com.br/src/assets/symbols_icons/FLRY.png
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
