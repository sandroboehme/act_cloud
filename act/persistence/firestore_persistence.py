import json
import os

from google.cloud import firestore

from act.persistence.persistence import Persistence
from definitions import ROOT_PATH, CONFIG_PATH


class FirestorePersistence(Persistence):

    def __init__(self, path, name, running_in_cloud=False):
        Persistence.__init__(self, path, name)

        if not running_in_cloud:
            auth_file_path = os.path.join(ROOT_PATH, 'auth.json')
            os.environ['GRPC_DNS_RESOLVER'] = 'native'
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = auth_file_path

        self.db = firestore.Client()

    def save_setup_impl(self, path, name, setup):
        doc_ref = self.db.document(path, name)
        doc_ref.set(setup)

    def update_setup_impl(self, path, name, setup):
        doc_ref = self.db.document(path, name)
        doc_ref.update(setup)

    def get_setup_impl(self, path, name):
        doc = self.db.document(path, name)
        return doc.get().to_dict()

    def delete_setup_impl(self, path, name):
        doc = self.db.document(path, name)
        collections = doc.collections()
        for collection in collections:
            self.delete_collection(collection, 50)

    def get_exchange_config_impl(self, path):
        doc = self.db.document(path)
        return doc.get().to_dict()

    def save_exchange_config(self, config):
        exchange_config_path = self.get_exchange_config_path()
        doc_ref = self.db.document(exchange_config_path)
        doc_ref.set(config)

    ######################################################################################################
    def get_strategy_state_coll(self):
        cs = self.db.collection(f'{self.path}/{self.name}/{Persistence.FOLDER_NAME_STRATEGY_STATE}')
        return cs

    def save_strategy_state_impl(self, new_strategy_state_content, iteration_index):
        doc_ref = self.db.document(f'{self.path}/{self.name}/{Persistence.FOLDER_NAME_STRATEGY_STATE}/{iteration_index}.json')
        new_strategy_state = {'iteration_index': iteration_index, 'content': new_strategy_state_content}
        doc_ref.set(new_strategy_state)
        return new_strategy_state

    def get_last_strategy_state_impl(self):
        cs = self.get_strategy_state_coll()

        last_doc_generator = cs.order_by('iteration_index', direction=firestore.Query.DESCENDING).limit(1).stream()
        last_doc = next(last_doc_generator, None)
        return last_doc.to_dict() if last_doc is not None else None

    def delete_collection(self, coll_ref, batch_size):
        batch = self.db.batch()
        docs = coll_ref.limit(batch_size).stream()
        deleted = 0

        for doc in docs:
            batch.delete(doc.reference)
            deleted = deleted + 1

        batch.commit()
        if deleted > 0:
            return self.delete_collection(coll_ref, batch_size)
