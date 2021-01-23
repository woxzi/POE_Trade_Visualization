from requests import post, get
from copy import deepcopy
from json import loads

from typing import Iterable
from itertools import chain
from Tools import to_chunks
from Tools.API import API_Names
from Tools.API.Ratelimiting import RatelimitRule, create_ratelimit, ratelimit

# extract related enums for convenience
POE_API_NAME = API_Names.PATH_OF_EXILE
TRADE_API_NAME = API_Names.PATH_OF_EXILE_TRADE

LEAGUE = 'Ritual'
MAX_LISTINGS_PER_REQUEST = 10

_search_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://www.pathofexile.com',
    'referer': f'https://www.pathofexile.com/trade/search/{LEAGUE}'
}

_search_result_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://www.pathofexile.com',
    'referer': f'https://www.pathofexile.com/trade/search/{LEAGUE}/{{trade_search_id}}'
}


class TooManyListingsException(Exception):
    pass


def _get_trade_api_ratelimit_rules():
    generic_trade_json = '{"query":{"status":{"option":"online"},"stats":[{"type":"and","filters":[]}]},"sort":{"price":"asc"}}'
    response = post(f'https://www.pathofexile.com/api/trade/search/{LEAGUE}', json=generic_trade_json, headers=_search_headers)

    rule_types = response.headers['X-Rate-Limit-Rules'].split(',')

    rule_data = [response.headers[f'X-Rate-Limit-{rule_type}'] for rule_type in rule_types]
    rule_data = ','.join(rule_data).split(',')
    rule_data = set(rule_data)  # remove duplicates

    rules = [[int(ruleitem) for ruleitem in rule.split(':')] for rule in rule_data]

    rules = [RatelimitRule(max_executions=max_requests - 1, interval=interval) for max_requests, interval, timeout in rules]

    return rules


TRADE_API_RATELIMIT_RULES = _get_trade_api_ratelimit_rules()

create_ratelimit(TRADE_API_RATELIMIT_RULES, name=TRADE_API_NAME)


@ratelimit(TRADE_API_NAME)
def send_search_request(query_json):
    """
    Runs a search using the supplied JSON as query parameters, returning all listings that matched said search
    :param query_json: The search parameters
    :return: (id, results): A tuple containing the Search ID and Trade IDs resulting from the search
    """

    if isinstance(query_json, str):
        query_json = loads(query_json)

    response = post(f'https://www.pathofexile.com/api/trade/search/{LEAGUE}', json=query_json, headers=_search_headers)
    results = response.json()
    return results['id'], results['result']


@ratelimit(TRADE_API_NAME)
def get_search_results(search_id: str, trade_ids: Iterable[str]):
    """
    Retrieves listing information from search results, by trade id.

    :param search_id: The search if returned by the send_search_request function
    :param trade_ids: Up to 10 ids returned by the send_search_request function
    :return:
    """
    if len(trade_ids) > 10:
        raise TooManyListingsException()

    headers = deepcopy(_search_result_headers)
    headers['referer'] = headers['referer'].format(trade_search_id=search_id)

    trade_id_string = ','.join(trade_ids)
    URL = f'https://www.pathofexile.com/api/trade/fetch/{trade_id_string}?query={search_id}'
    response = get(URL, json={'query': search_id}, headers=headers)

    results = response.json()
    return results


def fetch_query_results(query_json, num_trades: int = -1):
    """
    Performs a trade search and returns the results.
    :param query_json: The number of trades to pull
    :param num_trades: Restrict the fetch to only pull the first n trades, negative values will pull the first page.
    :return:
    """
    id, trades = send_search_request(query_json)
    if num_trades >= 0:
        trades = trades[:num_trades]

    trade_chunks = to_chunks(trades, MAX_LISTINGS_PER_REQUEST)

    chunk_results = [get_search_results(id, chunk)['result'] for chunk in trade_chunks]  # get results for all chunks
    results = list(chain.from_iterable(chunk_results))  # condense all results into list

    return results
