from os import path

from . import consts
from .item_sections import ItemSection, ItemMetaInfo
from .files import ShareStatsFile


class ShareStatsItem(object):

    def __init__(self, filename=None):
        if isinstance(filename, ShareStatsFile):
            self.filename = filename
        else:
            self.filename = ShareStatsFile(filename)
        self.question = ItemSection(self, "Question", "=")
        self.solution = ItemSection(self, "Solution", "=")
        self.meta_info = ItemMetaInfo(self)
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

    def parse(self, source_text):
        """parse file or source text is specified"""
        if isinstance(source_text, str):
            self.text_array = list(map(lambda x: x+"\n",
                                       source_text.split("\n")))
                # array of text lines ending with \n (like readlines)
        else:
            self.text_array = source_text
        self.question.parse()
        self.solution.parse()
        self.meta_info.parse()

        # overide answer_list correctness with meta info solution
        self.update_solution(self.meta_info.solution)


    def requires_answer_list(self):

        return self.meta_info.type in consts.HAVE_ANSWER_LIST

    def __str__(self):
        rtn = "".join(self.header)
        rtn += str(self.question) + "\n\n\n" + \
                str(self.solution) + "\n\n\n" + str(self.meta_info)
        return rtn

    def save(self):
        if len(self.filename.full_path):
            self.filename.make_dirs()
            #print("Save {}".format(self.filename.path))
            with open(self.filename.full_path, "w") as fl:
                fl.write(str(self))

    def validate_meta_info(self):
        rtn =""
        issues = 0

        if not self.meta_info.check_type():
            issues += 1
            rtn += "* Unknown/undefined  item type(extype))\n"

        if self.filename.name != self.meta_info.name: #FIXME use good folder
            issues += 1
            rtn += "* Item name (exname) does not match filename\n"

        if self.requires_answer_list():
            if not self.question.has_answer_list_section():
                issues += 1
                rtn += "* no answer list defined\n"
            if not self.solution.has_answer_list_section():
                issues += 1
                rtn += "* no feedback answer list defined\n"
        else:
            if self.question.has_answer_list_section():
                issues += 1
                rtn += "* answer list not required\n" #TODO or even allowed?
            if  self.solution.has_answer_list_section():
                issues += 1
                rtn += "* feedback answer list not required\n"

        if len(rtn):
            rtn = "{} issues found!\n".format(issues) + rtn

        return rtn

    def update_solution(self, solution_str):
        self.meta_info.solution = solution_str
        if self.question.has_answer_list_section():
            self.question.answer_list.solution_str = solution_str

#FIXME: if exsolution is updated in meta info and not save, new taxonimie override exsolution chages
#FIXME exsolution appears in meta info for new item, although not defined

