import pickle
import unittest
from datetime import datetime, timedelta
import time

from act.ACT import ACT
from act.data_feed.ccxt_data_feed import CCXTDataFeed
from act.indicator.TrendLine import TrendLine

from act.persistence.persistence_factory import PersistenceFactory
from act.persistence.persistence_type import PersistenceType
from act.store.ccxtstore import CCXTStore
from act.strategy.recording_strategy import RecordingStrategy
from act.strategy.trend_line_strategy import TrendLineStrategy


class TestACT(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestACT, self).__init__(*args, **kwargs)

        self.binance_store = CCXTStore(exchange="binance",
                                       currency="BTC",
                                       config=ACT.get_binance_config(),
                                       retries=5
                                       )

    def test_ACT_CCXT_forward_testing_intra_time_frame(self):

        # This should run the strategy 4 times. 3 times with the previous minute as full
        # candle and lastly with the minute of the to_date as the full candle.
        #
        # The from_date is set to the next full minute and the to_date a minute later.
        # The strategy is expected to run until the full candle for the to_date can be
        # retrieved from the exchange.
        #
        # If the current date is 01:04:33 pm the to_date is set to 01:05:00 pm.
        # The LocalScheduledPush starts at the next interval which will also be 01:05:03 pm.
        #
        # The strategy will run the 1st time at 01:05:xx.
        # This means a few seconds after 01:05 pm as the exchange will need a few seconds to
        # generate a new candle after 01:05. At this point the strategy will get the full candle
        # for 01:04 pm and the candle that is currently developing for 01:05 pm.
        #
        # The strategy will run the 2nd time a few seconds after 01:06 pm and will finally get
        # the full candle for the to_date (01:05 pm) as well as the next developing candle (01:06 pm).
        #
        act, from_date, to_date = TestACT.get_ACT_instance_for_intra_time_frame_test(local=True)
        local_scheduler = LocalScheduledPush(act, time_frame="20s")
        local_scheduler.run()

        strategy = act.get_strategy()

        self.assert_ccxt_forward_intra_time_frame_test(from_date, strategy, to_date)

    @staticmethod
    def get_ACT_instance_for_intra_time_frame_test(local=False):
        now = TestACT.get_now_avoid_scheduler_start_time()
        start_of_current_minute = now.replace(second=0, microsecond=0)
        from_date = start_of_current_minute + timedelta(minutes=1)
        to_date = start_of_current_minute+timedelta(minutes=2)
        print("datetime.now ", datetime.now(tz=UTC))
        print("from_date ", from_date)
        print("from_date ", from_date.timestamp())
        print("to_date ", to_date)
        print("to_date ", to_date.timestamp())

        data_feed = CCXTDataFeed('BTC/USDT',
                                 from_date = from_date,
                                 to_date = to_date,
                                 time_frame="1m")

        local_binance_store = CCXTStore(exchange="binance",
                                        currency="BTC",
                                        config=ACT.get_binance_config(),
                                        retries=5
                                        )

        strategy = RecordingStrategy()
        act = ACT(data_feed,
                  local_binance_store,
                  strategy,
                  # TODO: Think of a better way
                  from_date=from_date)

        if local:
            return act, from_date, to_date
        else:
            return act

    def assert_ccxt_forward_intra_time_frame_test(self, from_date, strategy, to_date):
        print("recorded iterations: ", strategy.recorded_iterations)
        assert len(strategy.recorded_iterations) == 4
        first_strategy_iteration_full_candle, first_strategy_iteration_developing_candle = strategy.recorded_iterations[
            0]
        second_strategy_iteration_full_candle, second_strategy_iteration_developing_candle = \
            strategy.recorded_iterations[1]
        third_strategy_iteration_full_candle, third_strategy_iteration_developing_candle = strategy.recorded_iterations[
            2]
        fourth_strategy_iteration_full_candle, fourth_strategy_iteration_developing_candle = \
            strategy.recorded_iterations[3]
        from_date_plus_1m = (from_date + timedelta(minutes=1)).timestamp()
        assert first_strategy_iteration_full_candle[0].timestamp() == from_date.timestamp()
        assert first_strategy_iteration_developing_candle[0].timestamp() == from_date_plus_1m  # 3 sec
        assert second_strategy_iteration_full_candle[0].timestamp() == from_date.timestamp()
        assert second_strategy_iteration_developing_candle[0].timestamp() == from_date_plus_1m  # 23 sec
        assert third_strategy_iteration_full_candle[0].timestamp() == from_date.timestamp()
        assert third_strategy_iteration_developing_candle[0].timestamp() == from_date_plus_1m  # 43 sec
        assert fourth_strategy_iteration_full_candle[0].timestamp() == to_date.timestamp()
        assert fourth_strategy_iteration_developing_candle[0].timestamp() == (
                to_date + timedelta(minutes=1)).timestamp()  # 3sec
        assert TestACT.candle_has_data(first_strategy_iteration_full_candle)
        assert TestACT.candle_has_data(first_strategy_iteration_developing_candle)
        assert TestACT.candle_has_data(second_strategy_iteration_full_candle)
        assert TestACT.candle_has_data(second_strategy_iteration_developing_candle)
        assert TestACT.candle_has_data(third_strategy_iteration_full_candle)
        assert TestACT.candle_has_data(third_strategy_iteration_developing_candle)
        assert TestACT.candle_has_data(fourth_strategy_iteration_full_candle)
        assert TestACT.candle_has_data(fourth_strategy_iteration_developing_candle)


if __name__ == '__main__':
    unittest.main()
