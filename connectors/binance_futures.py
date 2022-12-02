import requests
import pprint
import logging

# "https://fapi.binance.com"
# "https://testnet.binancefuture.com"

# Websocket API for lie streaming
# "wss://fstream.binance.com"

logger = logging.getLogger()


class BinanceFuturesClient:
    def __init__(self, testnet):
        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"

        self.prices = dict()

        logger.info("Binance Futures Client successfully initialized")

    # request function that receives multiple parameters
    def make_request(self, method, endpoint, data):
        if method == "GET":
            response = requests.get(self.base_url + endpoint, params=data)
        else:
            return ValueError()

        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Error while making %s request to %s: %s (error code %s)",
                         method, endpoint, response.json(), response.status_code)
            return None

    #
    def get_contracts(self):
        exchange_info = self.make_request("GET", "/fapi/v1/exchangeInfo", None)

        contracts = dict()
        if exchange_info is not None:
            for contract_data in exchange_info['symbols']:
                contracts[contract_data['pair']] = contract_data

        return contracts

    def get_historical_candles(self, symbol, interval):
        data = dict()
        data['symbol'] = symbol
        data['interval'] = interval
        data['limit'] = 1000

        raw_candles = self.make_request("GET", "/fapi/v1/klines", data)

        candles = []

        if raw_candles is not None:
            for candle in raw_candles:
                candles.append([candle[0], float(candle[1]), float(candle[2]), float(candle[3]), float(candle[4]), float(candle[5])])
        return candles

    def get_bid_ask(self, symbol):
        data = dict()
        data['symbol'] = symbol
        order_book_data = self.make_request("GET", "/fapi/v1/ticker/bookTicker", data)

        if order_book_data is not None:
            if symbol not in self.prices:
                self.prices[symbol] = {'bid' : float(order_book_data['bidPrice']),
                                       'ask' : float(order_book_data['askPrice'])}
            else:
                self.prices[symbol]['bid'] = float(order_book_data['bidPrice'])
                self.prices[symbol]['ask'] = float(order_book_data['askPrice'])

        return self.prices[symbol]



# pprint.pprint(get_contracts())
