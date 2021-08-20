from multiprocessing import Pool

from .rmd_file_list import BiLingRmdFileList, BiLingualRmdFilePair
from .item import RExamItem
from ..misc import iter_list


class _SearchSchemata(object):

    def __init__(self):
        self.search_types = []
        self.parameter = []
        self.functions = []

    def add(self, search_type, parameter):
        """para: search_type has to be 'name', 'question', 'solution',
        'meta_info' or 'raw_rmd'
        if parameter is iterable (but not a string), it will be multiple
        functions with different parameter.
        """

        if not isinstance(parameter, str) and hasattr(parameter, "__iter__"):
            for p in parameter:
                self._add(search_type, p)
        else:
            self._add(search_type, parameter)

    def _add(self, search_type, parameter):
        if search_type == "name":
            f = lambda x: x.name.find(parameter)
        elif search_type == "question":
            f = lambda x: x.question.str_text().find(parameter)
        elif search_type == "solution":
            f = lambda x: x.solution.str_text().find(parameter)
        elif search_type == "meta_info":
            f = lambda x: x.meta_info.str_text().find(parameter)
        elif search_type == "raw_rmd":
            f = lambda x: str(x).find(parameter)
        else:
            raise RuntimeError("{} is an unknown SearchFunction "
                               "type.".format(search_type))

        self.functions.append(f)
        self.parameter.append(parameter)
        self.search_types.append(search_type)


class EntryItemDatabase(object):
    # biligual RExamItem

    def __init__(self, shared_name, item_l1, item_l2):
        assert isinstance(item_l1, RExamItem) or item_l1 is None
        assert isinstance(item_l2, RExamItem) or item_l2 is None
        self.shared_name = shared_name
        self.item_l1 = item_l1
        self.item_l2 = item_l2
        self.id = None

    def is_same_as(self, item):
        """compares shared names and version id
        and ignores the id"""

        if isinstance(item, EntryItemDatabase):
            return self.shared_name == item.shared_name and \
                   self.hash_l1() == item.hash_l1() and \
                   self.hash_l2() == item.hash_l2()
        else:
            return False

    def hash_l1(self):
        try:
            return self.item_l1.hash()
        except:
            return ""

    def hash_l2(self):
        try:
            return self.item_l2.hash()
        except:
            return ""

    def hash_l1_short(self):
        try:
            return self.item_l1.hash_short()
        except:
            return ""

    def hash_l2_short(self):
        try:
            return self.item_l2.hash_short()
        except:
            return ""

    def short_repr(self, max_lines, use_l2, add_versions=False, short_version=True):
        if use_l2:
            try:
                txt = self.item_l2.question.str_text_short(max_lines, ignore_empty_lines=True)
            except:
                txt = ""
        else:
            try:
                txt = self.item_l1.question.str_text_short(max_lines, ignore_empty_lines=True)
            except:
                txt = ""

        rtn = [self.shared_name, txt]
        if add_versions:
            if short_version:
                if use_l2:
                    rtn.append(self.hash_l2_short())
                else:
                    rtn.append(self.hash_l1_short())
            else:
                if use_l2:
                    rtn.append(self.hash_l2())
                else:
                    rtn.append(self.hash_l1())
        return rtn

    @staticmethod
    def load(biling_filelist_entry, shared_name_with_bilingual_tag=False):
        assert isinstance(biling_filelist_entry, BiLingualRmdFilePair)

        if biling_filelist_entry.rmdfile_l1 is not None:
            l1 = RExamItem(biling_filelist_entry.rmdfile_l1)
        else:
            l1 = None

        if biling_filelist_entry.rmdfile_l2 is not None:
            l2 = RExamItem(biling_filelist_entry.rmdfile_l2)
        else:
            l2 = None

        return EntryItemDatabase(
                shared_name=biling_filelist_entry.shared_name(
                                    add_bilingual_tag=shared_name_with_bilingual_tag),
                item_l1=l1,
                item_l2=l2)


class ItemDatabase(BiLingRmdFileList):

    def __init__(self, base_directory, files_first_level,
                            files_second_level,
                            check_for_bilingual_files):
        """file_list_bilingual: path or file_list_biligual
        """
        super().__init__(base_directory=base_directory,
                         files_first_level=files_first_level,
                         files_second_level=files_second_level,
                         check_for_bilingual_files=check_for_bilingual_files)
        self._selected_ids = []

        ## LOAD DATA
        if len(self.files) > 1000:
            # speed up with multiprocessing
            entries = Pool().map(EntryItemDatabase.load, self.files)
        else:
            entries = map(EntryItemDatabase.load, self.files)
        self.entries = list(entries)

        # add unique ids
        for x in range(len(self.entries)):
            self.entries[x].id = x

        self.select() # select all

    def get_entries(self, ids, rm_nones=True):
        """returns subset of DatabaseEntries items """
        rtn = []
        for i in ids:
            try:
                rtn.append(self.entries[i])
            except:
                if not rm_nones:
                    rtn.append(None)
        return rtn

    @property
    def selected_entries(self):
        """selected name, l1, l2, l1_hash,
                    l2_hash"""
        return self.get_entries(self._selected_ids, rm_nones=True)

    def _search_select(self, search_function, item_ids_subset):
        """searches rexam file using search_function and returns idx,
        if found for at least one of the language.
        Use item_ids_subset (array if ids) to define the the  subset of
        items, in which you want to serach """

        idx = []
        for x in item_ids_subset:

            try:
                found = search_function(self.entries[x].item_l1)
            except:
                found = -1

            if found<0:
                try:
                    found = search_function(self.entries[x].item_l2)
                except:
                    found = -1

            if found>=0:
                idx.append(x)

        return idx

    def select(self, name=None, question=None, solution=None,
                     meta_information=None, raw_rmd=None,
                     search_logic_or=False):
        """select items based on text search"""

        # select all
        self._selected_ids = range(len(self.entries))
        search = _SearchSchemata()
        search.add("name", iter_list(name))
        search.add("question", iter_list(question))
        search.add("solution", iter_list(solution))
        search.add("meta_info", iter_list(meta_information))
        search.add("raw_rmd", iter_list(raw_rmd))

        if search_logic_or:
            # OR
            idx = []
            for fnc in search.functions:
                for x in self._search_select(fnc, item_ids_subset=self._selected_ids):
                    if x not in idx:
                        idx.append(x)
            self._selected_ids = sorted(idx)
        else:
            # AND
            for fnc in search.functions:
                self._selected_ids = self._search_select(fnc, item_ids_subset=self._selected_ids)

        return self._selected_ids

    def find_entry(self, entry_item_database):
        """returns all id of identical entries """

        same = filter(lambda x:x.is_same_as(entry_item_database), self.entries)
        rtn = map(lambda x: x.id, same)
        return list(rtn)

    def find(self, hash_l1,
             hash_l2=None,
             relative_path_l1 = None,
             relative_path_l2=None,
             shared_name = None,
             find_all=False):

        """advanced search function
        returns on first id  or array with all is (find_all=True)
        the found entries
        """

        rtn = []
        for cnt, e in enumerate(self.entries):
            a = shared_name is None or e.shared_name == shared_name
            b = relative_path_l1 is None or (e.item_l1 is not None and
                                             e.item_l1.relative_path == relative_path_l1)
            c = relative_path_l2 is None or \
                (e.item_l2 is not None and \
                 e.item_l2.relative_path == relative_path_l2)

            if  a and b and c:
                if  e.hash_l1() == hash_l1 and \
                    (hash_l2 is None or
                     e.hash_l2() == hash_l2):
                    if find_all:
                        rtn.append(cnt)
                    else:
                        return cnt

        if not find_all:
            return None
        else:
            return rtn
