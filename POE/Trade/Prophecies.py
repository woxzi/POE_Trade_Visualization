import csv

from Data.Index import PROPHECY_INFO
from Tools import Wrapper
from Tools.API.POE import get_first_page_data
from Tools.API.POE.Items import Item, CATEGORIZED_ITEMS, ITEMS_BY_NAME


class Prophecy(Wrapper):
    __wraps__ = Item


_prophecies = {item.name: Prophecy(item) for item in CATEGORIZED_ITEMS['Prophecies']}


class UpgradeProphecy(Wrapper):
    __wraps__ = Prophecy

    def __init__(self, prophecy: Prophecy, base_unique: Item, result_unique: Item):
        super().__init__(prophecy)
        self.base_unique = base_unique
        self.result_unique = result_unique
        self._value = None

    def __str__(self):
        return f'[{self.name}]: {self.base_unique.name} -> {self.result_unique.name}'


    # FOR PULLING PROPHECY VALUE FROM POE TRADE API
    # @property
    # def value(self):
    #     if self._value is not None:
    #         return self._value
    #     prophecy_query = {
    #         "query": {
    #             "status": {
    #                 "option": "online"
    #             },
    #             "name": self.name,
    #             "type": "Prophecy",
    #             "stats": [
    #                 {
    #                     "type": "and",
    #                     "filters": []
    #                 }
    #             ],
    #             "filters": {
    #                 "trade_filters": {
    #                     "filters": {
    #                         "indexed": {
    #                             "option": "1day"
    #                         }
    #                     }
    #                 },
    #                 "type_filters": {
    #                     "filters": {
    #                         "category": {
    #                             "option": "prophecy"
    #                         }
    #                     }
    #                 }
    #             }
    #         },
    #         "sort": {
    #             "price": "asc"
    #         }
    #     }
    #     trade_data = get_first_page_data(query_json=prophecy_query)
    #     for trade in trade_data['result']:
    #         print(trade['listing']['price'])


def _load_upgrade_prophecy_csv():
    global _prophecies
    with open(PROPHECY_INFO, 'r') as prophecy_file:
        reader = csv.reader(prophecy_file)
        prophecies = [UpgradeProphecy(prophecy=_prophecies[prophecy], base_unique=ITEMS_BY_NAME[base], result_unique=ITEMS_BY_NAME[result]) for prophecy, base, result in reader]
    return prophecies


UPGRADE_PROPHECIES = _load_upgrade_prophecy_csv()

print(UPGRADE_PROPHECIES[0].value)
