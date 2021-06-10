from os import path
from copy import deepcopy
import shutil
from .filepath import FilePath, os_rename

SEP = "-"
NL = "nl"
ENG = "en"

TAG_NL = SEP + NL
TAG_ENG = SEP + ENG
TAG_BILINGUAL = "{}[{}/{}]".format(SEP, NL, ENG)

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
            if lang in (NL, ENG):
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
            if self.language_code == NL:
                name += ENG
            else:
                name += NL

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