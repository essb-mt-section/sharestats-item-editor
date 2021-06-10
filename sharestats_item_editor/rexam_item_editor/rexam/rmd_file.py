from os import path, makedirs
from copy import deepcopy
from ..misc import os_rename, copytree

SEP = "-"
NL = "nl"
ENG = "en"

TAG_NL = SEP + NL
TAG_ENG = SEP + ENG
TAG_BILINGUAL = "{}[{}/{}]".format(SEP, NL, ENG)


class RmdFile(object):

    SUFFIX = ".Rmd"

    def __init__(self, file_path):
        if file_path is None:
            file_path=""
        self.directory, self.filename = path.split(file_path)
        #TODO base directory is assumed to be at second level.
        # define base directory explicitily

    def __eq__(self, other):
        try:
            return self.full_path == other.full_path
        except:
            return False

    @staticmethod
    def make_path(base_directory, name):
        # includes name also subdir
        return path.join(base_directory, name, "{}{}".format(name,
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

    @property
    def base_directory(self):
        return path.split(self.directory)[0]

    @property
    def name(self):
        return path.splitext(self.filename)[0]

    @name.setter
    def name(self, value):
        # changes name (and keeps extension)
        ext = path.splitext(self.filename)[1]
        self.filename = value + ext

    @property
    def full_path(self):
        return path.join(self.directory, self.filename)

    @property
    def relative_path(self):
        """path relative to base director"""
        return path.join(path.split(self.directory)[1],
                         self.filename)

    def make_dirs(self):
        try:
            makedirs(self.directory)
        except:
            pass

    def folder_mirrors_filename(self):
        return self.name == path.split(self.directory)[1]

    def get_mirroring_dir_name(self, add_directory_level=False):
        # changes name of sub folder
        if add_directory_level:
            return path.join(self.directory, self.name)
        else:
            d = path.split(self.directory)
            return path.join(d[0], self.name)

    def get_other_language_path(self):
        if len(self.language_code):
            name = self.name[:-2]
            if self.language_code == NL:
                name += ENG
            else:
                name += NL
            return self.make_path(self.base_directory, name)
        else:
            return None

    def rename(self, new_name, rename_dir = True, rename_on_disk=False):
        """Returns io error, if it occurs"""
        new = deepcopy(self)
        new.name = new_name
        if rename_dir:
            new_dir = new.get_mirroring_dir_name()
        else:
            new_dir = None

        if rename_on_disk:
            io_error = os_rename(self.full_path, new.full_path)
            if io_error:
                return "Can't rename directory: {}".format(io_error)
            elif new_dir is not None:
                io_error = os_rename(self.directory, new_dir)
                if io_error:
                    return "Can't rename directory: {}".format(io_error)

        self.filename = new.filename
        if new_dir:
            self.directory = new_dir

    def copy_files(self, new_name):
        """Returns io error, if it occurs other the new RmdFile object"""
        new = deepcopy(self)
        new.name = new_name
        new.directory = new.get_mirroring_dir_name()

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