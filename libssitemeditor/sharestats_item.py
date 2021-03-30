from os import path

from .item_sections import ItemSection, ItemMetaInfo
from .files import ShareStatsFilename


class ShareStatsItem(object):

    def __init__(self, filename=None):
        if isinstance(filename, ShareStatsFilename):
            self.filename = filename
        else:
            self.filename = ShareStatsFilename(filename)
        self.question = ItemSection(self, "Question", "=", has_answer_list=True)
        self.solution = ItemSection(self, "Solution", "=", has_answer_list=True)
        self.meta_info = ItemMetaInfo(self)
        self.header = []
        self.text_array = []

        if path.isfile(self.filename.path):
            self.import_file(self.filename.path)

    def import_file(self, text_file):
        """import a text file as content"""

        self.header = []
        with open(text_file, "r") as fl:
            self.text_array = fl.readlines()
        self.parse()

    def parse(self):
        self.question.parse()
        self.solution.parse()
        self.meta_info.parse()
        self.header = self.text_array[:self.question.line_range[0]]

    def __str__(self):
        rtn = "".join(self.header)
        rtn += str(self.question) + str(self.solution) + str(self.meta_info)
        return rtn

    def save(self):
        if len(self.filename.path):
            self.filename.make_dirs()
            with open(self.filename.path, "w") as fl:
                fl.writelines(str(self))


