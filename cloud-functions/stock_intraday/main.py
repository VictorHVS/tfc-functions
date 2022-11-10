import asyncio
import logging
import os
from functools import reduce

import sentry_sdk
import yfinance as yf
from google.cloud import firestore
from sentry_sdk.integrations.gcp import GcpIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[
        GcpIntegration(timeout_warning=True)
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1,
)


async def save(db, transaction, collection, uuid, document):
    result_ref = db.document(f"{collection}/{uuid}")
    if transaction:
        await transaction.set(result_ref, document)
    else:
        await result_ref.set(document)

    logging.info('%s saved in %s collection', uuid, collection)


def fetch_data_frame(symbols, period="1d", interval="30min"):
    return yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers=symbols,

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
    )


def fetch_stocks(stock_len):
    db = firestore.Client()
    return db.collection("stocks") \
        .where("enabled", "==", True) \
        .order_by("updated_at", direction=firestore.Query.ASCENDING) \
        .limit(stock_len) \
        .get()


def save_time_series(db, stock, df, interval):
    path = f"stocks/{stock.id}/{interval}"
    stock_dict = stock.to_dict()

    tasks = []
    for key in df:
        time_series = df[key]

        doc = {
            u'uuid': str(int(key.value / 1_000_000)),
            u'datetime': str(key),
            u'timezone': "America/Sao_Paulo",
            u'stock_uuid': stock.id,
            u'exchange_uuid': str(stock_dict["exchange_id"]),
            u'interval': str(interval),
            u'currency': str(stock_dict["currency"]),
            u'open': float(time_series["Open"]),
            u'high': float(time_series["High"]),
            u'low': float(time_series["Low"]),
            u'close': float(time_series["Close"]),
            u'volume': float(time_series["Volume"]),
        }

        tasks.append(
            save(
                db=db,
                transaction=None,
                collection=path,
                uuid=doc["uuid"],
                document=doc
            )
        )
    return tasks


async def update_stock_price(db, stock, df):
    prices = list(map(lambda price: round(price, 2), df.Close.values))

    if len(prices) == 0:
        fields = {
            "enabled": False,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        logging.warning("%s deactivated", stock.id)
    elif len(prices) > 1:
        fields = {
            "price": prices[-1],
            "price_flutuation": round((prices[-1] / prices[-2] - 1) * 100, 2),
            "price_absolute_flutuation": round(prices[-1] - prices[-2], 2),
            "week": prices,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
    else:
        fields = {
            "price": prices[-1],
            "price_flutuation": 0,
            "price_absolute_flutuation": 0,
            "week": prices,
            "updated_at": firestore.SERVER_TIMESTAMP
        }

    logging.info("saving", stock.id)
    await db.collection("stocks").document(stock.id).update(fields)


async def crawl_stock_price(stocks_dict, period, interval):
    try:
        db = firestore.AsyncClient()
        symbols_list = reduce(lambda a, b: a + " " + b.to_dict()["uuid"], stocks_dict, "")
        logging.info(symbols_list)
        df_time_series = fetch_data_frame(symbols=symbols_list, period=period, interval=interval)
        general_df_time_series = fetch_data_frame(symbols=symbols_list, period="5d", interval="1d")

        tasks = []
        for stock in stocks_dict:
            logging.info(stock.id)
            tasks += save_time_series(
                db=db,
                stock=stock,
                df=df_time_series[stock.id].to_dict(orient='index'),
                interval=interval
            )

            tasks.append(
                update_stock_price(
                    db=db,
                    stock=stock,
                    df=general_df_time_series[stock.id]
                )
            )
            logging.info('%s saved!', stock.id)
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(e)
        sentry_sdk.capture_exception(e)


def entry_point(event, context):
    period = str(event["attributes"]["period"])
    interval = str(event["attributes"]["interval"])
    stock_len = int(event["attributes"]["stock_len"])

    import time
    s = time.perf_counter()
    stocks_dict = fetch_stocks(stock_len)

    asyncio.run(crawl_stock_price(stocks_dict, period, interval))

    elapsed = time.perf_counter() - s
    logging.info(f"{__file__} executed in {elapsed:0.2f} seconds.")
