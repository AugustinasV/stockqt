import pandas as pd
import pendulum
from datetime import datetime, timedelta, timezone

import yfinance as yf

import threading
from threading import Lock

import queue
import time

import client

###################################
rows_for_settling = 100
q = queue.Queue()
client.actionQueue
###################################

s_print_lock = Lock()
def s_print(*a, **b):
    """Thread safe print function"""
    with s_print_lock:
        print(*a, **b)



def TSI(dataf: pd.DataFrame,
    long: int = 14,
    short: int = 7,
    signal: int = 5,
    column: str = 'Close',
    adjust: bool = True,
):
    ## Double smoother price change

    momentum = pd.Series(dataf[column].diff())  ## 1 period momentum
    _EMA25 = pd.Series(
        momentum.ewm(span=long, min_periods=long - 1, adjust=adjust).mean(),
        name="_price change EMA25",
    )
    _DEMA13 = pd.Series(
        _EMA25.ewm(span=short, min_periods=short - 1, adjust=adjust).mean(),
        name="_price change double smoothed DEMA13",
    )
    ## Double smoothed absolute price change
    absmomentum = pd.Series(dataf[column].diff().abs())
    _aEMA25 = pd.Series(
        absmomentum.ewm(span=long, min_periods=long - 1, adjust=adjust).mean(),
        name="_abs_price_change EMA25",
    )
    _aDEMA13 = pd.Series(
        _aEMA25.ewm(span=short, min_periods=short - 1, adjust=adjust).mean(),
        name="_abs_price_change double smoothed DEMA13",
    )
    TSI = pd.Series((_DEMA13 / _aDEMA13) * 100, name="TSI")
    SIGNAL = pd.Series(
        TSI.ewm(span=signal, min_periods=signal - 1, adjust=adjust).mean(),
        name="signal",
    )
    # return pd.concat([TSI, SIGNAL], axis=1,ignore_index=True)
    return TSI, SIGNAL

def MACD(
    ohlc: pd.DataFrame,
    period_fast: int = 10,
    period_slow: int = 20,
    signal: int = 5,
    column: str = 'Close',
    adjust: bool = True,
):
    EMA_fast = pd.Series(
        ohlc[column].ewm(ignore_na=False, span=period_fast, adjust=adjust).mean()
    )
    EMA_slow = pd.Series(
        ohlc[column].ewm(ignore_na=False, span=period_slow, adjust=adjust).mean()
    )
    MACD = pd.Series(EMA_fast - EMA_slow)
    MACD_signal = pd.Series(
        MACD.ewm(ignore_na=False, span=signal, adjust=adjust).mean()
    )
    # return pd.concat([MACD, MACD_signal], axis=1,ignore_index=True)
    return MACD, MACD_signal

def RSI(
    ohlc: pd.DataFrame,
    period: int = 14,
    period_ewm: int = 14,
    column: str = 'Close',
    adjust: bool = True,
):
    
    ## get the price diff

    delta = ohlc[column].diff()
    ## positive gains (up) and negative gains (down) Series
    up, down = delta.copy(), delta.copy()

    up[up < 0] = 0
    down[down > 0] = 0
    # EMAs of ups and downs
    _gain = up.ewm(alpha=1.0 / period, adjust=adjust).mean()
    _loss = down.abs().ewm(alpha=1.0 / period, adjust=adjust).mean()

    RS = _gain / _loss
    return pd.Series(100 - (100 / (1 + RS))), pd.Series(100 - (100 / (1 + RS))).ewm(ignore_na=False, span=period_ewm, adjust=adjust).mean()


def str1(current_pos:int, dataf:pd.DataFrame):
        
        asd = current_pos

        if current_pos == 0:
            if ( (dataf['TSI'].iloc[-1] > dataf['TSI_signal'].iloc[-1]) & (dataf['TSI'].iloc[-2] < dataf['TSI_signal'].iloc[-2]) & (dataf["RSI"].iloc[-1] < 40) ):
                asd = 1

            elif ( (dataf['TSI'].iloc[-1] < dataf['TSI_signal'].iloc[-1]) & (dataf['TSI'].iloc[-2] > dataf['TSI_signal'].iloc[-2]) & (dataf["RSI"].iloc[-1] > 60) ):
                asd = -1

        elif current_pos == -1:
            if ( (dataf['MACD'].iloc[-1] < dataf['MACD_signal'].iloc[-1]) & (dataf['MACD'].iloc[-2] > dataf['MACD_signal'].iloc[-2]) & (dataf["RSI_ewm"].iloc[-1] < 60) ):
                asd = 0

        elif current_pos == 1:
            if ( (dataf['MACD'].iloc[-1] > dataf['MACD_signal'].iloc[-1]) & (dataf['MACD'].iloc[-2] < dataf['MACD_signal'].iloc[-2]) & (dataf["RSI_ewm"].iloc[-1] > 40) ):
                asd = 0

        return asd


class download(threading.Thread):

    # __init__ class with name, time
    def __init__(self, ticker_name,time_interval) :
        threading.Thread.__init__(self)
        self.ticker = ticker_name # str (TSLA, AMZN, etc.)
        self.time = time_interval # str (1m, 5m, 15m, etc.)
        
        
        self.dataf = pd.DataFrame
        
        self.running = True


#########################################
        self.used_by = 'a'
        # self.used_by = strat      # one strat per download TODO
#########################################

    def __del__(self):
        s_print(self.ticker, self.time, 'deleted')
    
    def set_max_entries(self):
        self.asd = int(self.time.replace('m','')) * rows_for_settling
        return self.asd

    def read_yf(self,
                first:bool,
                ticker:str, 
                interval:str, 
                tz:str = 'America/New_York'):
        # get THE LAST AVAILABLE candle; TODO check
        if (first == True):
            start = pendulum.parse((datetime.utcnow() + timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M"),tz=tz).subtract(minutes=int((self.time.replace('m','')))* self.set_max_entries())
            end = pendulum.parse((datetime.utcnow() + timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M"),tz=tz).add(hours=1)
        
        # get candles from interval
        elif (first == False): 
            start = pendulum.parse((datetime.utcnow() + timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M"),tz=tz).subtract(minutes=int((self.time.replace('m',''))) * self.set_max_entries() ) # delete (* self.set_max_entries())             end = pendulum.parse((datetime.utcnow() + timedelta(hours=-4))().strftime("%Y-%m-%d %H:%M"),tz=tz).add(hours=1)
            end = pendulum.parse((datetime.utcnow() + timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M"),tz=tz).add(hours=1)

        df = yf.download(tickers=self.ticker, interval=self.time, start=start, end=end, progress = False)       # set to self.ticker, self.interval in call

        df.reset_index(inplace=True)  # Make it no longer an Index
        df = df.drop(['Adj Close'],axis=1)


        # add into if else block based on 'str...'
        df['TSI'] = 0
        df['TSI_signal'] = 0

        df['MACD'] = 0
        df['MACD_signal'] = 0

        df['RSI'] = 0
        df['RSI_ewm'] = 0


        return df

    def run(self):
        starttime = time.time()

        # get n rows
        while self.dataf.empty:    
        
            if self.running == True:
        
                try:
                    self.dataf = self.read_yf(first=True,
                                              ticker=self.ticker, interval=self.time)
                    s_print("Downloaded priming dataset for {}".format(self.ticker))      
                    print(len(self.dataf))
                except Exception as e:
                    s_print(e)
                    s_print("Can't download priming dataset for {}".format(self.ticker))
                    time.sleep(5)
                    pass

            else:
                break

        position = 0
        temp_position = 0
        while True:
        
            if self.running == True:
                try:
                    new_row = self.read_yf(first=False,
                                           ticker=self.ticker, interval=self.time)
                
                    if (new_row.empty != True):    # redundant????? TODO

                        if ((new_row['Datetime'].iloc[-1] != self.dataf['Datetime'].iloc[-1])):

                            self.dataf = (pd.concat([self.dataf,new_row.iloc[[-1]]],ignore_index=True))                          
                            
                            s_print('ADDED ROW', self.ticker, (datetime.utcnow() + timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S"))


################################################################################################################################################ change based on new strategy TODO
                            self.dataf['TSI'], self.dataf['TSI_signal'] = TSI(self.dataf)
                            self.dataf['MACD'], self.dataf['MACD_signal'] = MACD(self.dataf)
                            self.dataf['RSI'], self.dataf['RSI_ewm'] = RSI(self.dataf)
################################################################################################################################################


                            try:
                                position = str1(current_pos=position, dataf=self.dataf)
                            except Exception as e:
                                s_print(e)

                            s_print(self.dataf.tail(3))
                            s_print('POSITION ', self.ticker, position)

                            if position != temp_position:
                                try:
                                    client.actionQueue.put({
                                        str(self.ticker + " / " + self.time + " / " + self.used_by): position   # add quantities TODO 
                                    }, block= True, timeout= 30)
                                    s_print(self.ticker, 'ORDER UPDATE')
                                except:
                                    pass
                        else:
                            print(self.ticker, 'NO NEW', position)

                except Exception as e:
                    time.sleep(5)
                    pass

                temp_position = position
                time.sleep(10)

                # time.sleep((60.0 - ((time.time() - starttime) % 60.0)))

            else:
                break


# q={'TSLA/1m':download("TSLA","1m"),
#    'AMzN/1m':download("AMzN","1m"),
#    'AAPL/1m':download("AAPL","1m"),}

# q.append(download("TSLA","1m"))
# q.append(download("AMZN","1m"))
# q.append(download("AAPL","1m"))


# q['TSLA/1m'].start()
# q['AMZN/1m'].start()
# q['AAPL/1m'].start()



# time.sleep(20)
# q['TSLA/1m'].running=0
# del q['TSLA/1m']
# time.sleep(1)
# print('===================================================')

# print
 
# while True:pass


# a = download("TSLA","1m")
# b = download("AAPL","1m")
# c = download("AMZN","1m")
# aa = download("AMD","1m")
# bb = download("INTC","1m")
# cc = download("PLTR","1m")


# a.start()
# b.start()
# c.start()

# time.sleep(20)
# print(a)



###########################
# a.running=0
# del a
###########################


# time.sleep(10)


# aa.start()
# bb.start()
# cc.start()





