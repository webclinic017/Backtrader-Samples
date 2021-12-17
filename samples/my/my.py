import backtrader as bt
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Create a subclass of Strategy to define the indicators and logic


class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=2,  # period for the fast moving average
        pslow=2  # period for the slow moving average
    )

  
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
    def prenext(self):
        self.log('prenext')

    def nextstart(self):
        self.log('nextstart')
        self.next()
    
    def start(self):
        self.log('start')
    
    def stop(self):
        self.log('stop')
    

    def __init__(self):
        self.log('init')
        self.sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(self.sma1, sma2)  # crossover signal

    def notify_order(self, order):

        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        self.log('next sma %.2f'%self.sma1.sma[0])
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.log('BUY CREATE, %.2f' % self.data.close[0])
                self.buy()  # enter long

        elif self.crossover < 0:  # in the market & cross to the downside
            self.log('SELL CREATE, %.2f' % self.data.close[0])
            self.sell()  # close long position


cerebro = bt.Cerebro()  # create a "Cerebro" engine instance

# Datas are in a subfolder of the samples. Need to find where the script is
# because it could have been called from anywhere
modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
print('aa', modpath)
datapath = os.path.join(modpath, './orcl-1995-2014.txt')
print('bb', datapath)
# Create a Data Feed
data = bt.feeds.YahooFinanceCSVData(
    dataname=datapath,
    # Do not pass values before this date
    fromdate=datetime.datetime(1995, 1, 3),
    # Do not pass values before this date
    todate=datetime.datetime(1995, 4, 3),
    # Do not pass values after this date
    reverse=False)

cerebro.adddata(data)  # Add the data feed

cerebro.addstrategy(SmaCross)  # Add the trading strategy
cerebro.run()  # run it all
# cerebro.plot()  # and plot it with a single command

# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())