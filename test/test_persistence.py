import json
import os
import unittest

from act.persistence.persistence import Persistence
from act.persistence.persistence_factory import PersistenceFactory
from definitions import ROOT_PATH


class TestPersistence(unittest.TestCase):

    def setUp(self):
        auth_file_path = os.path.join(ROOT_PATH, 'auth.json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = auth_file_path
        abs_param_file = os.path.join(ROOT_PATH, 'test/backtestBNBPsarSL.json')
        with open(abs_param_file, 'r') as f:
            trade_setup = json.load(f)
            self.trade_parameter = dict(exchange=trade_setup['exchange'],
                                        pair=trade_setup['symbol'],
                                        year=trade_setup['fromdate']['year'],
                                        month=trade_setup['fromdate']['month'],
                                        day=trade_setup['fromdate']['day'],
                                        trade_id=trade_setup['name'])
        self.trade_setup_path = Persistence.get_path('local', 'binance', 'bnb/usdt')

    def test_get_path_from_data(self):
        # data should be
        # projects/example5-237118/databases/(default)/documents/' \
        #            'apps/cryptotrader-com/users/sandro/iterations/2019/5/20/' \
        #            'setups/binance/bnbusdt/backtestBNBPsarSL
        data = {'data': 'cHJvamVjdHMvZXhhbXBsZTUtMjM3MTE4L2RhdGFiYXNlcy8oZGVmYXVsdCkvZG9'
                        'jdW1lbnRzL2FwcHMvY3J5cHRvdHJhZGVyLWNvbS91c2Vycy9zYW5kcm8vaXRlcm'
                        'F0aW9ucy8yMDE5LzUvMjAvc2V0dXBzL2JpbmFuY2UvYm5idXNkdC9iYWNrdGVzd'
                        'EJOQlBzYXJTTA=='
                }
        path, name = Persistence.get_path_and_name_from_data(data)
        assert path == 'apps/cryptotrader-com/users/sandro/iterations/2019/5/20/setups/binance/bnbusdt'
        assert name == 'backtestBNBPsarSL'

    @unittest.skip("You may not want to copy your API keys to the Firestore just now.")
    def test_exchange_config(self):
        trade_setup_name = 'aTradeName'
        fs_p = PersistenceFactory.get_persistance(PersistenceType.FS,
                                                  self.trade_setup_path,
                                                  name=trade_setup_name)
        fs_config = fs_p.get_exchange_config()
        assert fs_config is not None

        firestore_p = PersistenceFactory.get_persistance(PersistenceType.GOOGLE_FIRESTORE,
                                                         self.trade_setup_path,
                                                         name=trade_setup_name)
        firestore_p.save_exchange_config(fs_config)
        firestore_config = firestore_p.get_exchange_config()
        assert firestore_config is not None
        assert firestore_config == fs_config

    def test_trade_setup_filesystem_persistence(self):
        persistence_imp = PersistenceFactory.get_persistance(PersistenceType.FS,
                                                             self.trade_setup_path,
                                                             name='backtestBNBPsarSL')
        self.trade_setup_persistence_test(persistence_imp)

    def test_trade_setup_firestore_persistence(self):
        persistence_imp = PersistenceFactory.get_persistance(PersistenceType.GOOGLE_FIRESTORE,
                                                             self.trade_setup_path,
                                                             name='backtestBNBPsarSL')
        self.trade_setup_persistence_test(persistence_imp)

    def trade_setup_persistence_test(self, persistence):
        abs_param_file = os.path.join(ROOT_PATH, 'test/backtestBNBPsarSL.json')

        persistence.delete_setup()

        with open(abs_param_file, 'r') as f:
            trade_setup = json.load(f)
            trade_setup['event_stop'] = False
            persistence.save_setup(trade_setup)
            retrieved_setup = persistence.get_setup()
            assert retrieved_setup == trade_setup
            persistence.end_setup()
            retrieved_setup = persistence.get_setup()
            assert retrieved_setup['event_stop']

    def test_persistence_type_handling(self):
        assert 'fs' == PersistenceType.FS.value
        assert 'google_cloud_storage' == PersistenceType.GOOGLE_CLOUD_STORAGE.value
        assert PersistenceType.FS == PersistenceType('fs')
        assert PersistenceType.GOOGLE_CLOUD_STORAGE == PersistenceType('google_cloud_storage')

    def test_file_system_persistence(self):
        persistence_imp = PersistenceFactory.get_cs_persistance(PersistenceType.FS,
                                                                  **self.trade_parameter,
                                                                  root_path=ROOT_PATH)
        self.persistence_impl_test(persistence_imp)

    def test_gcloud_storage_persistence(self):
        persistence_imp = PersistenceFactory.get_cs_persistance(PersistenceType.GOOGLE_CLOUD_STORAGE,
                                                                  **self.trade_parameter)
        self.persistence_impl_test(persistence_imp)

    def persistence_impl_test(self, persistence_imp):
        """
        Tests if it's possible to store the candle state initially when no trade folder is there yet and in
        subsequent cases when there is a previous candle state.
        :param persistence_imp:
        :param trade_parameter:
        :return:
        """
        persistence_imp.delete_trade()
        persistence_imp.save_strategy_state(candle_state={'aKey': 'aValue'})
        candle_state, path = persistence_imp.get_last_strategy_state()
        assert candle_state == {'aKey': 'aValue'}
        assert path == 'trades/binance/bnbusdt/2019/1/28/trailing_sl/1.json'

        persistence_imp.save_strategy_state(candle_state={'aKey2': 'aValue2'})
        candle_state, path = persistence_imp.get_last_strategy_state()
        assert candle_state == {'aKey2': 'aValue2'}
        assert path == 'trades/binance/bnbusdt/2019/1/28/trailing_sl/2.json'


if __name__ == '__main__':
    unittest.main()
