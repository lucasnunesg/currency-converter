from v2.external_api import CurrencyApiInterface, EconomiaAwesomeAPI


def update_currency_rates(currencies_list: list, api: CurrencyApiInterface = EconomiaAwesomeAPI) -> None:
    """Updates the currencies rate of the given database"""
    url = api.url_builder(currencies_list)
    currencies_usd_rate_dict = api.get_conversion(url=url)

    # Update the rates in the database
