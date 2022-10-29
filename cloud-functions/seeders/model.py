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
