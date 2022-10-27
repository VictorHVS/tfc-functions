class Exchange:

    COLLECTION = "exchanges"

    def __init__(self, mic_code, created_at, updated_at, name, country, suffix, delay, timezone):
        self.uuid = str(mic_code)
        self.created_at = created_at
        self.updated_at = updated_at
        self.name = str(name)
        self.country = str(country)
        self.suffix = str(suffix)
        self.delay = str(delay)
        self.timezone = str(timezone)

    def to_dict(self):
        dest = {
            u'uuid': self.uuid,
            u'created_at': self.created_at,
            u'updated_at': self.updated_at,
            u'name': self.name,
            u'suffix': self.suffix,
            u'delay': self.delay,
            u'timezone': self.timezone,
        }
        return dest
