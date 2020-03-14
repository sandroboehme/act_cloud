import pickle
from datetime import timedelta, datetime

import time

from pytz import UTC

from act.persistence.persistence_factory import PersistenceFactory
from act.persistence.persistence_type import PersistenceType


class ACT:

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
        '2w': timedelta(weeks=2),
    }

    # privat
    # available / online
    # testable
    #
    #
    # actbotc algorithmic crypto trading based on the cloud
    #
    # pcat

    # CACT Cloud based algorithmic crypto trading
    #
    # PCBACT Private Cloud based algorithmic crypto trading
    #
    # GCPACT Google Cloud Platform Algorithmic Crypto Trading
    #
    # GCACT
    #
    # CBACT
    #
    # CCT
    #
    # ACTIC


    # ACT Algorithmic Crypto Trading

    def __init__(self, data_feed, store=None, strategy=None, from_date=None, start_after_time_frame='1m'):
        self.data_feed = data_feed
        self.store = store
        if store is not None:
            data_feed.set_store(self.store)
        self.strategy = strategy
        self.strategy.set_data(self.data_feed)
        self.scheduler = None
        # TODO: Think of a better way than from_date and start_after_time_frame
        self.from_date = from_date
        self.start_after_time_frame = ACT.TIME_FRAMES.get(start_after_time_frame)
        self.iteration_count = 0

    def set_scheduler(self, scheduler):
        self.scheduler = scheduler

    def serialize(self, persistence):
        act = pickle.dumps(self, pickle.HIGHEST_PROTOCOL)

        candle_state_content = {
            'aKey': 'a value',
            'anOtherKey': 1234,
            'aNestedObj': {
                'aNestedKey': 12.12
            },
            'strategy': act
        }
        persistence.save_strategy_state(candle_state_content, self.iteration_count)

    def __getstate__(self):

        rv = vars(self).copy()
        if 'scheduler' in rv:
            del(rv['scheduler'])
        return rv

    @staticmethod
    def serialized_run(persistence_type=PersistenceType.GOOGLE_FIRESTORE,
                       setup_path=None, setup_name=None, scheduler=None, running_in_cloud=False):

        persistence = PersistenceFactory.get_persistance(persistence_type,
                                                         setup_path,
                                                         name=setup_name,
                                                         running_in_cloud=running_in_cloud)

        last_act_state = persistence.get_last_strategy_state()

        if last_act_state is None:
            act = persistence.get_act_instance_from_setup()
        else:
            last_act_string = last_act_state['content']['strategy']
            act = pickle.loads(last_act_string)

        if scheduler is not None:
            act.set_scheduler(scheduler)

        strategy = act.run()

        act.serialize(persistence)

        return strategy

    def run(self):
        print("ACT.run(): ", datetime.now(tz=UTC))
        print("ACT.run(): ", datetime.now(tz=UTC).timestamp())
        if self.from_date is not None \
                and datetime.now(tz=UTC) < self.from_date+self.start_after_time_frame:
            print("Not yet starting.")
            self.iteration_count += 1
            return True
        self.data_feed.load_next_candle()
        continue_running = self.strategy.process_next_candle()
        if (not continue_running or not self.data_feed.got_next_candle()) and self.scheduler is not None:
            self.scheduler.stop()
        self.iteration_count += 1
        return self.strategy

    def get_strategy(self):
        return self.strategy

