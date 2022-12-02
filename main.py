import tkinter as tk
import logging
from connectors.bitmex_futures import get_contracts
from connectors.binance_futures import BinanceFuturesClient
import config
import pprint

logger = logging.getLogger()

# logger.debug("This message is important only when debugging the program")
# logger.info("This message just shows basic information")
# logger.warning("This message is about something you should pay attention to")
# logger.error("this message helps to debug an error that occurred in your program")

logger .setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s :: %(message)s")
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

if __name__ == '__main__':

    binanceObject = BinanceFuturesClient(config.BINANCE_KEY, config.BINANCE_SECRET, False)
    pprint.pprint(binanceObject.get_balance())

    root = tk.Tk()


    root.mainloop()

