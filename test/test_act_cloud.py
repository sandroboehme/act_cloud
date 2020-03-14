import unittest

from act.ACT import ACT
from act.persistence.persistence_factory import PersistenceFactory
from act.persistence.persistence_type import PersistenceType
from act.store.ccxtstore import CCXTStore


class TestACTCloud(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestACTCloud, self).__init__(*args, **kwargs)

        self.binance_store = CCXTStore(exchange="binance",
                                       currency="BTC",
                                       retries=5
                                       )

        self.downtrend_setup = {
            "name": "downtrend_setup",
            "comments": [
                "Comment one",
                "Comment two, ..."
            ],
            "act": {
                "class_instance": {
                    "name": "ACT",
                    "module_name": "act.ACT",
                    "parameters": {
                        "data_feed": {
                            "class_instance": {
                                "name": "CCXTDataFeed",
                                "module_name": "act.data_feed.ccxt_data_feed",
                                "parameters": {
                                    "symbol": "BTC/USDT",
                                    "time_frame": "1m"
                                }
                            }
                        },
                        "store": {
                            "class_instance": {
                                "name": "CCXTStore",
                                "module_name": "act.store.ccxtstore",
                                "parameters": {
                                    "exchange": "binance",
                                    "currency": "BTC",
                                    "retries": 5
                                }
                            }
                        },
                        "strategy": {
                            "class_instance": {
                                "name": "TrendLineStrategy",
                                "module_name": "act.strategy.trend_line_strategy",
                                "parameters": {
                                    "x1":'2020-03-13 09:00:00',
                                    "y1":5785.09,
                                    "x2":'2020-03-13 23:00:00',
                                    "y2":5671.57
                                }
                            }
                        }
                    }
                }
            },
            "act_cloud_scheduler": {
                "topic": "act_runtime_v1",
                "cron": "* * * * *"
            }
        }

        self.uptrend_setup = {
            "name": "uptrend_setup",
            "comments": [
                "Comment one",
                "Comment two, ..."
            ],
            "act": {
                "class_instance": {
                    "name": "ACT",
                    "module_name": "act.ACT",
                    "parameters": {
                        "data_feed": {
                            "class_instance": {
                                "name": "CCXTDataFeed",
                                "module_name": "act.data_feed.ccxt_data_feed",
                                "parameters": {
                                    "symbol": "BTC/USDT",
                                    "time_frame": "1m"
                                }
                            }
                        },
                        "store": {
                            "class_instance": {
                                "name": "CCXTStore",
                                "module_name": "act.store.ccxtstore",
                                "parameters": {
                                    "exchange": "binance",
                                    "currency": "BTC",
                                    "retries": 5
                                }
                            }
                        },
                        "strategy": {
                            "class_instance": {
                                "name": "TrendLineStrategy",
                                "module_name": "act.strategy.trend_line_strategy",
                                "parameters": {
                                    "x1":'2020-03-13 05:00:00',
                                    "y1": 4849.65,
                                    "x2":'2020-03-13 19:00:00',
                                    "y2": 5011.96
                                }
                            }
                        }
                    }
                }
            },
            "act_cloud_scheduler": {
                "topic": "act_runtime_v1",
                "cron": "* * * * *"
            }
        }

    def test_prepare_cloud_run_setup_1(self):
        trade_setup_path = 'apps/cryptotrader-com/users/sandro/iterations/2020/2/9/setups/binance/btcusdt'
        setup_name = 'downtrend_setup'
        persistence = PersistenceFactory.get_persistance(PersistenceType.GOOGLE_FIRESTORE,
                                                         trade_setup_path,
                                                         name=setup_name)
        persistence.save_setup(self.downtrend_setup)
        persistence.delete_setup()


    def test_prepare_cloud_run_setup_2(self):
        trade_setup_path = 'apps/cryptotrader-com/users/sandro/iterations/2020/2/9/setups/binance/btcusdt'
        setup_name = 'uptrend_setup'
        persistence = PersistenceFactory.get_persistance(PersistenceType.GOOGLE_FIRESTORE,
                                                         trade_setup_path,
                                                         name=setup_name)
        persistence.save_setup(self.uptrend_setup)
        persistence.delete_setup()
