from os import path

from .item_sections import ItemSection, ItemMetaInfo
from .files import ShareStatsFilename


class ShareStatsItem(object):

    def __init__(self, filename=None):
        if isinstance(filename, ShareStatsFilename):
            self.filename = filename
        else:
            self.filename = ShareStatsFilename(filename)
        self.question = ItemSection(self, "Question", "=")
        self.solution = ItemSection(self, "Solution", "=")
        self.meta_info = ItemMetaInfo(self)
        self.header = []
        self.text_array = []

        if path.isfile(self.filename.path):
            self.import_file(self.filename.path)

    def import_file(self, text_file):
        """import a text file as content"""

        self.header = []
        self.text_array = []
        with open(text_file, "r") as fl:
            self.parse(fl.readlines())

    def parse(self, source_text):
        """parse file or source text is specified"""
        if isinstance(source_text, str):
            self.text_array = source_text.split("\n")
        else:
            self.text_array = source_text
        self.question.parse()
        self.solution.parse()
        self.meta_info.parse()


    def __str__(self):
        rtn = "".join(self.header)
        rtn += str(self.question) + "\n\n\n" + \
                str(self.solution) + "\n\n\n" + str(self.meta_info)
        return rtn

    def save(self):
        if len(self.filename.path):
            self.filename.make_dirs()
            #print("Save {}".format(self.filename.path))
            with open(self.filename.path, "w") as fl:
                fl.writelines(str(self))

    def validate_meta_info(self):
        rtn =""
        if self.filename.stats_share_name != self.meta_info.name:
            rtn += "* Exname does not match filename."

        #if self.meta_info. TODo

        return rtn


