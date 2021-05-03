import os
from os import path
from copy import deepcopy
from .. import misc

TAG_NL = "-nl"
TAG_ENG = "-en"
TAG_BILINGUAL = "-[nl/en]"

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

    @property
    def language_code(self):
        if self.name[-3] == "-":
            lang = self.name[-2:].lower()
            if lang in ("nl", "en"):
                return lang
        return ""

    @language_code.setter
    def language_code(self, v):
        assert(isinstance(v, str) and len(v)==2)
        if self.name[-3] == "-":
            self.name = self.name[-2] + v
        else:
            self.name = self.name + "-" + v

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

    def folder_mirrors_filename(self):
        return self.name == path.split(self.directory)[1]

    def get_mirroring_folder_name(self, add_directory_level=False):
        # changes name of sub folder
        if add_directory_level:
            return path.join(self.directory, self.name)
        else:
            d = path.split(self.directory)
            return path.join(d[0], self.name)

    def get_other_language_path(self):
        if len(self.language_code):
            name = self.name[:-2]
            if self.language_code == "nl":
                name += "en"
            else:
                name += "nl"
            return self.make_path(self.base_directory, name)
        else:
            return None

def get_rmd_files_second_level(folder, suffix=".Rmd"):
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
            first = RmdFile(lst.pop(0))
            second = RmdFile(first.get_other_language_path())

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

