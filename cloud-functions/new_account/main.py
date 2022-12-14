import logging
import os
from datetime import datetime

import sentry_sdk
from google.cloud import firestore
from sentry_sdk.integrations.gcp import GcpIntegration


class UserPortfolio:
    def __init__(self,
                 currency,
                 symbol,
                 net_value,
                 price_fluctuation,
                 price_fluctuation_absolute,
                 sum
                 ):
        self.currency = currency
        self.net_value = float(net_value)
        self.sum = float(sum)
        self.symbol = symbol
        self.price_fluctuation = float(price_fluctuation)
        self.price_fluctuation_absolute = float(price_fluctuation_absolute)

    def to_dict(self):
        return self.__dict__


class User:
    def __init__(self,
                 uuid,
                 created_at,
                 name,
                 username,
                 performance,
                 profitable,
                 trades,
                 rank_position,
                 week,
                 portfolio_by_currency
                 ):
        self.uuid = str(uuid)
        self.created_at = created_at
        self.name = name
        self.username = username
        self.performance = performance
        self.profitable = profitable
        self.trades = trades
        self.rank_position = rank_position
        self.week = week
        self.portfolio_by_currency = portfolio_by_currency

    def to_dict(self):
        dest = {
            u'uuid': self.uuid,
            u'created_at': self.created_at,
            u'name': self.name,
            u'username': self.username,
            u'performance': self.performance,
            u'proftable': self.profitable,
            u'trades': self.trades,
            u'rank_position': self.rank_position,
            u'week': self.week,
            u'portfolio_by_currency': [x.__dict__ for x in self.portfolio_by_currency],
        }
        return dest


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


def auth_new_account(event, context):
    try:
        net_value = os.environ.get('NET_VALUE')
        created_at = datetime.strptime(event['metadata']['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
        user = User(
            uuid=event['uid'],
            created_at=created_at,
            name=None,
            username=None,
            performance=0,
            profitable=0,
            trades=0,
            rank_position=0,
            week=[net_value],
            portfolio_by_currency=[
                UserPortfolio(
                    currency="BRL",
                    symbol="R$",
                    net_value=float(net_value),
                    sum=float(net_value),
                    price_fluctuation=0,
                    price_fluctuation_absolute=0,
                )
            ]
        )

        db = firestore.Client()
        if db.collection("users").document(user.uuid).get().exists:
            raise ValueError(f"User {user.uuid} already exists")

        db.collection("users").document(user.uuid).set(user.to_dict())
        logging.info(user.to_dict())
    except Exception as e:
        logging.error(e)
        sentry_sdk.capture_exception(e)

# if __name__ == '__main__':
#     event = {
#         'email': 'vhv.sousa@gmail.com',
#         'metadata': {'createdAt': '2022-11-04T05:42:05Z'},
#         'providerData': [{'email': 'vhv.sousa@gmail.com', 'providerId': 'password', 'uid': 'vhv.sousa@gmail.com'}],
#         'uid': '4A2OMb89mGcyos6dricymEGi1bG2-victor'
#     }
#     auth_new_account(event, None)
