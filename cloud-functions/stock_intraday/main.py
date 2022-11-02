import asyncio
import logging
import os

import firebase_admin
import sentry_sdk
import yfinance as yf
from firebase_admin import firestore
from firebase_admin.credentials import Certificate
from sentry_sdk.integrations.gcp import GcpIntegration

sentry_sdk.init(
    dsn="https://0df591e2d2484901b49980602430c81b@o78857.ingest.sentry.io/6775447",
    integrations=[
        GcpIntegration(timeout_warning=True),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1,
)


def instantiate():
    if firebase_admin._apps:
        return firebase_admin.get_app(), firestore.client()

    try:
        key_path = f'{os.path.pardir}/credentials.json'

        cred = Certificate(key_path)
        app = firebase_admin.initialize_app(cred)
        db = firestore.client()
    except:
        app = firebase_admin.initialize_app()
        db = firestore.client()

    return app, db


async def save(db, transaction, collection, uuid, document):
    result_ref = db.document(f"{collection}/{uuid}")
    if transaction:
        return transaction.set(result_ref, document)
    else:
        return result_ref.set(document)

    # logging.info('%s saved in %s collection', uuid, collection)


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
    )


def fetch_stocks(db, stock_len):
    return db.collection("stocks") \
        .where("enabled", "==", True) \
        .order_by("updated_at", direction=firestore.firestore.Query.ASCENDING) \
        .limit(stock_len) \
        .stream()


async def save_time_series(stock, period, interval, db):
    path = f"stocks/{stock}/{interval}"
    stock_dict = stock.to_dict()
    df = fetch_data_frame(symbol=stock.id, period=period, interval=interval).to_dict(orient='index')

    # tasks = []
    for key in df:
        time_series = df[key]

        doc = {
            u'uuid': str(int(key.value / 1_000_000)),
            u'datetime': key,
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

        # tasks.append(
        save(
            db=db,
            transaction=None,
            collection=path,
            uuid=doc["uuid"],
            document=doc
        )
        # )
    # await asyncio.gather(*tasks)


async def update_stock_price(stock, db):
    df = fetch_data_frame(symbol=stock.id, period="5d", interval="1d")
    prices = list(map(lambda price: round(price, 2), df.Close.values))

    if len(prices) == 0:
        fields = {
            "enabled": False,
            "updated_at": firestore.firestore.SERVER_TIMESTAMP
        }
        logging.warning("%s deactivated", stock.id)
    elif len(prices) > 1:
        fields = {
            "price": prices[-1],
            "price_flutuation": round((prices[-1] / prices[-2] - 1) * 100, 2),
            "price_absolute_flutuation": round(prices[-1] - prices[-2], 2),
            "week": prices,
            "updated_at": firestore.firestore.SERVER_TIMESTAMP
        }
    else:
        fields = {
            "price": prices[-1],
            "price_flutuation": 0,
            "price_absolute_flutuation": 0,
            "week": prices,
            "updated_at": firestore.firestore.SERVER_TIMESTAMP
        }

    await db.collection("stocks").document(stock.id).update(fields)


async def crawl_stock_price(stocks_dict, period, interval, db):
    try:
        tasks = []
        for stock in stocks_dict:
            print(stock.id)
            # await save_time_series(stock, period, interval, db)
            tasks.append(save_time_series(stock, period, interval, db))
            # tasks.append(update_stock_price(stock, db))
            logging.info('%s saved!', stock.id)
        await asyncio.gather(*tasks)
    except Exception as e:
        print(e)
        logging.error(e)
        sentry_sdk.capture_exception(e)


def entry_point(event, context):
    period = "5d"
    interval = "1d"
    stock_len = 10

    # period = str(event["attributes"]["period"])
    # interval = str(event["attributes"]["interval"])
    # stock_len = int(event["attributes"]["stock_len"])

    import time
    s = time.perf_counter()
    app, db = instantiate()

    stocks_dict = fetch_stocks(db, stock_len)

    asyncio.run(crawl_stock_price(stocks_dict, period, interval, db))

    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")


if __name__ == '__main__':
    entry_point(None, None)
