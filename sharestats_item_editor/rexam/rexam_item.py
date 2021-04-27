from os import path, rename
from copy import copy

from .item_sections import ItemSection, ItemMetaInfo
from .files import RmdFile
from .issue import Issue

class RExamItem(object):

    META_INFO_CLASS = ItemMetaInfo

    def __init__(self, filename=None, meta_info_class=None):
        if isinstance(filename, RmdFile):
            self.filename = filename
        else:
            self.filename = RmdFile(filename)
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

        self.header = copy(self.text_array[:self.question.line_range[0]])
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
        new = self.filename.copy()
        new.set_mirroring_folder_name()
        rename(self.filename.directory, new.directory)

    def validate(self):
        """Validates the item and returns a list of issues"""
        issues = self.meta_info.validate()

        # check answer & feedback list
        if self.meta_info.requires_answer_list():
            if not self.question.has_answer_list_section():
                issues.append(Issue("No answer list defined",
                                    self.fix_add_answer_list))
            if not self.solution.has_answer_list_section():
                issues.append(Issue("No feedback answer list defined"))
        else:
            if self.question.has_answer_list_section():
                issues.append(Issue("Answer list not required")) #TODO or even allowed?
            if  self.solution.has_answer_list_section():
                issues.append(Issue("Feedback answer list not required")) #TODO or even allowed?

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





