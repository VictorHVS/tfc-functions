class Exchange:
    COLLECTION = "exchanges"

    def __init__(self, mic_code, created_at, updated_at, name, country, suffix, delay, timezone):
        self.uuid = str(suffix)
        self.created_at = created_at
        self.updated_at = updated_at
        self.name = str(name)
        self.country = str(country)
        self.suffix = str(suffix)
        self.mic_code = str(mic_code)
        self.delay = str(delay)
        self.timezone = str(timezone)

    def to_dict(self):
        dest = {
            u'uuid': self.uuid,
            u'created_at': self.created_at,
            u'updated_at': self.updated_at,
            u'name': self.name,
            u'suffix': self.suffix,
            u'mic_code': self.mic_code,
            u'delay': self.delay,
            u'timezone': self.timezone,
        }
        return dest


class Stock:
    COLLECTION = "stocks"

    def __init__(self,
                 symbol,
                 created_at,
                 updated_at,
                 name,
                 exchange_name,
                 currency,
                 exchange_id,
                 sector,
                 industry,
                 website,
                 description,
                 city,
                 state,
                 country,
                 logo_url
                 ):
        self.uuid = f'{symbol}{exchange_id}'
        self.symbol = str(symbol)
        self.exchange_id = str(exchange_id)
        self.exchange_name = str(exchange_name)
        self.created_at = created_at
        self.updated_at = updated_at
        self.name = str(name)
        self.currency = str(currency)
        self.enabled = True
        self.sector = str(sector)
        self.industry = str(industry)
        self.website = str(website)
        self.description = str(description)
        self.city = str(city)
        self.state = str(state)
        self.country = str(country)
        self.logo_url = str(logo_url)

    def to_dict(self):
        dest = {
            u'uuid': self.uuid,
            u'created_at': self.created_at,
            u'updated_at': self.updated_at,
            u'name': self.name,
            u'symbol': self.symbol,
            u'exchange_id': self.exchange_id,
            u'exchange_name': self.exchange_name,
            u'currency': self.currency,
            u'enabled': self.enabled,
            u'sector': self.sector,
            u'industry': self.industry,
            u'website': self.website,
            u'description': self.description,
            u'city': self.city,
            u'state': self.state,
            u'country': self.country,
            u'logo_url': self.logo_url,
        }
        return dest


class TimeSeries:
    def __init__(self,
                 uuid,
                 datetime,
                 stock_uuid,
                 interval,
                 currency,
                 exchange_uuid,
                 timezone,
                 open,
                 high,
                 low,
                 close,
                 volume,
                 ):
        self.uuid = str(uuid)
        self.datetime = datetime
        self.timezone = str(timezone)
        self.stock_uuid = str(stock_uuid)
        self.exchange_uuid = str(exchange_uuid)
        self.interval = str(interval)
        self.currency = str(currency)
        self.open = float(open)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.volume = float(volume)

    def to_dict(self):
        dest = {
            u'uuid': self.uuid,
            u'datetime': self.datetime,
            u'timezone': self.timezone,
            u'stock_uuid': self.stock_uuid,
            u'exchange_uuid': self.exchange_uuid,
            u'interval': self.interval,
            u'currency': self.currency,
            u'open': self.open,
            u'high': self.high,
            u'low': self.low,
            u'close': self.close,
            u'volume': self.volume,
        }
        return dest


class UserPortfolio:
    def __init__(self,
                 currency,
                 net_value,
                 sum
                 ):
        self.currency = currency
        self.net_value = float(net_value)
        self.sum = float(sum)

    def to_dict(self):
        return self.__dict__


class User:
    COLLECTION = "users"

    def __init__(self,
                 uuid,
                 created_at,
                 name,
                 username,
                 portfolio_by_currency
                 ):
        self.uuid = str(uuid)
        self.created_at = created_at
        self.name = name
        self.username = username
        self.portfolio_by_currency = portfolio_by_currency

    def to_dict(self):
        dest = {
            u'uuid': self.uuid,
            u'created_at': self.created_at,
            u'name': self.name,
            u'username': self.username,
            u'portfolio_by_currency': [x.__dict__ for x in self.portfolio_by_currency],
        }
        return dest
