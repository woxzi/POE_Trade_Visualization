from Utils.API.Ratelimit import RatelimitRule
from requests import post


def _get_trade_api_ratelimit_rules():
    response = post('https://www.pathofexile.com/api/trade/search/Heist')

    rule_types = response.headers['X-Rate-Limit-Rules'].split(',')

    rule_data = [response.headers[f'X-Rate-Limit-{rule_type}'] for rule_type in rule_types]
    rule_data = ','.join(rule_data).split(',')
    rule_data = set(rule_data)  # remove duplicates

    rules = [[int(ruleitem) for ruleitem in rule.split(':')] for rule in rule_data]

    rules = [RatelimitRule(max_executions=max_requests - 1, interval=interval) for max_requests, interval, timeout in rules]

    return rules


API_NAME = 'Path of Exile API'
TRADE_API_NAME = API_NAME + ' (Trade)'
TRADE_API_RATELIMIT_RULES = _get_trade_api_ratelimit_rules()

