from os import path
import json
import time

from .item_database import ItemDatabase
from .item_bilingual import EntryItemDatabase, EntryBiLingFileList
from .item import FILE_ENCODING

def _get_relpath_hash(item):
    # helper function
    try:
        return item.relative_path, \
               item.version_id
    except:
        return None, None


class ExamQuestion(object):

    def __init__(self, shared_name, path_item, path_translation,
                 hash_item, hash_translation):
        self.shared_name = shared_name
        self.path_item = path_item
        self.path_translation = path_translation
        self.hash_item = hash_item
        self.hash_translation = hash_translation

    def is_same_as(self, other):
        return isinstance(other, ExamQuestion) and \
               self.shared_name == other.shared_name and \
               self.path_item == other.path_item and \
               self.path_translation == other.path_translation and \
               self.hash_item == other.hash_item and \
               self.hash_translation == other.hash_translation

    @staticmethod
    def from_database_item(db_item):
        assert isinstance(db_item, EntryItemDatabase)
        ip, ih = _get_relpath_hash(db_item.item)
        tp, th = _get_relpath_hash(db_item.translation)
        return ExamQuestion(shared_name=db_item.shared_name,
                            path_item=ip, path_translation=tp,
                            hash_item=ih, hash_translation=th)


class Exam(object):

    def __init__(self):
        """
        """
        self.questions = []
        self._time_last_change = None
        self.info = None

    @staticmethod
    def time_stamp():
        return time.strftime("%d-%m-%Y %H:%M", time.gmtime())

    def clear(self):
        self.questions = []
        self._time_last_change = Exam.time_stamp()

    def add_database_item(self, item):
        assert isinstance(item, (EntryItemDatabase, EntryBiLingFileList))
        if isinstance(item, EntryBiLingFileList):
            item = EntryItemDatabase.load(item, shared_name_with_bilingual_tag=False)

        self._time_last_change = Exam.time_stamp()
        path_item, hash_item = _get_relpath_hash(item.item)
        path_trans, hash_trans = _get_relpath_hash(item.translation)
        self.questions.append(ExamQuestion(shared_name=item.shared_name,
                                           path_item=path_item,
                                           path_translation=path_trans,
                                           hash_item=hash_item,
                                           hash_translation=hash_trans))

    def as_dict_list(self):

        return {"time" : self._time_last_change,
             "names": [x.shared_name for x in self.questions],
             "items": [x.path_item for x in self.questions],
             "translations" : [x.path_translation for x in self.questions],
             "item_version_ids": [x.hash_item for x in self.questions],
             "translation_version_ids": [x.hash_translation for x in self.questions]
              }

    def save(self, json_filename, info=None):
        print("Save {}".format(json_filename))
        if info is not None:
            self.info = info

        d = self.as_dict_list()
        if self.info is not None:
            d["info"] = self.info

        with open(json_filename, 'w', encoding=FILE_ENCODING) as fl:
            fl.write(json.dumps(d, indent = 2))

    def load(self, json_filename):
        with open(json_filename, 'r', encoding=FILE_ENCODING) as fl:
            d = json.load(fl)

        try:
            self._time_last_change = d["time"]
        except:
            self._time_last_change = None
        try:
            self.info = d["info"]
        except:
            self.info = None

        self.questions = []
        for x in range(len(d["names"])):

            self.questions.append(ExamQuestion(shared_name=d["names"][x],
                                               path_item=d["items"][x],
                                               path_translation=d["translations"][x],
                                               hash_item=d["item_version_ids"][x],
                                               hash_translation=d["translation_version_ids"][x]))

    def get_database_ids(self, item_db):
        """returns ids from item database"""
        if not isinstance(item_db, ItemDatabase):
            return None

        rtn = []
        for quest in self.questions:
            idx = item_db.find(
                item_version_id=quest.hash_item ,
                translation_version_id=quest.hash_translation,
                shared_name=quest.shared_name,
                item_relative_path=quest.path_item,
                translation_relative_path=quest.path_translation,
                find_all=False) # finds just first one
            rtn.append(idx)

        return rtn

    def find_item(self, item):
        """returns question id first occurance if item"""

        if not isinstance(item, EntryItemDatabase):
            return None
        else:
            needle = ExamQuestion.from_database_item(item)
            for x, quest in enumerate(self.questions):
                if quest.is_same_as(needle):
                    return x
            return None

    def remove_item(self, item):
        idx = self.find_item(item)
        if idx is not None:
            return self.questions.pop(idx)

    def replace(self, source_id, target_id):
        if source_id < len(self.questions) and target_id < len(self.questions):
            tmp = self.questions.pop(source_id)
            self.questions = self.questions[:target_id] + [tmp] + \
                             self.questions[target_id:]
            return True
        else:
            return False
