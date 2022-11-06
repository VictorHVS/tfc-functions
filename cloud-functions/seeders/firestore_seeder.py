import logging

import firebase_admin
from firebase_admin import firestore
from firebase_admin.credentials import Certificate

from seeders.exchanges.exchanges import exchanges_to_json
from seeders.historical_data.historical_data import time_series_to_dict, periods_intervals
from model import Exchange, Stock, TimeSeries
from seeders.stocks.stocks import stocks_to_json


def instantiate():
    if firebase_admin._apps:
        return firebase_admin.get_app(), firestore.client()

    try:
        key_path = '../credentials.json'
        cred = Certificate(key_path)
        app = firebase_admin.initialize_app(cred)
        db = firestore.client()
    except:
        app = firebase_admin.initialize_app()
        db = firestore.client()

    return app, db


def save(db, transaction, collection, uuid, document):
    result_ref = db.document(f"{collection}/{uuid}")
    if transaction:
        transaction.set(result_ref, document)
    else:
        result_ref.set(document)

    logging.info('%s saved in %s collection', uuid, collection)


def seed_exchanges(db, transaction):
    exchanges_dict = exchanges_to_json()
    for item in exchanges_dict:
        if item['mic_code'] is not None:
            exchange = Exchange(
                mic_code=item['mic_code'],
                created_at=firestore.firestore.SERVER_TIMESTAMP,
                updated_at=firestore.firestore.SERVER_TIMESTAMP,
                name=item['exchange'],
                country=item['country'],
                suffix=item['suffix'],
                delay=item['delay'],
                timezone=item['timezone'],
            )

            save(
                db=db,
                transaction=transaction,
                collection=Exchange.COLLECTION,
                uuid=exchange.uuid,
                document=exchange.to_dict()
            )


def seed_stocks(db, transaction):
    stocks_dict = stocks_to_json()
    for item in stocks_dict:
        stock = Stock(
            symbol=item['symbol'],
            created_at=firestore.firestore.SERVER_TIMESTAMP,
            updated_at=firestore.firestore.SERVER_TIMESTAMP,
            exchange_id=item['exchange'],
            country=item['country'],
            name=item['shortName'],
            currency=item['currency'],
            exchange_name="BOVESPA",
            sector=item['sector'],
            industry=item['industry'],
            website=item['website'],
            description=item['longBusinessSummary'],
            city=item['city'],
            state=item['state'],
            logo_url=item['logo_url'],
        )

        save(
            db=db,
            transaction=transaction,
            collection=Stock.COLLECTION,
            uuid=stock.uuid,
            document=stock.to_dict()
        )


def seed_historical_data(db):
    stocks_dict = stocks_to_json()
    for item in stocks_dict:
        symbol = item['symbol']
        exchange = item['exchange']
        for period in periods_intervals:
            interval_str = period["interval"]
            path = f"{Stock.COLLECTION}/{symbol}{exchange}/{interval_str}"
            print(path)

            time_series_list = time_series_to_dict(symbol=symbol, period=interval_str)

            for time_series in time_series_list:
                doc = TimeSeries(
                    uuid=time_series["uuid"],
                    datetime=time_series["datetime"],
                    stock_uuid=time_series["stock_uuid"],
                    interval=time_series["interval"],
                    currency=time_series["currency"],
                    exchange_uuid=time_series["exchange_uuid"],
                    timezone=time_series["timezone"],
                    open=time_series["open"],
                    high=time_series["high"],
                    low=time_series["low"],
                    close=time_series["close"],
                    volume=time_series["volume"]
                )

                save(
                    db=db,
                    transaction=None,
                    collection=path,
                    uuid=doc.uuid,
                    document=doc.to_dict()
                )


def seed():
    app, db = instantiate()
    transaction = db.transaction()

    seed_exchanges(db, None)
    seed_stocks(db, None)
    seed_historical_data(db)

    transaction.commit()


if __name__ == '__main__':
    seed()
