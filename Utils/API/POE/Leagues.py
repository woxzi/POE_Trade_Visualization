import requests
from urllib.parse import quote


class League(object):
    def __init__(self, id: str, text: str):
        self.id = id
        self.text = text

    def __str__(self):
        return f"League(ID: '{self.id}', Text: '{self.text}')"

    @property
    def url_id(self):
        return quote(self.id)


def get_active_leagues():
    """
    This method pulls all public leagues currently available in Path of Exile
    :return: A list containing league objects, representing each currently active league
    """
    response = requests.get(url="https://www.pathofexile.com/api/trade/data/leagues")
    response_data = response.json()
    for item in response.headers.items():
        print(item)

    return [League(league_data['id'], league_data['text']) for league_data in response_data['result']]


DEFAULT_LEAGUE = get_active_leagues()[0]
