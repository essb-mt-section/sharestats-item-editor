from os import path
import json
import time

from .item_database import ItemDatabase
from .item_bilingual import EntryItemDatabase, EntryBiLingFileList

class Exam(object):

    def __init__(self, item_database=None):
        """param:
            item_database: ItemDatabase or base folder
        """
        self._shared_names = []
        self._items  = []
        self._translations = []
        self._item_hash = []
        self._trans_hash = []
        self._time_last_change = None
        self.item_db = None
        self.set_item_database(item_database)

    @staticmethod
    def time_stamp():
        return time.strftime("%d-%m-%Y %H:%M", time.gmtime())

    def set_item_database(self, item_database):

        if isinstance(item_database, ItemDatabase):
            self.item_db = item_database
        elif isinstance(item_database, str) and path.isdir(item_database) :
            self.item_db = ItemDatabase(item_database)
        else:
            self.item_db = None

    def clear(self):
        self._shared_names = []
        self._items  = []
        self._translations = []
        self._item_hash = []
        self._trans_hash = []
        self._time_last_change = Exam.time_stamp()

    def add_item(self, item):
        assert isinstance(item, (EntryItemDatabase, EntryBiLingFileList))
        if isinstance(item, EntryBiLingFileList):
            item = EntryItemDatabase.load(item, add_bilingual_tag=False)

        self._shared_names.append(item.shared_name)
        self._time_last_change = Exam.time_stamp()
        try:
            self._items.append(item.item.relative_path)
            self._item_hash.append(item.item.version_id())
        except:
            self._items.append(None)
            self._item_hash.append(None)
        try:
            self._translations.append(item.translation.relative_path)
            self._trans_hash.append(item.translation.version_id())
        except:
            self._translations.append(None)
            self._trans_hash.append(None)

    def as_dict_list(self):
        return {"time" : self._time_last_change,
             "base_dir": self.item_db.base_directory,
             "names": self._shared_names,
             "items": self._items,
             "translations" : self._translations,
             "item_version_ids": self._item_hash,
             "translation_version_ids": self._trans_hash}

    def save(self, json_filename):
        with open(json_filename, 'w') as fl:
            fl.write(json.dumps(self.as_dict_list(), indent = 2))

    def load(self, json_filename):
        with open(json_filename, 'r') as fl:
            d = json.load(fl)

        try:
            self._time_last_change = d["time"]
        except:
            self._time_last_change = None

        if path.isdir(d["base_dir"]):
            self.item_db = ItemDatabase(d["base_dir"])

        self._items = d["items"]
        self._translations = d["translations"]
        self._item_hash = d["item_version_ids"]
        self._trans_hash = d["translation_version_ids"]
        self._shared_names = d["names"]

    def get_database_ids(self):
        """returns ids from item database"""
        if not isinstance(self.item_db, ItemDatabase):
            return None

        rtn = []
        for x in range(len(self._items)):
            idx = self.item_db.find_version(
                item_version_id=self._item_hash[x],
                translation_version_id=self._trans_hash[x],
                shared_name=self._shared_names[x],
                item_relative_path=self._items[x],
                translation_relative_path=self._translations[x])

            if len(idx):
                rtn.append(idx[0])
            else:
                rtn.append(None)

        return rtn
