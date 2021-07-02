import os
from os import path
from .. import misc
from multiprocessing import Pool

from .rmd_file import RmdFile, BiLingualRmdFilePair, CODE_L1, CODE_L2
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
            f = lambda x: x.question.str_text.find(parameter)
        elif search_type == "solution":
            f = lambda x: x.solution.str_text.find(parameter)
        elif search_type == "meta_info":
            f = lambda x: x.meta_info.str_text.find(parameter)
        elif search_type == "raw_rmd":
            f = lambda x: str(x).find(parameter)
        else:
            raise RuntimeError("{} is an unknown SearchFunction "
                               "type.".format(search_type))

        self.functions.append(f)
        self.parameter.append(parameter)
        self.search_types.append(search_type)

class ItemFileList(object):

    Entry = BiLingualRmdFilePair

    def __init__(self, folder=None, files_first_level=True,
                                    files_second_level=True,
                                    check_for_bilingual_files=True):
        self.files = []
        self.base_directory = folder
        self.files_first_level = files_first_level
        self.files_second_level = files_second_level

        # check for matching languages
        lst = misc.CaseInsensitiveStringList(self.get_rmd_files())

        self._file_list_hash = hash(tuple(lst.get())) # simple hashes for online
        # change detection, this are not the version IDs!

        if check_for_bilingual_files:
            reference_language = CODE_L1
        else:
            reference_language = None
        second = None
        while len(lst) > 0:
            first = RmdFile(file_path=lst.pop(0),
                            base_directory=self.base_directory)

            if check_for_bilingual_files:
                second = first.get_other_language_rmdfile()

            if second is not None and second.full_path in lst:
                # get in correct cases
                second_full_cases = lst.remove(second.full_path)
                lst.remove_all(second_full_cases) # remove all others versions (should not be the case)
                second = RmdFile(file_path=second_full_cases,
                                 base_directory=self.base_directory)
            else:
                second = None

            self.files.append(ItemFileList.Entry(rmd_file_item=first,
                                 rmd_file_translation=second,
                                 reference_language_code=reference_language))

        self.files = sorted(self.files, key=lambda x:x.shared_name())

    def get_count(self):

        rtn = {"total": len(self.files),
                CODE_L1: 0,
                CODE_L2: 0,
                "bilingual": 0,
                "undef": 0}

        for f in self.files:
            if f.is_bilingual():
                rtn["bilingual"] += 1
            else:
                try:
                    lang = f.rmd_item.language_code
                except:
                    lang = None
                try:
                    rtn[lang] += 1
                except:
                    rtn["undef"] += 1

        return rtn

    def is_file_list_changed(self):
        lst = self.get_rmd_files()
        return hash(tuple(lst)) != self._file_list_hash

    def get_shared_names(self, bilingual_tag=True):
        return [x.shared_name(bilingual_tag) for x in self.files]

    def find_shared_name(self, name):
        tmp = self.get_shared_names(bilingual_tag=False)
        try:
            return tmp.index(name)
        except:
            return None

    def find_filename(self, fl_name):
        """find idx by file name of first or second language"""

        for cnt, fl in enumerate(self.files):
            if fl.rmd_item.filename == fl_name or \
                    (fl.rmd_translation is not None and
                     fl.rmd_translation.filename == fl_name):
                return cnt

        return None

    def get_rmd_files(self, suffix=RmdFile.SUFFIX):
        """returns list with Rmd files at the second levels and/or first
        level (depending on files_first_level and files_second_level).

         Second level files: The file with the same name as the folder;
         otherwise first rexam found is this subfolder return.

         returns absolute pathes """

        if self.base_directory is None:
            return []
        lst = []
        for name in os.listdir(self.base_directory):
            fld = path.join(self.base_directory, name)
            if path.isdir(fld) and self.files_second_level:
                good_fl_name = path.join(fld, name + suffix)
                if path.isfile(good_fl_name):
                    lst.append(good_fl_name)
                else:
                    # search for a rexam file in the subdirectory
                    try:
                        subdir_lst = os.listdir(fld)
                    except:
                        subdir_lst = []  # no permission to access dir
                    for fl_name in map(lambda x: path.join(fld, x), subdir_lst):
                        # no permission
                        if fl_name.lower().endswith(suffix.lower()):
                            # best guess
                            lst.append(fl_name)
                            break

            elif path.isfile(fld) and self.files_first_level:
                if fld.lower().endswith(suffix.lower()):
                    lst.append(fld)

        return [path.abspath(x) for x in lst]


class EntryItemDatabase(object):

    def __init__(self, shared_name, item, translation):
        assert isinstance(item, RExamItem) or item is None
        assert isinstance(translation, RExamItem) or translation is None
        self.shared_name = shared_name
        self.item = item
        self.translation = translation
        self.id = None

    def is_same_as(self, item):
        """compares shared names and version id
        and ignores the id"""

        if isinstance(item, ItemDatabase.Entry):
            return self.shared_name == item.shared_name and\
                self.version_item == item.version_item and \
                self.version_translation == item.version_translation
        else:
            return False

    @property
    def version_item(self):
        try:
            return self.item.version_id
        except:
            return ""

    @property
    def version_translation(self):
        try:
            return self.translation.version_id
        except:
            return ""

    @property
    def version_item_short(self):
        return self.version_translation[:7]

    @property
    def version_translation_short(self):
        return self.version_item[:7]

    def short_repr(self, max_lines, add_versions=False, short_version=True):
        try:
            a_txt = self.item.question.str_text_short(max_lines)
        except:
            a_txt = ""
        try:
            b_txt = self.translation.question.str_text_short(max_lines)
        except:
            b_txt = ""

        rtn = [self.shared_name, a_txt, b_txt]
        if add_versions:
            if short_version:
                rtn.extend([self.version_item_short,
                            self.version_translation_short])
            else:
                rtn.extend([self.version_item, self.version_translation])
        return rtn

    @staticmethod
    def load(biling_filelist_entry, shared_name_with_bilingual_tag=False):
        assert isinstance(biling_filelist_entry, BiLingualRmdFilePair)

        if biling_filelist_entry.rmd_item is not None:
            item = RExamItem(biling_filelist_entry.rmd_item)
        else:
            item = None

        if biling_filelist_entry.rmd_translation is not None:
            translation = RExamItem(biling_filelist_entry.rmd_translation)
        else:
            translation = None

        return ItemDatabase.Entry(
                shared_name=biling_filelist_entry.shared_name(
                                    add_bilingual_tag=shared_name_with_bilingual_tag),
                item=item,
                translation=translation)


class ItemDatabase(ItemFileList):

    Entry = EntryItemDatabase

    def __init__(self, folder, files_first_level,
                            files_second_level,
                            check_for_bilingual_files):
        """file_list_bilingual: path or file_list_biligual
        """
        super().__init__(folder=folder,
                         files_first_level=files_first_level,
                         files_second_level=files_second_level,
                         check_for_bilingual_files=check_for_bilingual_files)
        self._selected_ids = []

        ## LOAD DATA
        if len(self.files) > 1000:
            # speed up with multiprocessing
            entries = Pool().map(ItemDatabase.Entry.load, self.files)
        else:
            entries = map(ItemDatabase.Entry.load, self.files)
        self.entries = list(entries)

        # add unique ids
        for x in range(len(self.entries)):
            self.entries[x].id = x

        self.select() # select all

    def get_entries(self, ids, rm_nones=True):
        """returns subset of Rexam items """
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
        """selected name, item, translation, item_version,
                    translation_version"""
        return self.get_entries(self._selected_ids)

    def _search_select(self, search_function, item_ids_subset):
        """searches rexam file using search_function and returns idx,
        if found for at least one of the language.
        Use item_ids_subset (array if ids) to define the the  subset of
        items, in which you want to serach """

        idx = []
        for x in item_ids_subset:

            try:
                found = search_function(self.entries[x].item)
            except:
                found = -1

            if found<0:
                try:
                    found = search_function(self.entries[x].translation)
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


    def find(self, item_version_id,
             translation_version_id=None,
             item_relative_path = None,
             translation_relative_path=None,
             shared_name = None,
             find_all=False):

        """advanced search function
        returns on first id  or array with all is (find_all=True)
         the found entries
         """

        rtn = []
        for cnt, e in enumerate(self.entries):
            a = shared_name is None or e.shared_name == shared_name
            b = item_relative_path is None or (e.item is not None and
                                e.item.relative_path == item_relative_path)
            c = translation_relative_path is None or \
                (e.translation is not None and \
                 e.translation.relative_path ==translation_relative_path)

            if  a and b and c:
                if  e.version_item == item_version_id and \
                    (translation_version_id is None or
                         e.version_translation== translation_version_id):
                    if find_all:
                        rtn.append(cnt)
                    else:
                        return cnt

        if not find_all:
            return None
        else:
            return rtn