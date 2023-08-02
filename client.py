from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

from pytrading212 import CFD, CFDMarketOrder, CFDLimitStopOrder, CFDOCOOrder
from pytrading212 import Mode

import threading
from threading import Lock

from queue import Queue



actionQueue = Queue(maxsize=10)


options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--start-maximized')


class broker(threading.Thread):
    PATH = "/usr/bin/chromedriver"

    def __init__(self) :
        threading.Thread.__init__(self)
        

    def run(self):

        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        cfd = CFD(email='', password='', driver=driver, mode=Mode.DEMO)

        while True:
            try:
                trade = actionQueue.get(block=False)
                ticker=  (list(trade.keys())[0].split(' ] '))[0] # ticker, time, strat

                cfd_order = CFDMarketOrder(instrument_code = ticker,
                                quantity=0.1 * list(trade.values())[0],  # Buy (quantity is positive)
                                target_price=cfd.get_current_price(instrument_code=ticker),
                                limit_distance=  0.4,
                                stop_distance= 0.2)
                
                new_order = cfd.execute_order(order=cfd_order)
            
            except Exception as e:
                print('ERROR', e)
                pass

a = broker()
a.start()