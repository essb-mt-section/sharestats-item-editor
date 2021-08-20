import json
import time

from ..consts import FILE_ENCODING
from .item_database import ItemDatabase, BiLingualRmdFilePair, EntryItemDatabase
from .item import RmdFile, RExamItem
from .item import AnswerList


def _get_relpath_and_hash(item):
    # helper function
    try:
        return item.relative_path, \
               item.hash()
    except:
        return None, None


class ExamQuestion:

    def __init__(self, shared_name, path_l1, path_l2,
                 hash_l1, hash_l2):

        self.shared_name = shared_name
        self.path_l1 = path_l1
        self.path_l2 = path_l2
        self.hash_l1 = hash_l1
        self.hash_l2 = hash_l2

    def is_same_as(self, other):
        return isinstance(other, ExamQuestion) and \
               self.shared_name == other.shared_name and \
               self.path_l1 == other.path_l1 and \
               self.path_l2 == other.path_l2 and \
               self.hash_l1 == other.hash_l1 and \
               self.hash_l2 == other.hash_l2

    @staticmethod
    def create_from_database_entry(db_item):
        assert isinstance(db_item, EntryItemDatabase)
        ip, ih = _get_relpath_and_hash(db_item.item_l1)
        tp, th = _get_relpath_and_hash(db_item.item_l2)

        return ExamQuestion(shared_name=db_item.shared_name,
                            path_l1=ip, path_l2=tp,
                            hash_l1=ih, hash_l2=th)

    def markdown_l1(self):
        return RExamItem(RmdFile(self.path_l1)).markdown()

    def markdown_l2(self):
        return RExamItem(RmdFile(self.path_l2)).markdown()


class Exam(object):

    def __init__(self, json_filename=None):
        """
        """
        self.questions = []
        self._time_last_change = None
        self.info = None
        self.json_filename = None
        self._item_db = None
        if json_filename is not None:
            self.load(json_filename)

    @property
    def item_database(self):
        return self._item_db

    @item_database.setter
    def item_database(self, v):
        assert(isinstance(v, ItemDatabase))
        self._item_db = v

    @staticmethod
    def time_stamp():
        return time.strftime("%d-%m-%Y %H:%M", time.gmtime())

    def clear(self):
        self.questions = []
        self._time_last_change = Exam.time_stamp()

    def add_database_item(self, item):
        assert isinstance(item, (EntryItemDatabase, BiLingualRmdFilePair))
        if isinstance(item, BiLingualRmdFilePair):
            item = EntryItemDatabase.load(item, shared_name_with_bilingual_tag=False)

        self._time_last_change = Exam.time_stamp()
        path_l1, hash_l1 = _get_relpath_and_hash(item.item_l1)
        path_l2, hash_l2 = _get_relpath_and_hash(item.item_l2)
        self.questions.append(ExamQuestion(shared_name=item.shared_name,
                                           path_l1=path_l1,
                                           path_l2=path_l2,
                                           hash_l1=hash_l1,
                                           hash_l2=hash_l2))

    def as_dict_list(self):

        return {"time" : self._time_last_change,
             "names": [x.shared_name for x in self.questions],
             "paths_l1": [x.path_l1 for x in self.questions],
             "paths_l2" : [x.path_l2 for x in self.questions],
             "hashes_l1": [x.hash_l1 for x in self.questions],
             "hashes_l2": [x.hash_l2 for x in self.questions]
              }

    def save(self, json_filename=None, info=None):
        if json_filename is None:
            if self.json_filename is None:
                raise RuntimeError("Specify json_filename to save exam.")
            else:
                json_filename = self.json_filename

        print("Save {}".format(json_filename))
        if info is not None:
            self.info = info

        d = self.as_dict_list()
        if self.info is not None:
            d["info"] = self.info

        with open(json_filename, 'w', encoding=FILE_ENCODING) as fl:
            fl.write(json.dumps(d, indent = 2))

    def load(self, json_filename):
        self.json_filename = json_filename
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
                                               path_l1=d["paths_l1"][x],
                                               path_l2=d["paths_l2"][x],
                                               hash_l1=d["hashes_l1"][x],
                                               hash_l2=d["hashes_l2"][x]))

    def get_database_ids(self, rm_nones=False):
        """returns ids from item database or the question if not found
        takes into account the hashes!"""

        if self._item_db is None:
            return []

        rtn = []
        for quest in self.questions:
            idx = self._item_db.find(
                hash_l1=quest.hash_l1 ,
                hash_l2=quest.hash_l2,
                shared_name=quest.shared_name,
                relative_path_l1=quest.path_l1,
                relative_path_l2=quest.path_l2,
                find_all=False) # finds just first one

            if idx is not None:
                rtn.append(idx)
            elif not rm_nones:
                rtn.append(None)

        return rtn


    def find_item(self, item):
        """returns question id first occurance if item"""

        if not isinstance(item, EntryItemDatabase):
            return None
        else:
            needle = ExamQuestion.create_from_database_entry(item)
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

    def markdown(self, use_l2=False):
        if self._item_db is None:
            return ""

        old_tag = AnswerList.TAG_CORRECT
        AnswerList.TAG_CORRECT = "* X"
        rtn = ""
        for cnt, db_idx in enumerate(self.get_database_ids(rm_nones=False)):
            if db_idx is not None:
                db_entry = self._item_db.entries[db_idx]
            else:
                db_entry = EntryNotFound(self.questions[cnt])

            if use_l2:
                tmp = db_entry.item_l2
            else:
                tmp = db_entry.item_l1

            q_str = tmp.markdown(enumerator=cnt + 1, wrap_text_width=80)
            rtn += q_str + "\n\n"

        AnswerList.TAG_CORRECT = old_tag

        return rtn.strip()


class EntryNotFound(EntryItemDatabase):

    def __init__(self, exam_question, use_l2=False):
        assert isinstance(exam_question, ExamQuestion)

        l = "-"*79 + "\n"
        tarray = [l, "ERROR: File not found\n", l]
        item_l1 = RExamItem()
        item_l2 = RExamItem()
        if not use_l2:
            item_l1.question.text_array = tarray +\
                                      ["File: {}\n".format(exam_question.path_l1),
                                       "Hash: {}\n".format(exam_question.hash_l1)]
            item_l1.name = exam_question.shared_name
            item_l1.meta_info.name = exam_question.shared_name
        else:
            item_l2.question.text_array = tarray +\
                                      ["File: {}\n".format(exam_question.path_l2),
                                       "Hash: {}\n".format(exam_question.hash_l2)]
            item_l2.name = exam_question.shared_name
            item_l2.meta_info.name = exam_question.shared_name

        super().__init__(shared_name=exam_question.shared_name,
                         item_l1=item_l1, item_l2=item_l2)
