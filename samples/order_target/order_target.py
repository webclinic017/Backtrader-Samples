#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015, 2016 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
from datetime import datetime

import backtrader as bt


class TheStrategy(bt.Strategy):
    '''
    This strategy is loosely based on some of the examples from the Van
    K. Tharp book: *Trade Your Way To Financial Freedom*. The logic:

      - Enter the market if:
        - The MACD.macd line crosses the MACD.signal line to the upside
        - The Simple Moving Average has a negative direction in the last x
          periods (actual value below value x periods ago)

     - Set a stop price x times the ATR value away from the close

     - If in the market:

       - Check if the current close has gone below the stop price. If yes,
         exit.
       - If not, update the stop price if the new stop price would be higher
         than the current
    '''

    params = (
        ('use_target_size', False),
        ('use_target_value', False),
        ('use_target_percent', False),
    )

    def notify_order(self, order):
        if order.status == order.Completed:
            pass

        if not order.alive():
            self.order = None  # indicate no order is pending

    def start(self):
        self.order = None  # sentinel to avoid operrations on pending order

    def next(self):
        dt = self.data.datetime.date()

        portfolio_value = self.broker.get_value()
        print('%04d - %s - Position Size:     %02d - Value %.2f' %
              (len(self), dt.isoformat(), self.position.size, portfolio_value))

        data_value = self.broker.get_value([self.data])

        if self.p.use_target_value:
            print('%04d - %s - data value %.2f' %
                  (len(self), dt.isoformat(), data_value))

        elif self.p.use_target_percent:
            port_perc = data_value / portfolio_value
            print('%04d - %s - data percent %.2f' %
                  (len(self), dt.isoformat(), port_perc))

        if self.order:
            return  # pending order execution

        size = dt.day
        if (dt.month % 2) == 0:
            size = 31 - size

        if self.p.use_target_size:
            target = size
            print('%04d - %s - Order Target Size: %02d' %
                  (len(self), dt.isoformat(), size))

            self.order = self.order_target_size(target=size)

        elif self.p.use_target_value:
            value = size * 1000

            print('%04d - %s - Order Target Value: %.2f' %
                  (len(self), dt.isoformat(), value))

            self.order = self.order_target_value(target=value)

        elif self.p.use_target_percent:
            percent = size / 100.0

            print('%04d - %s - Order Target Percent: %.2f' %
                  (len(self), dt.isoformat(), percent))

            self.order = self.order_target_percent(target=percent)


def runstrat(args=None):
    args = parse_args(args)

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000)

    dkwargs = dict()
    if args.fromdate is not None:
        dkwargs['fromdate'] = datetime.strptime(args.fromdate, '%Y-%m-%d')
    if args.todate is not None:
        dkwargs['todate'] = datetime.strptime(args.todate, '%Y-%m-%d')

    # data
    # data = bt.feeds.YahooFinanceCSVData(dataname=args.data, **dkwargs)
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(1995, 1, 3),
        # Do not pass values before this date
        todate=datetime.datetime(1995, 4, 3),
        # Do not pass values after this date
        reverse=False)

    cerebro.adddata(data)

    # strategy
    cerebro.addstrategy(TheStrategy,
                        use_target_size=200, # args.target_size,
                        use_target_value=5000, # args.target_value,
                        use_target_percent=0.5) # args.target_percent)

    cerebro.run()


runstrat()