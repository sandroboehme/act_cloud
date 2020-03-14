from enum import Enum


class PersistenceType:
    # (id, module name, class name)
    FS = {'key':'fs',
          'module_name': 'act.persistence.filesystem_persistence',
          'class_name': 'FilesystemPersistence'}
    GOOGLE_FIRESTORE = {'key':'google_firestore',
                        'module_name': 'act.persistence.firestore_persistence',
                        'class_name': 'FirestorePersistence'}

