import os
from os import path
from .. import misc

from .rexam_item import RmdFilename, RExamItem

TAG_NL = "-nl"
TAG_ENG = "-en"
TAG_BILINGUAL = "-[nl/en]"

def _get_rmd_files_second_level(folder,
                                suffix=RmdFilename.RMDFILE_SUFFIX):
    """returns list with Rmd files at the second levels that has the same
    name as the folder. Otherwise first rexam found is return."""

    if folder is None:
        return []
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


class BilingualRmdFiles(object):
    """representation of two RMD Files"""
    
    def __init__(self, filename_item, filename_translation=None):

        if filename_item is None and filename_translation is not None:
            filename_translation, filename_item = \
                                filename_item, filename_translation # swap

        if isinstance(filename_item, RmdFilename):
            a = filename_item
        else:
            a = RmdFilename(filename_item)

        if filename_translation is not None:
            if isinstance(filename_translation, RmdFilename):
                b = filename_translation
            else:
                b = RmdFilename(filename_translation)
            if b.language_code == "nl": # NL is reference language
                b, a = a, b
        else:
            b = None

        self._item = a
        self._translation = b

    @property
    def filename_item(self):
        return self._item

    @property
    def filename_translation(self):
        return self._translation

    def shared_name(self, add_bilingual_tag=True):
        """bilingual_file_list_entry: tuple of two entries"""

        name = self._item.name
        if len(name):
            if self._translation is not None:
                if name.endswith(TAG_NL) or \
                        name.endswith(TAG_ENG):
                    name = name[:-3]
                if add_bilingual_tag:
                    name = name + TAG_BILINGUAL
            return name

        else:
            return self._item.filename

    def is_bilingual(self):
        return self._translation is not None and self._item is not None

    def load_item(self):
        if self._item is None:
            return None
        else:
            return RExamItem(self._item)

    def load_translation(self):
        if self._translation is None:
            return None
        else:
            return RExamItem(self._translation)


class BilingualFileList(object):

    def __init__(self, folder=None):
        self.files = []
        self.folder = folder
        # check for matching languages
        lst = _get_rmd_files_second_level(folder)
        self._file_list_hash = hash(tuple(lst))

        while len(lst) > 0:
            first = RmdFilename(lst.pop(0))
            second = RmdFilename(first.get_other_language_path())
            if second.full_path in lst:
                lst = misc.remove_all(lst, second.full_path,
                                      ignore_cases=True)  # remove all
            else:
                second = None

            self.files.append(BilingualRmdFiles(filename_item=first,
                                                filename_translation=second))

        self.files = sorted(self.files, key=lambda x:x.shared_name())

    def get_count(self):

        rtn = {"total": len(self.files),
                "nl": 0, "en": 0,
                "bilingual": 0,
                "undef": 0}
        for f in self.files:
            if f.is_bilingual():
                rtn["bilingual"] += 1
            elif f.filename_item.language_code == "en":
                rtn["en"] += 1
            elif f.filename_item.language_code == "nl":
                rtn["nl"] += 1
            else:
                rtn["undef"] += 1

        return rtn

    def is_file_list_changed(self):
        lst = _get_rmd_files_second_level(self.folder)
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
            if fl.filename_item.filename == fl_name or \
                    (fl.filename_translation is not None and
                     fl.filename_translation.filename == fl_name):
                return cnt

        return None

    def load_rexam_files(self, idx):
        """returns tuple of RExam files or None if file does not exist."""
        try:
            fls = self.files[idx]
        except:
            return None, None

        return fls.load_item(), fls.load_translation()