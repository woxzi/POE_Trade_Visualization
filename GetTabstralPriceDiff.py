from Tools.API.POE import fetch_query_results
from Tools.API.POE_Ninja import get_chaos_equivalent

tabstral_query_json = '''
{
  "query": {
    "status": {
      "option": "online"
    },
    "type": "Astral Plate",
    "stats": [
      {
        "type": "and",
        "filters": []
      }
    ],
    "filters": {
      "misc_filters": {
        "filters": {
          "ilvl": {
            "min": 86
          },
          "shaper_item": {
            "option": "false"
          },
          "crusader_item": {
            "option": "false"
          },
          "hunter_item": {
            "option": "false"
          },
          "elder_item": {
            "option": "false"
          },
          "redeemer_item": {
            "option": "false"
          },
          "warlord_item": {
            "option": "false"
          }
        }
      },
      "trade_filters": {
        "filters": {
          "price": {
            "min": 2
          }
        }
      },
      "socket_filters": {
        "filters": {
          "links": {
            "min": 6
          },
          "sockets": {
            "w": 6
          }
        }
      }
    }
  },
  "sort": {
    "price": "asc"
  }
}
'''

beastsplit_query = '''
{
  "query": {
    "status": {
      "option": "online"
    },
    "type": "Fenumal Plagued Arachnid",
    "stats": [
      {
        "type": "and",
        "filters": []
      }
    ]
  },
  "sort": {
    "price": "asc"
  }
}
'''

tabstral_data = fetch_query_results(tabstral_query_json, 10)
beastsplit_data = fetch_query_results(beastsplit_query, 10)

tabstral_prices = []
for item in tabstral_data:
    currency_type = item['listing']['price']['currency']
    currency_amount = item['listing']['price']['amount']
    currency_value = get_chaos_equivalent(currency_type, 'Ritual') * currency_amount
    tabstral_prices.append(currency_value)

    # print('Tabstral ', f'{currency_value}c', item['listing']['price'])

beastsplit_prices = []
for item in beastsplit_data:
    currency_type = item['listing']['price']['currency']
    currency_amount = item['listing']['price']['amount']
    currency_value = get_chaos_equivalent(currency_type, 'Ritual') * currency_amount
    beastsplit_prices.append(currency_value)

    # print('Beastsplit ', f'{currency_value}c', item['listing']['price'])

tabstral_average_value = sum(tabstral_prices) / len(tabstral_prices)
beastsplit_average_value = sum(beastsplit_prices) / len(beastsplit_prices)

print('Avg Tabstral Price:', tabstral_average_value)
print('Avg Beastsplit Price:', beastsplit_average_value)
print('Avg Profit:', tabstral_average_value - beastsplit_average_value)
