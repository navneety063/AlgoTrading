import yfinance as yf
import backtrader as bt
import random
import pandas as pd
import numpy as np

class ShortSellBuy():
    def __init__(self, high, Sprice) -> None:
        self.high = high
        self.Sprice = Sprice
        self.zeroPointEightAchived = False
    def feed(self, market):
        print("ShortSellBuy")
        if market.datas[0].high[0] > market.datas[0].high[-1]:
            market.order =  market.close()
            return Initial()
        elif market.datas[0].low[0] < market.ema[0]:
            return ShortSellSell(self.high, self.Sprice)
        else:
            return self

class ShortSellSell():
    def __init__(self, high, Sprice) -> None:
        self.high = high
        self.Sprice = Sprice
        self.zeroPointEightAchived = False
    def feed(self, market):
        print("ShortSellSell")
        if market.datas[0].close[0] > market.ema[0]:
            return ShortSellBuy(self.high, self.Sprice)
        elif self.zeroPointEightAchived and market.datas[0].low[0] < market.ema[0]:
            print("SELL PRICE:",self.Sprice)
            return ShortSellBuy(self.high, self.Sprice)
        elif self.zeroPointEightAchived and (market.datas[0].open[0]-self.Sprice/self.Sprice)*100 < -0.8:
            market.order = market.close()
            return Initial()
        elif not self.zeroPointEightAchived and (market.datas[0].open[0]-self.Sprice/self.Sprice)*100 >= -0.8:
            self.zeroPointEightAchived = True
            return self
        else:
            return self

class ShortSellPreSell():
    def __init__(self) -> None:
        pass
    
    def feed(self, market):
        print("Shortsellpresell")
        if market.datas[0].low[0] < market.datas[0].low[-1]:
           market.order = market.sell()
           return ShortSellSell(market.datas[0].high[-1],market.datas[0].open[0])
        elif (market.datas[0].close[0] < market.s3 and market.datas[0].open[0] > market.s3) or (market.datas[0].close[0] < market.s2 and market.datas[0].open[0] > market.s2) or (market.datas[0].close[0] < market.s1 and market.datas[0].open[0] > market.s1):
            return ShortSellPreSell()
        else:
            return Initial()

class PreSell():
    def __init__(self, low, bprice) -> None:
        self.low = low
        self.bprice = bprice
    def feed(self, market):
        print("Pre sell state")
        if market.datas[0].low[0] > market.ema[0]:
            return Buy(self.low, self.bprice)
        elif market.datas[0].low[0] < market.datas[0].low[-1]:
            print("profit sell", market.datas[0].close[0])
            market.order = market.close()
            return Initial()
        else:
            return self

class Buy():
    def __init__(self, low, bprice) -> None:
        self.low = low
        self.bprice = bprice
        self.zeroPointEightAchived = False
    def feed(self, market):
        print("Buy State",market.datas[0].close[0], market.ema[0])
        print("lows",self.low, market.datas[0].low[0])
        if self.low > market.datas[0].low[0]:
            print("stoploss buy", self.low , market.datas[0].low[0])
            print("loss sell price", market.datas[0].close[0])
            market.order = market.close()
            return Initial()
        elif self.zeroPointEightAchived and market.datas[0].close[0] < market.ema[0]:
            print("BUY PRICE:",self.bprice)
            return PreSell(self.low, self.bprice)
        elif self.zeroPointEightAchived and (market.datas[0].open[0]-self.bprice/self.bprice)*100 < 0.8:
            market.order = market.close()
            return Initial()
        elif not self.zeroPointEightAchived and (market.datas[0].open[0]-self.bprice/self.bprice)*100  >= 0.8:
            self.zeroPointEightAchived = True
            return self
        else:
            return self

class PreBuy():
    def __init__(self) -> None:
        pass

    def feed(self, market):
        print("Prebuy")
        if market.datas[0].high[-1] < market.datas[0].high[0]:
            print("buy price", market.datas[0].close[0])
            market.order = market.buy()
            return Buy(market.datas[0].low[-1], market.datas[0].open[0])
        elif (market.datas[0].close[0] > market.r1 and market.datas[0].open[0] < market.r1) or (market.datas[0].close[0] > market.r2 and market.datas[0].open[0] < market.r2) or (market.datas[0].close[0] > market.r3 and market.datas[0].open[0] < market.r3) :
            return PreBuy()
        else:
            return Initial()

class Initial():

    def __init__(self) -> None:
        pass
    
    def feed(self, market):
        print("Inital state", market.adx, market.diPlus, market.diMinus)
        if market.indicator.lines.p[0] > market.datas[0].close[0]:
            if market.adx > 25.6 and market.diMinus > market.adx:
                print("short sell", market.datas[0].close[0], market.datas[0].open[0], market.s1, market.s2, market.s3)
                if (market.datas[0].close[0] < market.s3 and market.datas[0].open[0] > market.s3) or (market.datas[0].close[0] < market.s2 and market.datas[0].open[0] > market.s2) or (market.datas[0].close[0] < market.s1 and market.datas[0].open[0] > market.s1):
                    print("short sell entry", market.datas[0].low[0], market.datas[0].open[0], market.datas[0].high[0], market.datas[0].close[0])
                    return ShortSellPreSell()
        elif market.adx > 25.6 and market.diPlus > market.adx:
            print("long sell", market.datas[0].close[0], market.datas[0].open[0], market.r1, market.r2, market.r3)
            if (market.datas[0].close[0] > market.r1 and market.datas[0].open[0] < market.r1) or (market.datas[0].close[0] > market.r2 and market.datas[0].open[0] < market.r2) or (market.datas[0].close[0] > market.r3 and market.datas[0].open[0] < market.r3) :
                print("long sell entry", market.datas[0].low[0], market.datas[0].open[0], market.datas[0].high[0], market.datas[0].close[0])
                return PreBuy()
        return self

class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.ema = bt.indicators.ExponentialMovingAverage(self.datas[0], period=13, plot = False)
        self.Adx = bt.indicators.AverageDirectionalMovementIndex(self.datas[0], period=14, plot = False)
        self.indicator = bt.indicators.FibonacciPivotPoint(self.data1)
        self.state = Initial()

        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.b = False

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        self.diPlus = self.Adx.DIplus[0]
        self.diMinus = self.Adx.DIminus[0]
        self.adx = self.Adx.lines.adx[0]
        self.r1, self.r2, self.r3 = self.indicator.lines.r1[0], self.indicator.lines.r2[0], self.indicator.lines.r3[0]
        self.s1, self.s2, self.s3 = self.indicator.lines.s1[0], self.indicator.lines.s2[0], self.indicator.lines.s3[0]
        self.log('Close, %.2f' % self.dataclose[0])
        self.state = self.state.feed(self)
       

def get_historical_data(symbol):
    raw_df =   yf.download(
        tickers = symbol,
        period = "60d",
        interval = "5m",
        group_by = 'ticker',
        prepost = True,
        threads = True,
        proxy = None
    )
    return raw_df


# if __name__ == '__main__':
#     cerebro = bt.Cerebro()
#     cerebro.addstrategy(TestStrategy)

#     cerebro.adddata(data)
#     cerebro.resampledata(data, timeframe=bt.TimeFrame.Days).plotinfo.plot = False
#     cerebro.broker.setcash(70000.0)
#     cerebro.addsizer(bt.sizers.FixedSize, stake=10)
#     cerebro.broker.setcommission(commission=0.0)
#     print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
#     cerebro.run()
#     print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

file = pd.read_csv("stocks1.csv")
ans = []
for i, t in enumerate(file['Ticker'].iloc[:400]):
    print("Current :", i+1)
    try:
        dataframe = get_historical_data(t +'.NS')
        data = bt.feeds.PandasData(dataname=dataframe, timeframe=bt.TimeFrame.Minutes)
        cerebro = bt.Cerebro()
        cerebro.addstrategy(TestStrategy)

        cerebro.adddata(data)
        cerebro.resampledata(data, timeframe=bt.TimeFrame.Days).plotinfo.plot = False
        cerebro.broker.setcash(70000.0)
        cerebro.addsizer(bt.sizers.FixedSize, stake=10)
        cerebro.broker.setcommission(commission=0.0)
        # print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.run()
        # print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        ans.append((cerebro.broker.getvalue(), t))
    except ZeroDivisionError:
        print("division by zero error")

ans.sort(reverse=True)
data = []
for v, t in ans:
    data.append([t, v])
df = pd.DataFrame(data, columns=["Ticker", "Return"])
df.to_csv("output1.csv")