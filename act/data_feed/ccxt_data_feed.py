from datetime import datetime, timedelta

from pytz import UTC

from act.data_feed.data_feed import DataFeed


class CCXTDataFeed(DataFeed):

    TIME_FRAMES = {
        '5s': timedelta(seconds=5),
        '30s': timedelta(seconds=30),
        '1m': timedelta(minutes=1),
        '3m': timedelta(minutes=3),
        '5m': timedelta(minutes=5),
        '15m': timedelta(minutes=15),
        '30m': timedelta(minutes=30),
        '90m': timedelta(minutes=90),
        '1h': timedelta(hours=1),
        '2h': timedelta(hours=2),
        '3h': timedelta(hours=3),
        '4h': timedelta(hours=4),
        '6h': timedelta(hours=6),
        '8h': timedelta(hours=8),
        '12h': timedelta(hours=12),
        '1d': timedelta(days=1),
        '1w': timedelta(weeks=1),
        '2w': timedelta(weeks=2)
    }

    def __init__(self, symbol, from_date=None, to_date=None, from_date_str=None, to_date_str=None, time_frame='1m'):
        self.store = None
        self.symbol = symbol
        self.time_frame_key=time_frame
        self.time_frame=CCXTDataFeed.TIME_FRAMES.get(time_frame)
        self.has_next_candle = True
        self.previous_complete_candle = None
        self.current_developing_candle = None
        self.to_date = None

        if from_date_str is not None:
            self.from_date = datetime.strptime(from_date_str, '%Y-%m-%d %H:%M:%S')
        elif from_date is not None:
            self.from_date = from_date
        else:
            self.from_date = datetime.now(tz=UTC)

        # set tz to UTC
        self.from_date = self.from_date.replace(tzinfo=UTC) if self.from_date.tzinfo is None \
            else self.from_date.astimezone(tz=UTC)

        if to_date_str is not None:
            self.to_date = datetime.strptime(to_date_str, '%Y-%m-%d %H:%M:%S')
            self.to_date.replace(tzinfo=UTC)

        if to_date is not None:
            self.to_date = to_date.replace(tzinfo=UTC) if to_date.tzinfo is None \
                else to_date.astimezone(tz=UTC)

        load_full_candle_since_datetime = self.from_date if self.from_date is not None else datetime.now(tz=UTC)
        load_full_candle_since_datetime = load_full_candle_since_datetime.replace(second=0, microsecond=0)
        self.load_full_candle_since = int((load_full_candle_since_datetime - self.time_frame).timestamp())

        # calculate the next load_since value for the next candle
        self.next_full_candle_since = int((datetime.fromtimestamp(self.load_full_candle_since) + self.time_frame).timestamp())
        print("initial self.load_full_candle_since: ", self.load_full_candle_since)
        print("initial self.next_full_candle_since: ", self.next_full_candle_since)

    def set_store(self, store):
        self.store = store

    @staticmethod
    def dateparse (time_in_secs):
        return datetime.fromtimestamp(float(time_in_secs)/1000, tz=UTC)

    def load_next_candle(self):
        next_full_candle_available = datetime.now(tz=UTC).timestamp() > self.next_full_candle_since + self.time_frame.seconds
        print("next_full_candle_available: ", next_full_candle_available)

        if next_full_candle_available:
            self.load_full_candle_since = self.next_full_candle_since
            self.next_full_candle_since = int((datetime.fromtimestamp(self.load_full_candle_since) + self.time_frame).timestamp())
            print("self.load_full_candle_since: ", self.load_full_candle_since)
            print("self.next_full_candle_since: ", self.next_full_candle_since)

        print("load_full_candle_since: ", self.load_full_candle_since)
        ohlc = self.store.fetch_ohlcv(self.symbol, timeframe=self.time_frame_key,
                                      # The since timestamp is inclusive. Thus e.g. the timestamp for the
                                      # specified minute will also be returned by the fetch_ohlcv() method.
                                      since=self.load_full_candle_since * 1000,
                                      # Always load the last full and current intra timeframe candle.
                                      # During backtesting the second candle will be the next full candle.
                                      limit=2)

        self.previous_complete_candle = ohlc[0]
        developing_candle_available = len(ohlc) == 2
        self.current_developing_candle = ohlc[1] if developing_candle_available else None

        self.previous_complete_candle[0] = CCXTDataFeed.dateparse(self.previous_complete_candle[0])
        if developing_candle_available:
            self.current_developing_candle[0] = CCXTDataFeed.dateparse(self.current_developing_candle[0])
        prev_complete_candle_before_to_date = self.to_date is None \
            or self.to_date.timestamp() > self.previous_complete_candle[0].timestamp()

        self.has_next_candle = prev_complete_candle_before_to_date
        print(f"to_date {self.to_date} > prev_complete_candle {self.previous_complete_candle[0]}? {self.has_next_candle}")

        print(self.has_next_candle)
        return self.has_next_candle

    def got_next_candle(self):
        return self.has_next_candle
