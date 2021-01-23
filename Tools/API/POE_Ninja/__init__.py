from dataclasses import dataclass
from typing import Dict

from requests import get

from Tools.API import API_Names

POE_NINJA_API_NAME = API_Names.PATH_OF_EXILE


@dataclass
class Currency(object):
    id: int
    icon: str  # the url in which the icon is stored
    name: str
    tradeId: str  # the name of the currency used in POE Trade API
    chaos_value: float  # the amount of chaos that this currency is worth


_currency_data = {}


def update_exchange_rates(league: str):
    global _currency_data
    print('Retrieving currency exchange rates from poe.ninja')
    result = get(f'https://poe.ninja/api/data/currencyoverview?league={league}&type=Currency')
    result_body = result.json()
    currency_worth_amounts = {line['currencyTypeName']: line['chaosEquivalent'] for line in result_body['lines']}
    for line in result_body['lines']:
        if line['currencyTypeName'] == 'Chaos Orb':
            print(line)

    currency_details = result_body['currencyDetails']

    currency_data = {}
    for currency in currency_details:
        if currency['tradeId'] == 'chaos':
            currency_data[currency['tradeId']] = Currency(chaos_value=1, **currency)
        elif not (currency['name'] in currency_worth_amounts.keys()):
            currency_data[currency['tradeId']] = Currency(chaos_value=0, **currency)
        else:
            currency_data[currency['tradeId']] = Currency(chaos_value=currency_worth_amounts[currency['name']], **currency)

    _currency_data[league] = currency_data


def get_currency_exchange_rates(league: str):
    global _currency_data
    if not league in _currency_data:
        update_exchange_rates(league)

    return _currency_data[league]


def get_chaos_equivalent(currency_id: str, league: str):
    rates = get_currency_exchange_rates(league)
    return rates[currency_id].chaos_value
