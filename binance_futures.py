import requests
import pprint
# "https://fapi.binance.com"
# "https://textnet.binancefuture.com"

# Websocket API for lie streaming
# "wss://fstream.binance.com"

def get_contracts():

    response_object = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
    # print(response_object.status_code, response_object.json())
    # pprint.pprint(response_object.json())
    # pprint.pprint(response_object.json()['symbols'])

    contracts = []
    for contract in response_object.json()['symbols']:
        # pprint.pprint(contract)
        # pprint.pprint(contract['pair'])
        contracts.append(contract['pair'])

    return contracts
pprint.pprint(get_contracts())