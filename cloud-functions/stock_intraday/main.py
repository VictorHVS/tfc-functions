import logging

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
    traces_sample_rate=0.1,
)


def fetch_data_frame(tickers, period="1d", interval="1m"):
    dt = yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers=tickers,

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
        prepost=True,

        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads=True,

        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy=None
    )

    return dt


def instantiate():
    try:
        key_path = 'credentials.json'
        cred = Certificate(key_path)
        app = firebase_admin.initialize_app(cred)
        db = firestore.client()
    except:
        app = firebase_admin.initialize_app()
        db = firestore.client()

    return app, db


def save(db, transaction, collection, uuid, document):
    result_ref = db.collection(collection).document(uuid)
    if transaction:
        transaction.set(result_ref, document)
    else:
        result_ref.set(document)


def entry_point(event, context):
    # CRIAR UM INTERMEDIARIO QUE IRÁ:
    # 1. Criar um cron que roda every minuto e executa esta funcao
    # 2. Esta funcao pega os ultimos 69 stocks atualizados
    # 3. Executa o mesmo que o seeder de historical data
    # 4. Atualiza price int, price_flutuation float, price_absolute_flutuation float,1d_price_past_week [] on stock
    app, db = instantiate()
    tickers = ["RRRP3.SA", "ALPA4.SA", "ABEV3.SA", "AMER3.SA", "ASAI3.SA", "AZUL4.SA", "B3SA3.SA", "BPAN4.SA",
               "BBSE3.SA", "BRML3.SA", "BBDC3.SA", "BBDC4.SA", "BRAP4.SA", "BBAS3.SA", "BRKM5.SA", "BRFS3.SA",
               "BPAC11.SA", "CRFB3.SA", "CCRO3.SA", "CMIG4.SA", "CIEL3.SA", "COGN3.SA", "CPLE6.SA", "CSAN3.SA",
               "CPFE3.SA", "CMIN3.SA", "CVCB3.SA", "CYRE3.SA", "DXCO3.SA", "ECOR3.SA", "ELET3.SA", "ELET6.SA",
               "EMBR3.SA", "ENBR3.SA", "ENGI11.SA", "ENEV3.SA", "EGIE3.SA", "EQTL3.SA", "EZTC3.SA", "FLRY3.SA",
               "GGBR4.SA", "GOAU4.SA", "GOLL4.SA", "NTCO3.SA", "SOMA3.SA", "HAPV3.SA", "HYPE3.SA", "IGTI11.SA",
               "IRBR3.SA", "ITSA4.SA", "ITUB4.SA", "JBSS3.SA", "JHSF3.SA", "KLBN11.SA", "RENT3.SA", "LWSA3.SA",
               "LREN3.SA", "MGLU3.SA", "MRFG3.SA", "CASH3.SA", "BEEF3.SA", "MRVE3.SA", "MULT3.SA", "PCAR3.SA",
               "PETR3.SA", "PETR4.SA", "PRIO3.SA", "PETZ3.SA", "POSI3.SA", "QUAL3.SA", "RADL3.SA", "RDOR3.SA",
               "RAIL3.SA", "SBSP3.SA", "SANB11.SA", "CSNA3.SA", "SLCE3.SA", "SULA11.SA", "SUZB3.SA", "TAEE11.SA",
               "VIVT3.SA", "TIMS3.SA", "TOTS3.SA", "UGPA3.SA", "USIM5.SA", "VALE3.SA", "VIIA3.SA", "VBBR3.SA",
               "WEGE3.SA", "YDUQ3.SA"]

    data_frame = fetch_data_frame(' '.join(tickers), period="15m")

    # size = len(data_frame.axes[0].array)

    for ticker in tickers:
        dt = data_frame[ticker]
        # dt_dict = dt.to_dict()
        print(ticker)

        logging.warning('%s', dt)

        # for i in range(size):
        #     index = dt.axes[0].array[i]
        #     price_open = dt_dict['High'][index]
        #     low = dt_dict['Low'][index]
        #     volume = dt_dict['Volume'][index]
        #     close = dt_dict['Close'][index]
        #
        #     if i < size - 5:
        #         logging.info('%s %s', ticker, dt)
        # save(
        #     db=db,
        #     collection="temp",
        #     uuid=None,
        #     document=dt,
        #     transaction=None
        # )
