import yfinance as yf
import backtrader as bt
import random
import pandas as pd
import numpy as np

class ShortSellBuy():
    def __init__(self, low, close) -> None:
        self.low = low
        self.close = close

    def feed(self, market):
        if market.datas[0].close[0] > market.datas[0].close[-1]:
            market.buy()
            return Initial()
        elif market.datas[0].low[0] < market.ema[0]:
            return ShortSellSell(self.low, self.close)
        else:
            return self

class ShortSellSell():
    def __init__(self, low, close) -> None:
        self.low = low
        self.close = close
    
    def feed(self, market):
        if market.datas[0].close[0] > market.ema[0]:
            return ShortSellBuy(self.low, self.close)
        elif market.datas[0].close[0] > self.close:
            market.buy()
            return Initial()
        else:
            return self

class ShortSellPreSell():
    def __init__(self, low, close) -> None:
        self.low = low
        self.close = close
    
    def feed(self, market):
        if market.datas[0].low[0] < self.low:
            market.sell()
            return ShortSellSell(self.low, self.close)
        return Initial()

class PreSell():
    def __init__(self, low) -> None:
        self.low = low

    def feed(self, market):
        print("Pre sell state")
        if market.datas[0].low[0] > market.ema[0]:
            return Buy(self.low)
        elif market.datas[0].low[0] < market.datas[0].low[-1]:
            print("profit sell", market.datas[0].close[0])
            market.order = market.sell()
            return Initial()
        else:
            return self

class Buy():
    def __init__(self, low) -> None:
        self.low = low

    def feed(self, market):
        print("Buy State")
        if self.low > market.datas[0].low[0]:
            print("loss sell price", market.datas[0].close[0])
            market.order = market.sell()
            return Initial()
        elif market.datas[0].low[0] < market.ema[0]:
            return PreSell(self.low)
        else:
            return self

class PreBuy():
    def __init__(self) -> None:
        pass

    def feed(self, market):
        print("Prebuy")
        if market.datas[0].close[-1] < market.datas[0].close[0]:
            print("buy price", market.datas[0].close[0])
            market.order = market.buy()
            return Buy(market.datas[0].low[-1])
        elif market.datas[0].close[0] > market.r1 or market.datas[0].close[0] > market.r2 or market.datas[0].close[0] > market.r3:
            return PreBuy()
        else:
            return Initial()

class Initial():

    def __init__(self) -> None:
        pass
    
    def feed(self, market):
        print("Inital State", market.adx, market.diPlus)
        if market.indicator.lines.p[0] > market.datas[0].close[0]:
            if market.adx >= 25.6 and market.diMinus >= market.adx:
                if market.datas[0].low[0] < market.s3 or market.datas[0].low[0] < market.s2 or market.datas[0].low[0] < market.s1:
                    return ShortSellPreSell(market.datas[0].low[0], market.datas[0].close[0])
        elif market.adx >= 25.6 and market.diPlus >= market.adx:
            print(market.datas[0].close[0], market.r1, market.datas[0].close[0], market.r2, market.datas[0].close[0], market.r3)
            if market.datas[0].close[0] > market.r1 or market.datas[0].close[0] > market.r2 or market.datas[0].close[0] > market.r3:
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
        self.ema = bt.indicators.ExponentialMovingAverage(self.datas[0], period=13)
        self.Adx = bt.indicators.AverageDirectionalMovementIndex(self.datas[0])
        self.indicator = bt.indicators.FibonacciPivotPoint(self.data1)
        self.state = Initial()

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.b = False
        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
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
        period = "10d",
        interval = "5m",
        group_by = 'ticker',
        prepost = True,
        threads = True,
        proxy = None
    )
    return raw_df

dataframe = get_historical_data('GOOG')
print(dataframe.head())
data = bt.feeds.PandasData(dataname=dataframe)

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    cerebro.adddata(data)
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes)
    # Set our desired cash start
    cerebro.broker.setcash(70000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()

