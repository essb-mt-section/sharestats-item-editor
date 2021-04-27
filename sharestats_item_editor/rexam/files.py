import os
from os import path
from copy import deepcopy
from .. import consts, misc

class RmdFile(object):

    CASE_SENSITIVE_NAMING = False

    def __init__(self, file_path):
        if file_path is None:
            file_path=""
        self.directory, self.filename = path.split(file_path)

    def __eq__(self, other):
        try:
            if RmdFile.CASE_SENSITIVE_NAMING:
                return self.full_path == other.full_path
            else:
                return self.full_path.lower() == other.full_path.lower()
        except:
            return False

    def __str__(self):
        return str(self.full_path)

    @staticmethod
    def make_path(base_directory, name):
        # includes name also subdir
        return path.join(base_directory, name, "{}.Rmd".format(name))

    def copy(self):
        return deepcopy(self)

    def get_language(self):
        if len(self.name) >= 3 and self.name[-3] == "-":
            lang = self.name[-2:].lower()
            if lang in ("nl", "en"):
                return lang
        return ""

    @property
    def base_directory(self):
        return path.split(self.directory)[0]

    @property
    def name(self):
        if RmdFile.CASE_SENSITIVE_NAMING:
            return path.splitext(self.filename)[0]
        else:
            return path.splitext(self.filename)[0].lower()

    @name.setter
    def name(self, value):
        # changes name (and keeps extension)
        ext = path.splitext(self.filename)[1]
        self.filename = value + ext

    @property
    def full_path(self):
        return path.join(self.directory, self.filename)

    def make_dirs(self):
        try:
            os.makedirs(self.directory)
        except:
            pass

    def is_good_directory_name(self):
        if RmdFile.CASE_SENSITIVE_NAMING:
            return self.name == path.split(self.directory)[1]
        else:
            return self.name == path.split(self.directory)[1].lower()

    def fix_directory_name(self, add_directory_level=False):
        # changes name of sub folder
        if add_directory_level:
            self.directory = path.join(self.directory, self.name)
        else:
            d = path.split(self.directory)
            self.directory = path.join(d[0], self.name)

        return self.directory

    def get_other_language_path(self):
        lang = self.get_language()
        if len(lang):
            name = self.name[:-2]
            if lang == "nl":
                name += "en"
            else:
                name += "nl"
            return self.make_path(self.base_directory, name)
        else:
            return None


class FileListBilingual(object):

    def __init__(self, folder=None):
        self.files = []
        if folder is None:
            return

        # check for matching languages
        lst = FileListBilingual._get_rmd_files_second_level(folder)
        while len(lst) > 0:
            first = RmdFile(lst.pop(0))
            second = RmdFile(first.get_other_language_path())

            if second is not None:
                lst = misc.remove_all(lst, second.full_path, ignore_cases=True)  # remove all instance of second in lst
                if path.isfile(second.full_path):
                    if second.get_language() == "nl":
                        second, first = first, second  # swap
                else:
                    second = None

            self.files.append((first, second))

        self.files = sorted(self.files,
                             key=FileListBilingual.shared_name)

    @staticmethod
    def shared_name(bilingual_file_names, add_bilingual_tag=True):
        """bilingual_file_list_entry: tuple of two entries"""

        name = bilingual_file_names[0].name
        if len(name):
            if bilingual_file_names[1] is not None:
                if name.endswith(consts.TAG_NL) or \
                        name.endswith(consts.TAG_ENG):
                    name = name[:-3]
                if add_bilingual_tag:
                    name = name + consts.TAG_BILINGUAL
            return name

        else:
            return bilingual_file_names[0].filename

    def get_shared_names(self, bilingual_tag=True):
        return [FileListBilingual.shared_name(x, bilingual_tag)
                    for x in self.files]

    @staticmethod
    def _get_rmd_files_second_level(folder, suffix=".Rmd"):
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
                        subdir_lst=[] # no permission to acces dir
                    for fl_name in map(lambda x: path.join(fld, x), subdir_lst):
                        # not permission
                        if fl_name.lower().endswith(suffix.lower()):
                            # best guess
                            lst.append(fl_name)
                            break

        return sorted(lst)

    def find_filename(self, fl_name):
        # find filename in first item of bilingual file list
        tmp = [x[0].filename==fl_name for x in self.files]
        try:
            return tmp.index(True)
        except:
            return None

    def is_bilingual(self, idx):
        try:
            return None not in self.files[idx]
        except:
            return None
