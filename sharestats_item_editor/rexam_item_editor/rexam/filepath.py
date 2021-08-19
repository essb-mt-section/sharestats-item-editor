from os import path, makedirs, rename
from copy import deepcopy

def os_rename(source, destination):
    """rename file or folder and return error if it occurs"""
    try:
        return rename(source, destination)
    except IOError as io_error:
        return io_error

class FilePath(object):

    def __init__(self, file_path, base_directory = None):
        """Class handling filename and relative file locations

        Base_directory, sub_directory (relative to base) and filename

        if base directory is None,  base_directory assumed to be at first
        level and subdir at second level

        otherwise: file_path is relative to base directory
        """

        if file_path is None or file_path == "":
            self.filename = ""
            self.sub_directory = ""
            if base_directory is None:
                self.base_directory = ""
            else:
                self.base_directory = base_directory

        elif base_directory is None:
            directory, self.filename = path.split(path.abspath(file_path))
            self.base_directory, self.sub_directory = path.split(directory)
            if len(self.base_directory)==0:
                self.sub_directory, self.base_directory = \
                                    self.base_directory, self.sub_directory

        else:
            self.base_directory = path.abspath(base_directory)
            abs_file_path = path.abspath(file_path)
            if abs_file_path.startswith(self.base_directory):
                # abs_file_path is subpart of base directory
                rel_file_path = path.relpath(abs_file_path,
                                             start= self.base_directory)
            else:
                # abs_file_path is not subpart of base directory,
                # it's thus relative to base_directory
                rel_file_path = file_path

                if file_path == abs_file_path:
                    # it's abs_solute path (but not part of base_directory)
                    # base_direct does not make sense
                    self.base_directory = ""

            self.sub_directory, self.filename = path.split(rel_file_path)

    def __eq__(self, other):
        try:
            return self.full_path == other.full_path
        except:
            return False

    def __str__(self):
        return self.full_path

    @property
    def name(self):
        # without file extension
        return path.splitext(self.filename)[0]

    @name.setter
    def name(self, value):
        # changes name (and keeps extension)
        ext = path.splitext(self.filename)[1]
        self.filename = value + ext

    @property
    def full_path(self):
        return path.join(self.base_directory, self.sub_directory, self.filename)

    @property
    def directory(self):
        return path.join(self.base_directory, self.sub_directory)

    @property
    def relative_path(self):
        """path relative to base director"""
        return path.join(self.sub_directory, self.filename)

    def make_dirs(self):
        try:
            makedirs(self.directory)
        except:
            pass

    def rename(self, new_name, new_sub_dir = None, rename_on_disk=False):
        """Returns io error, if it occurs"""
        new = deepcopy(self)
        new.name = new_name
        if new_sub_dir is not None:
            new.sub_directory = new_sub_dir

        if rename_on_disk:
            if new_sub_dir is not None:
                io_error = os_rename(self.directory, new.directory)
                if io_error:
                    return "Can't rename directory: {}".format(io_error)

            io_error = os_rename(path.join(new.directory, self.filename),
                                 new.full_path)
            if io_error:
                return "Can't rename file: {}".format(io_error)

        self.filename = new.filename
        self.sub_directory = new.sub_directory
