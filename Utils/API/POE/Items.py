from requests import get
from dataclasses import dataclass, field
from itertools import chain

_items_JSON = get('https://www.pathofexile.com/api/trade/data/items').json()['result']


@dataclass(eq=True)
class Item(object):
    type: str
    text: str
    name: str = field(default=None)
    flags: dict = field(default=None)
    disc: str = field(default=None)

    @property
    def unique(self) -> bool:
        return self.flags is not None and 'unique' in self.flags and self.flags['unique']

    def __str__(self):
        field_list = [attribute for attribute in dir(self) if not attribute.startswith('__')]
        return ', '.join([f'{field.replace("_", " ").title()}: {getattr(self, field)}' for field in field_list if getattr(self, field) is not None])


def _load_items_json(json):
    '''
    Formats the incoming JSON data coming fromt he POE API
    :param json: A parsed json object from the POE data site
    :return: A dict of categories, each with individual item objects
    '''
    categories = {}
    for category in _items_JSON:
        category_items = []
        for item in category['entries']:
            category_items.append(Item(**item))
        if category['label'] in categories:
            categories[category['label']].extend(category_items)
        else:
            categories[category['label']] = category_items
    return categories


CATEGORIZED_ITEMS = _load_items_json(_items_JSON)
ITEMS_BY_NAME = {item.name: item for item in chain.from_iterable(CATEGORIZED_ITEMS.values())}
