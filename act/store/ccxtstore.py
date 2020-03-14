#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2017 Ed Bartosh <bartosh@gmail.com>
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

import json
import time
from datetime import datetime
from functools import wraps

import ccxt
from ccxt.base.errors import NetworkError, ExchangeError


class CCXTStore(object):
    '''API provider for CCXT feed and broker classes.

    Added a new get_wallet_balance method. This will allow manual checking of the balance.
        The method will allow setting parameters. Useful for getting margin balances

    Added new private_end_point method to allow using any private non-unified end point

    '''

    @staticmethod
    def nonce_fct():
        return str(int(time.time() * 1000))

    @staticmethod
    def get_binance_config():
        store_config = {
            # 'apiKey': runtime_config["keys"]["binance"]["apikey"],
            # 'secret': runtime_config["keys"]["binance"]["secret"],
            'enableRateLimit': True,
            'nonce': CCXTStore.nonce_fct,
        }
        return store_config

    @staticmethod
    def get_exchange(exchange):
        return getattr(ccxt, exchange)({
            # 'apiKey': runtime_config["keys"]["binance"]["apikey"],
            # 'secret': runtime_config["keys"]["binance"]["secret"],
            'enableRateLimit': True,
            'nonce': CCXTStore.nonce_fct,
        })

    def __setstate__(self, d):
        self.__dict__ = d
        self.exchange = CCXTStore.get_exchange(d['exchange_name'])

    def __init__(self, exchange, currency, config=None, retries=5, debug=False):
        self.exchange_name = exchange
        self.exchange = CCXTStore.get_exchange(exchange)
        self.currency = currency
        self.retries = retries
        self.debug = debug
        # balance = self.exchange.fetch_balance() if 'secret' in config else 0
        self._cash = 0 #if balance == 0 else balance['free'][currency]
        self._value = 0 #if balance == 0 else balance['total'][currency]

    def retry(method):
        @wraps(method)
        def retry_method(self, *args, **kwargs):
            for i in range(self.retries):
                if self.debug:
                    print('{} - {} - Attempt {}'.format(datetime.now(), method.__name__, i))
                time.sleep(self.exchange.rateLimit / 1000)
                try:
                    return method(self, *args, **kwargs)
                except (NetworkError, ExchangeError):
                    if i == self.retries - 1:
                        raise

        return retry_method

    @retry
    def get_wallet_balance(self, currency, params=None):
        balance = self.exchange.fetch_balance(params)
        return balance

    @retry
    def get_balance(self):
        balance = self.exchange.fetch_balance()
        self._cash = balance['free'][self.currency]
        self._value = balance['total'][self.currency]

    @retry
    def getposition(self):
        return self._value
        # return self.getvalue(currency)

    @retry
    def create_order(self, symbol, order_type, side, amount, price, params):
        # returns the order
        return self.exchange.create_order(symbol=symbol, type=order_type, side=side,
                                          amount=amount, price=price, params=params)

    @retry
    def cancel_order(self, order_id, symbol):
        return self.exchange.cancel_order(order_id, symbol)

    @retry
    def fetch_trades(self, symbol):
        return self.exchange.fetch_trades(symbol)

    @retry
    def fetch_ohlcv(self, symbol, timeframe, since, limit, params={}):
        if self.debug:
            print('Fetching: {}, TF: {}, Since: {}, Limit: {}'.format(symbol, timeframe, since, limit))
        return self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit, params=params)

    @retry
    def fetch_order(self, oid, symbol):
        return self.exchange.fetch_order(oid, symbol)

    @retry
    def fetch_open_orders(self):
        return self.exchange.fetchOpenOrders()

    @retry
    def private_end_point(self, type, endpoint, params):
        '''
        Open method to allow calls to be made to any private end point.
        See here: https://github.com/ccxt/ccxt/wiki/Manual#implicit-api-methods

        - type: String, 'Get', 'Post','Put' or 'Delete'.
        - endpoint = String containing the endpoint address eg. 'order/{id}/cancel'
        - Params: Dict: An implicit method takes a dictionary of parameters, sends
          the request to the exchange and returns an exchange-specific JSON
          result from the API as is, unparsed.

        To get a list of all available methods with an exchange instance,
        including implicit methods and unified methods you can simply do the
        following:

        print(dir(ccxt.hitbtc()))
        '''
        return getattr(self.exchange, endpoint)(params)
