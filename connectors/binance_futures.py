import requests
import time
import logging
import hmac
import hashlib
from urllib.parse import urlencode
# "https://fapi.binance.com"
# "https://testnet.binancefuture.com"

# Websocket API for lie streaming
# "wss://fstream.binance.com"

logger = logging.getLogger()

class BinanceFuturesClient:
    def __init__(self, public_key, secret_key, testnet):
        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"

        self.public_key = public_key
        self.secret_key = secret_key

        self.headers = {'X-MBX-APIKEY': self.public_key}

        self.prices = dict()

        logger.info("Binance Futures Client successfully initialized")

    def generate_signature(self, data):
        return hmac.new(self.secret_key.encode(), urlencode(data).encode(), hashlib.sha256).hexdigest()

    # request function that receives multiple parameters
    def make_request(self, method, endpoint, data):
        if method == "GET":
            response = requests.get(self.base_url + endpoint, params=data, headers=self.headers)
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

    def get_balance(self):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        balances = dict()
        account_data = self.make_request("GET", "/fapi/v2/account", data)

        if account_data is not None:
            for account in account_data['assets']:
                balances[account['asset']] = account

        return balances

    def place_order(self):
        return

    def cancel_order(self):
        return

    def get_order_status(self):
        return


