import os

import pandas as pd
import json


def exchanges_to_json():
    df = pd.read_csv(f'{os.path.dirname(__file__)}/exchanges.csv', delimiter=";")
    return json.loads(df.to_json(orient='records'))


if __name__ == '__main__':
    print(exchanges_to_json())
