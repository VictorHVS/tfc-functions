def return_exchanges():
    """Busca e retornar todas as exchanges que serão usadas no projeto

        No Momento, apenas a bovespa está na lista.

    Returns:
        array: Lista de Exchanges
    """
    return [
        {
            "name": "B3 - Brasil Bolsa Balcão S.A",
            "acronym": "Bovespa",
            "mic": "BVMF",
            "country": "Brazil",
            "country_code": "BR",
            "city": "Sao Paulo",
            "website": "www.bmfbovespa.com.br",
            "timezone": {
                "timezone": "America/Sao_Paulo",
                "abbr": "-03",
                "abbr_dst": "-03"
            },
            "currency": {
                "code": "BRL",
                "symbol": "R$",
                "name": "Brazilian Real"
            },
            # TODO
            "open_at": DATETIME,
            "close_at": DATETIME
        }
    ]


def insert_exchanges(exchanges):
    # TODO: Salvar no DB
    pass
