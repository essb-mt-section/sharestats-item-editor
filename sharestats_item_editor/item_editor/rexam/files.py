from os import path, makedirs
from copy import deepcopy
from ..misc import os_rename, copytree

TAG_NL = "-nl"
TAG_ENG = "-en"
TAG_BILINGUAL = "-[nl/en]"

class RmdFilename(object):

    CASE_SENSITIVE_NAMING = False
    RMDFILE_SUFFIX = ".Rmd"

    def __init__(self, file_path):
        if file_path is None:
            file_path=""
        self.directory, self.filename = path.split(file_path)

    def __eq__(self, other):
        try:
            if RmdFilename.CASE_SENSITIVE_NAMING:
                return self.full_path == other.full_path
            else:
                return self.full_path.lower() == other.full_path.lower()
        except:
            return False

    @staticmethod
    def make_path(base_directory, name):
        # includes name also subdir
        return path.join(base_directory, name, "{}.Rmd".format(name))

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
        if RmdFilename.CASE_SENSITIVE_NAMING:
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
            if self.language_code == "nl":
                name += "en"
            else:
                name += "nl"
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

class BilingualRmdFiles(object):
    """representation of two RMD Files"""

    def __init__(self, filename_item, filename_translation=None):

        if filename_item is None and filename_translation is not None:
            filename_translation, filename_item = \
                filename_item, filename_translation  # swap

        if isinstance(filename_item, RmdFilename):
            a = filename_item
        else:
            a = RmdFilename(filename_item)

        if filename_translation is not None:
            if isinstance(filename_translation, RmdFilename):
                b = filename_translation
            else:
                b = RmdFilename(filename_translation)
            if b.language_code == "nl":  # NL is reference language
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
