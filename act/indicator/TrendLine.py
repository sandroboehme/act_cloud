import datetime

import time


class TrendLine:
    '''
    Implementation mostly copied from https://backtest-rookies.com/2017/06/21/backtrader-trend-line-indicator/
    Thanks for the great work!

    The indicator requires two price points and date points to serve as X and Y
    values in calcuating the slope and the future expected price trend

    x1 = Date/Time, String in the following format "YYYY-MM-DD HH:MM:SS" of
    the start of the trend
    y1 = Float, the price (Y value) of the start of the trend.
    x2 = Date/Time, String in the following format "YYYY-MM-DD HH:MM:SS" of
    the end of the trend
    y2 = Float, the price (Y value) of the end of the trend.
    '''

    def __init__(self, strategy=None, x1=None, y1=None, x2=None, y2=None):
        self.strategy = strategy
        self.x1 = datetime.datetime.strptime(x1, "%Y-%m-%d %H:%M:%S")
        self.x2 = datetime.datetime.strptime(x2, "%Y-%m-%d %H:%M:%S")
        self.y1 = y1
        self.y2 = y2
        x1_time_stamp = time.mktime(self.x1.timetuple())
        x2_time_stamp = time.mktime(self.x2.timetuple())
        self.m = TrendLine.get_slope(x1_time_stamp,x2_time_stamp,self.y1,self.y2)
        self.B = TrendLine.get_y_intercept(self.m, x1_time_stamp, self.y1)
        self.result = None

    def calculate_result(self):
        self.process_next_candle()
        return self.result

    def process_next_candle(self):
        current_candle = self.strategy.get_data().get_previous_complete_candle()
        self.result = self.get_y_for_date(current_candle[0])

    def get_y_for_date(self, current_date):
        date_timestamp = time.mktime(current_date.timetuple())
        return self.get_y(date_timestamp)

    @staticmethod
    def get_slope(x1,x2,y1,y2):
        m = (y2-y1)/(x2-x1)
        return m

    @staticmethod
    def get_y_intercept(m, x1, y1):
        b=y1-m*x1
        return b

    def get_y(self,ts):
        Y = self.m * ts + self.B
        return Y
