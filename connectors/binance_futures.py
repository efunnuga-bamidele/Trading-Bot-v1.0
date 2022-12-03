import requests
import time
import logging
import hmac
import hashlib
from urllib.parse import urlencode
import websocket
import json
import threading

# "https://fapi.binance.com"
# "https://testnet.binancefuture.com"

# Websocket API for lie streaming
# "wss://fstream.binance.com"

logger = logging.getLogger()

class BinanceFuturesClient:
    def __init__(self, public_key, secret_key, testnet):
        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
            self.wss_url = "wss://stream.binancefuture.com/ws"
        else:
            self.base_url = "https://fapi.binance.com"
            self.wss_url = "wss://fstream.binance.com/ws"

        self.public_key = public_key
        self.secret_key = secret_key

        self.headers = {'X-MBX-APIKEY': self.public_key}

        self.prices = dict()
        self.id = 1
        self.ws = None

        # Create a threading function to run parallel in background while other functions execute.
        threadObject = threading.Thread(target= self.start_ws)
        threadObject.start()

        logger.info("Binance Futures Client successfully initialized")

    def generate_signature(self, data):
        return hmac.new(self.secret_key.encode(), urlencode(data).encode(), hashlib.sha256).hexdigest()

    # request function that receives multiple parameters
    def make_request(self, method, endpoint, data):
        if method == "GET":
            response = requests.get(self.base_url + endpoint, params=data, headers=self.headers)
        elif method == "POST":
            response = requests.post(self.base_url + endpoint, params=data, headers=self.headers)
        elif method == "DELETE":
            response = requests.delete(self.base_url + endpoint, params=data, headers=self.headers)
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

    def place_order(self, symbol, side, quantity, order_type, price=None, tif=None):
        data = dict()
        data['symbol'] = symbol
        data['side'] = side
        data['quantity'] = quantity
        data['type'] = order_type

        if price is not None:
            data['price'] = price
        if tif is not None:
            data['timeInForce'] = tif

        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request("POST", "/fapi/v1/order", data)

        return order_status

    def cancel_order(self, symbol, order_id):
        data = dict()
        data['symbol'] = symbol
        data['orderId'] = order_id
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request("DELETE", "/fapi/v1/order", data)

        return order_status

    def get_order_status(self, symbol, order_id):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        dict['symbol'] = symbol
        dict['orderId'] = order_id
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request("GET", "/fapi/v1/order", data)

        return order_status

    def start_ws(self):
        self.ws = websocket.WebSocketApp(self.wss_url, on_open=self.on_open, on_close=self.on_close, on_error=self.on_error,
                                    on_message=self.on_message)
        self.ws.run_forever()

    def on_open(self, ws):
        logger.info("Binance connection opened")
        self.subscribe_channel("BTCUSDT")

    def on_close(self, ws):
        logger.warning("Binance connection closed")

    def on_error(self, ws, msg):
        logger.info("Binance connection error: %s", msg)

    def on_message(self, ws, msg):
        # print(msg)
        data = json.loads(msg)

        if "e" in data:
            if data['e'] == "bookTicker":
                symbol = data['s']
                if symbol not in self.prices:
                    self.prices[symbol] = {'bid' : float(data['b']),
                                       'ask' : float(data['a'])}
                else:
                    self.prices[symbol]['bid'] = float(data['b'])
                    self.prices[symbol]['ask'] = float(data['a'])
                print(self.prices[symbol])

    def subscribe_channel(self, symbol):
        data = dict()
        data['method'] = "SUBSCRIBE"
        data['params'] = []
        data['params'].append(symbol.lower() + "@bookTicker")
        data['id'] = self.id

        self.ws.send(json.dumps(data))

        self.id += 1



