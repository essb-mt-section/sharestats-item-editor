import os
from os import path
from .. import misc

from .rexam_item import RmdFilename, RExamItem

TAG_NL = "-nl"
TAG_ENG = "-en"
TAG_BILINGUAL = "-[nl/en]"

def get_rmd_files_second_level(folder,
                               suffix=RmdFilename.RMDFILE_SUFFIX):
    """returns list with Rmd files at the second levels that has the same
    name as the folder. Otherwise first rexam found is return."""

    lst = []
    for name in os.listdir(folder):
        fld = path.join(folder, name)
        if path.isdir(fld):
            good_fl_name = path.join(fld, name+suffix)
            if path.isfile(good_fl_name):
                lst.append(good_fl_name)
            else:
                # search for rexam file
                try:
                    subdir_lst = os.listdir(fld)
                except:
                    subdir_lst=[] # no permission to access dir
                for fl_name in map(lambda x: path.join(fld, x), subdir_lst):
                    # no permission
                    if fl_name.lower().endswith(suffix.lower()):
                        # best guess
                        lst.append(fl_name)
                        break

    return lst


class FileListBilingual(object):

    def __init__(self, folder=None):
        self.files = []
        if folder is None:
            return

        self.folder = folder
        # check for matching languages
        lst = get_rmd_files_second_level(folder)
        self._file_list_hash = hash(tuple(lst))

        while len(lst) > 0:
            first = RmdFilename(lst.pop(0))
            second = RmdFilename(first.get_other_language_path())

            if second.full_path in lst:
                lst = misc.remove_all(lst, second.full_path,
                                      ignore_cases=True)  # remove all
                # instance of second in lst
                if second.language_code == "nl":
                    second, first = first, second  # swap
            else:
                second = None
            self.files.append((first, second))

        self.files = sorted(self.files,
                             key=FileListBilingual.shared_name)


    def get_count(self):

        rtn = {"total": len(self.files),
                "nl": 0, "en": 0,
                "bilingual": 0,
                "undef": 0}
        for a, b in self.files:
            if b is not None:
                rtn["bilingual"] += 1
            if a.language_code == "en":
                rtn["en"] += 1
            elif a.language_code == "nl":
                rtn["nl"] += 1
            else:
                rtn["undef"] += 1

        return rtn

    @staticmethod
    def shared_name(bilingual_file_names, add_bilingual_tag=True):
        """bilingual_file_list_entry: tuple of two entries"""

        name = bilingual_file_names[0].name
        if len(name):
            if bilingual_file_names[1] is not None:
                if name.endswith(TAG_NL) or \
                        name.endswith(TAG_ENG):
                    name = name[:-3]
                if add_bilingual_tag:
                    name = name + TAG_BILINGUAL
            return name

        else:
            return bilingual_file_names[0].filename

    def file_list_changed(self):
        lst = get_rmd_files_second_level(self.folder)
        return hash(tuple(lst)) != self._file_list_hash

    def get_shared_names(self, bilingual_tag=True):
        return [FileListBilingual.shared_name(x, bilingual_tag)
                    for x in self.files]

    def find_shared_name(self, name):
        tmp = self.get_shared_names(bilingual_tag=False)
        try:
            return tmp.index(name)
        except:
            return None

    def find_filename(self, fl_name, second_language=False):
        """find idx by file name of first or second language"""

        item = int(second_language)
        tmp = [x[item].filename==fl_name for x in self.files]
        try:
            return tmp.index(True)
        except:
            return None

    def is_bilingual(self, idx):
        try:
            return None not in self.files[idx]
        except:
            return None

    def load_rexam_files(self, idx):
        """returns tuple of RExam files or None if file does not exist."""

        try:
            fls = self.files[idx]
        except:
            return None, None

        if fls[0] is not None:
            a = RExamItem(fls[0])
        else:
            a = None

        if fls[1] is not None:
            b = RExamItem(fls[1])
        else:
            b = None

        return a, b

    def iter_rexam_files(self):
        return map(self.load_rexam_files, range(len(self.files)))


class ItemDatabase(object):

    def __init__(self, file_list_bilingual):
        assert isinstance(file_list_bilingual, FileListBilingual)
        self.file_list = file_list_bilingual
        self.data = []
        self._idx = []
        cnt = 0
        for rexam_fls, name in zip(self.file_list.iter_rexam_files(),
                    self.file_list.get_shared_names(bilingual_tag=False)):
            self.data.append([cnt, name, rexam_fls[0], rexam_fls[1]])
            cnt += 1

        self.reset_search()

    def reset_search(self):
        """similar to select all"""
        self._idx = range(len(self.data))

    @property
    def selected_rows(self):
        """selected rows"""
        return [x for x in self.data if x[0] in self._idx]

    def _find_idx(self, search_function):
        """searches rexam file using search_function and returns idx,
        if found for one of the laguages"""
        idx = []
        for x in self.selected_rows:
            try:
                found = search_function(x[2])
            except:
                found = -1

            if found<0:
                try:
                    found = search_function(x[3])
                except:
                    found = -1

            if found>=0:
                idx.append(x[0])

        return idx

    def search_name(self, text):
        self._idx = self._find_idx(lambda x: x.filename.name.find(text))

    def search_question(self, text):
        self._idx = self._find_idx(lambda x: x.question.str_text.find(text))

    def search_meta_info(self, text):
        self._idx = self._find_idx(lambda x: x.meta_info.str_text.find(text))

    def search_solution(self, text):
        self._idx = self._find_idx(lambda x: x.solution.str_text.find(text))

    def search_raw_rmd(self, text):
        self._idx = self._find_idx(lambda x: str(x).find(text))

    def get_question_overview(self, max_lines=3):
        """returns table with cnt, name, short question a, short question b"""
        rtn = []
        for r in self.selected_rows:
            try:
                a_txt = r[2].question.str_text_short(max_lines)
            except:
                a_txt = ""
            try:
                b_txt = r[3].question.str_text_short(max_lines)
            except:
                b_txt = ""

            rtn.append([r[0], r[1], a_txt, b_txt])

        return rtn