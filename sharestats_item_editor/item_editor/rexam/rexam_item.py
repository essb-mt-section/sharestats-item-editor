import hashlib
from os import path, rename, makedirs
import shutil
from copy import deepcopy

from .item_sections import ItemSection, ItemMetaInfo
from .issue import Issue

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


def os_rename(source, destination):
    """rename file or folder and return error if it occurs"""
    try:
        return rename(source, destination)
    except IOError as io_error:
        return io_error

def copytree(source_folder, destination_folder):
    """copies a folder and return error if it occurs"""
    try:
        shutil.copytree(source_folder, destination_folder)
    except IOError as io_error:
        return io_error


class RExamItem(object):

    META_INFO_CLASS = ItemMetaInfo

    def __init__(self, filename=None):
        if isinstance(filename, RmdFilename):
            self.filename = filename
        else:
            self.filename = RmdFilename(filename)
        self.question = ItemSection(self, "Question", "=")
        self.solution = ItemSection(self, "Solution", "=")
        self.meta_info = RExamItem.META_INFO_CLASS(self)

        self.header = []
        self.text_array = []

        if path.isfile(self.filename.full_path):
            self.import_file(self.filename.full_path)

    def import_file(self, text_file):
        """import a text file as content"""
        self.header = []
        self.text_array = []
        with open(text_file, "r") as fl:
            self.parse(fl.readlines())

    def parse(self, source_text, reset_meta_information=False):
        """parse file or source text is specified"""
        if isinstance(source_text, str):
            self.text_array = list(map(lambda x: x+"\n",
                                       source_text.split("\n")))
                # array of text lines ending with \n (like readlines)
        else:
            self.text_array = source_text
        self.question.parse()
        self.solution.parse()
        self.meta_info.parse(reset_parameter=reset_meta_information)

        self.header = deepcopy(self.text_array[:self.question.line_range[0]])
        # override answer_list correctness with meta info solution
        self.update_solution(self.meta_info.solution)

    def __str__(self):
        rtn = "".join(self.header)
        rtn += str(self.question) + "\n\n\n" + \
                str(self.solution) + "\n\n\n" + str(self.meta_info)
        return rtn

    def save(self):
        if len(self.filename.full_path):
            self.filename.make_dirs()
            #print("Save {}".format(self.filename.full_path))
            with open(self.filename.full_path, "w") as fl:
                fl.write(str(self))

    def fix_add_answer_list(self):
        self.question.add_answer_list_section()

    def fix_directory_name(self):
        self.save()
        rename(self.filename.directory, self.filename.get_mirroring_dir_name())

    def validate(self):
        """Validates the item and returns a list of issues"""
        issues = self.meta_info.validate()

        # check answer & feedback list
        if self.meta_info.requires_answer_list():
            if not self.question.has_answer_list_section():
                issues.append(Issue("answers", "No answer list defined",
                                    self.fix_add_answer_list))
            if not self.solution.has_answer_list_section():
                issues.append(Issue("feedback",
                                    "No feedback answer list defined"))
        else:
            if self.question.has_answer_list_section():
                issues.append(Issue("answers", "Answer list not required"))
            if  self.solution.has_answer_list_section():
                issues.append(Issue("feedback",
                                    "Feedback answer list not required"))

        return issues

    def update_solution(self, solution_str):
        if len(solution_str) == 0 and len(self.meta_info.solution)==0:
            #don't write solution nothing changed (avoid creating of solution
            # is solution_str is empty and parameter is not yet defined)
            return
        self.meta_info.solution = solution_str
        self.meta_info.sort_parameter()
        if self.question.has_answer_list_section():
            self.question.answer_list.solution_str = solution_str

    def version_id(self):
        """question id is based on the filename and file folder"""
        txt = str(self.question) + str(self.solution) + str(self.meta_info)
        return hashlib.md5(txt.encode()).hexdigest()





