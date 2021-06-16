from os import path
from copy import deepcopy
import shutil
from .filepath import FilePath, os_rename

SEP = "-"
CODE_L1 = "nl"
CODE_L2 = "en"

TAG_L1 = SEP + CODE_L1
TAG_L2 = SEP + CODE_L2
TAG_BILINGUAL = "{}[{}/{}]".format(SEP, CODE_L1, CODE_L2)

def copytree(source_folder, destination_folder):
    """copies a folder and return error if it occurs"""
    try:
        shutil.copytree(source_folder, destination_folder)
    except IOError as io_error:
        return io_error


class RmdFile(FilePath):

    SUFFIX = ".Rmd"

    @staticmethod
    def make_path(base_directory, name, add_subdir=True):
        if add_subdir:
            return path.join(base_directory, name, "{}{}".format(name,
                                            RmdFile.SUFFIX))
        else:
            return path.join(base_directory, "{}{}".format(name,
                                                           RmdFile.SUFFIX))

    @property
    def language_code(self):
        if len(self.name)>=4 and self.name[-3] == SEP:
            lang = self.name[-2:].lower()
            if lang in (CODE_L1, CODE_L2):
                return lang
        return ""

    @language_code.setter
    def language_code(self, v):
        assert(isinstance(v, str) and len(v)==2)
        if self.name[-3] == SEP:
            self.name = self.name[-2] + v
        else:
            self.name = self.name + SEP + v

    def subdir_mirrors_filename(self):
        return self.name == self.sub_directory

    def get_other_language_rmdfile(self):
        if len(self.language_code):
            name = self.name[:-2]
            if self.language_code == CODE_L1:
                name += CODE_L2
            else:
                name += CODE_L1

            rtn = deepcopy(self)
            rtn.name = name
            if len(self.sub_directory):
                rtn.sub_directory = name
            return rtn
        else:
            return None

    def copy_subdir_files(self, new_name):
        """Returns io error, if it occurs other the new RmdFile object"""
        new = deepcopy(self)
        new.name = new_name
        new.sub_directory = new_name

        #copy fiels
        ioerror = copytree(self.directory, new.directory)
        if ioerror:
            return ioerror
        else:
            copied_rmd = deepcopy(new)
            copied_rmd.name = self.name # has still old name
            ioerror = os_rename(copied_rmd.full_path, new.full_path)
            if ioerror:
                return ioerror

        return new

class BiLingualRmdFilePair(object):
    """Two RMD Files, reference language and translation
    """

    def __init__(self, rmd_file_item, rmd_file_translation=None,
                        reference_language_code=None):
        """if reference language_code is defined, items that does not have
        this reference code will be stored as rmd_translation """

        x = []
        for rmd in (rmd_file_item, rmd_file_translation):
            if rmd is None:
                x.append(None)
            else:
                if isinstance(rmd, RmdFile):
                    x.append(rmd)
                else:
                    x.append(RmdFile(rmd))

        if (x[0] is None and x[1] is not None):
            x = x[1], x[0]

        elif x[1] is not None:
            # --> two languages: swap, if x[1] is NL
            if reference_language_code is not None and \
                    x[1].language_code == reference_language_code:
                x = x[1], x[0]

        self._item = x[0]
        self._translation = x[1]

    def __str__(self):
        if self._item is None:
            i = "None"
        else:
            i = self._item.relative_path
        if self._translation is None:
            t = "None"
        else:
            t = self._translation.relative_path

        return "{}: ({}, {})".format(self.shared_name(), i, t)

    @property
    def rmd_item(self):
        return self._item

    @property
    def rmd_translation(self):
        return self._translation

    def shared_name(self, add_bilingual_tag=True, lower_case=True):

        if self._item is not None and self._translation is None:
            return self._item.name.lower()
        elif self._item is None and self._translation is not None:
            return self._translation.name.lower()
        elif self._item is None and self._translation is None:
            return None
        else:
            # is bilingual
            name = self._item.name.lower()
            if name.endswith(TAG_L1) or \
                    name.endswith(TAG_L2):
                name = name[:-3]
            if add_bilingual_tag:
                name = name + TAG_BILINGUAL
            return name

    def is_bilingual(self):
        return self._translation is not None and self._item is not None
