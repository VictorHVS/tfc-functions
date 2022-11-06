import logging
import os

import sentry_sdk
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

db = firestore.Client()


def delete_user_collection(user_id):
    doc = db.collection("users").document(user_id).get()
    print(doc.to_dict())
    if not doc.exists:
        raise ValueError(f"User {user_id} not exists")

    logging.info(doc.to_dict())
    db.collection("users").document(user_id).delete()


def auth_remove_account(event, context):
    try:
        user_id = event['uid']
        delete_user_collection(user_id)
    except Exception as e:
        logging.error(e)
        sentry_sdk.capture_exception(e)


# if __name__ == '__main__':
#     event = {
#         'email': 'vhv.sousa@gmail.com',
#         'metadata': {'createdAt': '2022-11-04T05:42:05Z'},
#         'providerData': [{'email': 'vhv.sousa@gmail.com', 'providerId': 'password', 'uid': 'vhv.sousa@gmail.com'}],
#         'uid': 'UKCEPkaQeSRzFHrFl9DOcNRQDXe2'
#     }
#     auth_remove_account(event, None)
