from act.indicator.TrendLine import TrendLine
from act.strategy.strategy import Strategy


class TrendLineStrategy(Strategy):

    def __init__(self, x1='2017-12-18 00:00:00', y1 = 18865.00, x2 = '2019-08-12 00:00:00', y2 = 11539.08):
        self.tl = TrendLine(strategy=self, x1=x1, y1=y1, x2=x2, y2=y2)
        self.close_above = list()
        self.wick_above = list()
        self.iteration_count = 0
        self.candles = list()

    def process_next_candle(self):
        self.iteration_count += 1
        previous_complete_candle = self.get_data().get_previous_complete_candle()
        self.candles.append(previous_complete_candle)
        print("previous_complete_candle: ", previous_complete_candle)
        trend_line_price = self.tl.calculate_result()
        print(trend_line_price)
        is_wick_above = trend_line_price < previous_complete_candle[2] \
                        and trend_line_price > previous_complete_candle[4]
        if is_wick_above:
            candle_date, tl_price, high = previous_complete_candle[0], trend_line_price, previous_complete_candle[2]
            print("wick_above: ", candle_date, tl_price, previous_complete_candle)
            self.wick_above.append((candle_date, tl_price, previous_complete_candle))

        is_close_above = trend_line_price < previous_complete_candle[4]
        if is_close_above:
            candle_date, tl_price, high = previous_complete_candle[0], trend_line_price, previous_complete_candle[4]
            print("close_above: ", candle_date, tl_price, previous_complete_candle)
            self.close_above.append((candle_date, tl_price, previous_complete_candle))

        return True
