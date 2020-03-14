import importlib

from act.persistence.persistence import Persistence
from act.persistence.persistence_type import PersistenceType


class PersistenceFactory(object):

    @staticmethod
    def get_persistance(persistence_type, path=None, data=None, name=None, running_in_cloud=False):

        if path is None:
            path, name = Persistence.get_path_and_name_from_data(data)

        json_file_extension = '.json'
        if name.endswith(json_file_extension):
            name = name[:-len(json_file_extension)]

        if persistence_type == PersistenceType.GOOGLE_FIRESTORE:
            module = importlib.import_module(PersistenceType.GOOGLE_FIRESTORE['module_name'])
            instance = getattr(module, PersistenceType.GOOGLE_FIRESTORE['class_name'])(path, name, running_in_cloud)
            return instance
        else:
            # TODO: That creates a runtime dependency to the FS persistance in the cloud.
            # Not sure yet if that's the way to go.
            module = importlib.import_module(PersistenceType.FS['module_name'])
            instance = getattr(module, PersistenceType.FS['class_name'])(path, name)
            return instance
