from os import path, rename
from collections import OrderedDict
import hashlib
from copy import deepcopy
import textwrap

from . import extypes
from .. import templates
from ..consts import FILE_ENCODING
from .rmd_file import RmdFile
from .filepath import FilePath
from .issue import Issue
from ..misc import extract_parameter


class ItemSection(object):

    def __init__(self, parent, label, underline_chr, min_underline_length=4):

        assert (isinstance(parent, (ItemSection, RExamItem)))

        self._parent = parent
        self._underline_chr = underline_chr
        self._underline_string = underline_chr * min_underline_length

        self.label = label
        self.text_array = []  # array of text lines ending with \n (like readlines)
        self.line_range = [None, None]
        self.answer_list = None

    def parse(self, parent=None):
        # find the section and copy content to object
        if parent is not None:
            self._parent = parent
        prev = ""
        is_section = False
        self.text_array = []
        self.line_range = [None, None]
        cnt = None
        for cnt, line in enumerate(self._parent.text_array):
            if not is_section:
                if line.startswith(self._underline_string) and \
                        prev.strip() == self.label:
                    is_section = True
                    self.line_range[0] = cnt - 1
            else:
                if line.startswith(self._underline_string):
                    # end section
                    self.text_array.pop()
                    cnt -= 2
                    break
                else:
                    self.text_array.append(line)
            prev = line

        if self.line_range[0] is not None:
            self.line_range[1] = cnt

        if not isinstance(self, AnswerList):
            answer_list = AnswerList(self)
            answer_list.parse()
            a, b = answer_list.line_range
            if a is not None and b is not None:
                self.text_array = self.text_array[:a] + self.text_array[b + 1:]
                self.answer_list = answer_list
            else:
                self.answer_list = None

    def add_answer_list_section(self):
        if not self.has_answer_list_section():
            self.answer_list = AnswerList(self)

    def has_answer_list_section(self):
        return self.answer_list is not None

    def str_markdown_heading(self):
        return "{}\n{}\n".format(self.label,
                                 str(self._underline_chr * len(self.label)))

    def str_text(self, ignore_empty_lines=False, wrap_text_width=0):
        if ignore_empty_lines:
            tmp = [x for x in self.text_array if len(x.strip())]
        else:
            tmp = self.text_array

        if wrap_text_width > 1:
            rtn = ""
            for x in tmp:
                rtn += textwrap.fill(x, width=wrap_text_width,
                                     replace_whitespace=False) + "\n"
        else:
            rtn = "".join(tmp).rstrip()

        return rtn.rstrip()

    def str_text_short(self, max_lines=2, ignore_empty_lines=True):
        """return x lines for the section and ignores empty lines"""
        if ignore_empty_lines:
            cnt = 0
            rtn = ""
            for x in self.text_array:
                if len(x.strip()):
                    rtn += x
                    cnt += 1
                    if cnt >= max_lines:
                        break
            return rtn.strip()

        else:
            return "".join(self.text_array[:max_lines]).strip()

    def __str__(self):
        # section as string
        rtn = self.str_markdown_heading() + self.str_text()
        if self.answer_list is not None:
            return rtn + "\n\n" + str(self.answer_list)
        else:
            return rtn


class AnswerList(ItemSection):
    TAG_CORRECT = "#"
    TAG_ITEM = "*"

    def __init__(self, parent):
        super().__init__(parent, "Answerlist", "-")
        self.answers = []
        self._correct = []
        self._tab_sep = []  # used tab separator for this item?

    def parse(self, parent=None):
        super().parse(parent=parent)
        self.answers = []
        self._correct = []
        self._tab_sep = []
        unparsed_content = []

        l_tag_item = len(AnswerList.TAG_ITEM) + 1
        l_tag_corr = len(AnswerList.TAG_CORRECT) + 1
        while len(self.text_array) > 0:
            answer = self.text_array.pop(0)
            tag, tab_sep = check_tag(answer, AnswerList.TAG_ITEM, AnswerList.TAG_CORRECT)
            if tab_sep is not None:
                self._tab_sep.append(tab_sep)
            if tag == AnswerList.TAG_ITEM:
                self.answers.append(answer[l_tag_item:].strip())
                self._correct.append(False)
            elif tag == AnswerList.TAG_CORRECT:
                self.answers.append(answer[l_tag_corr:].strip())
                self._correct.append(True)
            else:
                unparsed_content.append(answer)

        self.text_array = unparsed_content

    @staticmethod
    def extract_solution(markdown):
        """extracts solution from markdown string that used TAG_CORRECT"""

        solution = ""
        for l in markdown.split("\n"):
            tag, _ = check_tag(l, AnswerList.TAG_ITEM, AnswerList.TAG_CORRECT)
            if tag == AnswerList.TAG_ITEM:
                solution += "0"
            elif tag == AnswerList.TAG_CORRECT:
                solution += "1"
        return solution

    @property
    def solution_str(self):
        return "".join(map(lambda x: str(int(x)), self._correct))

    @solution_str.setter
    def solution_str(self, value):
        self._correct = []
        for cnt, ans in enumerate(self.answers):
            try:
                self._correct.append(value[cnt] == "1")
            except:
                self._correct.append(False)

    def str_answers(self, tag_mark_correct=False, highlight_correct_before_after=""):
        """mark_correct add chars before and after correct e.g. '**' for markdown bold"""
        rtn = ""
        for ans, correct, tab_sep in zip(self.answers, self._correct, self._tab_sep):
            if tag_mark_correct and correct:
                tag = AnswerList.TAG_CORRECT
            else:
                tag = AnswerList.TAG_ITEM

            if correct:
                mark = highlight_correct_before_after
            else:
                mark = ""

            if tab_sep:
                rtn += "{}\t{}{}{}\n".format(tag, mark, ans, mark)
            else:
                rtn += "{} {}{}{}\n".format(tag, mark, ans, mark)

        return rtn

    def __str__(self):
        rtn = self.str_markdown_heading() + self.str_answers() + self.str_text()
        return rtn.strip()

    def fix_tabs(self):
        if True in self._tab_sep:
            self._tab_sep = [False] * len(self._tab_sep)

    def validate(self):
        issues = []
        if True in self._tab_sep:
            issues.append(Issue("tabs_in_answerlist",
                                "Tabs used as separator in Answerlist",
                                self.fix_tabs))
        return issues


class ItemMetaInfo(ItemSection):
    _REQUIRED_PARAMETER = None

    def __init__(self, parent):
        assert (isinstance(parent, RExamItem))
        super().__init__(parent, "Meta-information", "=")
        self.parameter = OrderedDict()

    @classmethod
    def required_parameter(cls):
        if cls._REQUIRED_PARAMETER is None:
            # try to load it once from templates
            rtn = {}
            for k, filename in templates.FILES.items():
                meta_info = False
                rtn[k] = OrderedDict()
                with open(filename, "r", encoding=FILE_ENCODING) as fl:
                    for l in fl:
                        if l.startswith("Meta-information"):
                            meta_info = True
                        elif meta_info:
                            para = extract_parameter(l)
                            if para is not None:
                                rtn[k].update(para)

            cls._REQUIRED_PARAMETER = rtn

        return cls._REQUIRED_PARAMETER

    def parse(self, parent=None, reset_parameter=False):
        super().parse(parent=parent)
        additional_content = []
        if reset_parameter:
            self.parameter = OrderedDict()
        while len(self.text_array) > 0:
            l = self.text_array.pop(0)
            para = extract_parameter(l)
            if para is None:
                additional_content.append(l)
            else:
                self.parameter.update(para)
        self.text_array = additional_content

    def str_parameter(self):
        rtn = ""
        for k, v in self.parameter.items():
            rtn += "{}: {}\n".format(k, v)
        return rtn

    def __str__(self):
        rtn = self.str_markdown_heading() + self.str_parameter() + "\n" \
              + self.str_text()
        return rtn.strip()

    def _try_parameter(self, label):
        try:
            return self.parameter[label]
        except:
            return ""

    def sort_parameter(self):
        # sorting parameter based on Templates (in place)
        required = ItemMetaInfo.required_parameter()
        try:
            req_para = required[self.type].keys()
        except:
            return False

        new_para = OrderedDict()
        for k in req_para:
            if k in self.parameter:
                new_para[k] = self.parameter.pop(k)
        new_para.update(self.parameter)
        self.parameter = new_para

    @property
    def name(self):
        return self._try_parameter("exname")

    @name.setter
    def name(self, v):
        self.parameter["exname"] = v

    @property
    def section(self):
        return self._try_parameter("exsection")

    @section.setter
    def section(self, v):
        self.parameter["exsection"] = v

    @property
    def type(self):
        return self._try_parameter("extype")

    @type.setter
    def type(self, v):
        self.parameter["extype"] = v

    @property
    def solution(self):
        return self._try_parameter("exsolution")

    @solution.setter
    def solution(self, v):
        self.parameter["exsolution"] = v

    def check_type(self):
        """:returns True if known type
        """

        return self.type in extypes.EXTYPES.keys()

    def requires_answer_list(self):
        return self.type in extypes.HAVE_ANSWER_LIST

    def get_missing_parameter(self):
        required = ItemMetaInfo.required_parameter()
        try:
            parameter = required[self.type]
        except:
            return {}

        return {k: v for k, v in parameter.items() if k not in self.parameter}

    def fix_missing_parameter(self):
        for k, v in self.get_missing_parameter().items():
            self.parameter[k] = v

    def validate(self):
        issues = []

        # is type defined type
        if not self.check_type():
            issues.append(Issue("extype",
                                "Unknown/undefined item type(extype))", None))

        # missing parameter
        missing_parameter = self.get_missing_parameter()
        if len(missing_parameter):
            issues.append(Issue("missings", "Missing required meta-information: {}".format(
                list(missing_parameter.keys())),
                                self.fix_missing_parameter))

        return issues


class RExamItem(RmdFile):
    META_INFO_CLASS = ItemMetaInfo

    def __init__(self, file_path=None):
        assert isinstance(file_path, FilePath) or file_path is None
        if file_path is not None:
            super().__init__(file_path=file_path.relative_path,
                             base_directory=file_path.base_directory)
        else:
            super().__init__(file_path)
        self.question = ItemSection(self, "Question", "=")
        self.solution = ItemSection(self, "Solution", "=")
        self.meta_info = RExamItem.META_INFO_CLASS(self)

        self.header = []
        self.text_array = []
        self._hash = None

        if path.isfile(self.full_path):
            self.import_file(self.full_path)

    def hash(self):
        """question id is based on the file content"""

        if self._hash is None:
            txt = "".join(self.text_array)
            self._hash = hashlib.sha1(txt.encode()).hexdigest()  # calc only once

        return self._hash

    def hash_short(self):
        return self.hash()[:7]

    def import_file(self, text_file):
        """import a text file as content"""
        self.header = []
        self.text_array = []
        with open(text_file, "r", encoding=FILE_ENCODING) as fl:
            self.parse(fl.readlines())

    def parse(self, source_text, reset_meta_information=False):
        """parse file or source text is specified"""
        if isinstance(source_text, str):
            self.text_array = list(map(lambda x: x + "\n",
                                       source_text.split("\n")))
            # array of text lines ending with \n (like readlines)
        else:
            self.text_array = source_text

        self.question.parse(parent=self)
        self.solution.parse(parent=self)
        self.meta_info.parse(parent=self,
                             reset_parameter=reset_meta_information)

        self.header = deepcopy(self.text_array[:self.question.line_range[0]])
        # override answer_list correctness with meta info solution
        self.update_solution(self.meta_info.solution)

    def __str__(self):
        rtn = "".join(self.header)
        rtn += str(self.question) + "\n\n\n" + \
               str(self.solution) + "\n\n\n" + str(self.meta_info)
        return rtn

    def save(self):
        if len(self.full_path):
            self.make_dirs()
            with open(self.full_path, "w", encoding=FILE_ENCODING) as fl:
                fl.write(str(self))

    def fix_add_answer_list(self):
        self.question.add_answer_list_section()

    def fix_directory_name(self):
        self.save()
        rename(self.directory, path.join(self.base_directory, self.name))

    def fix_uppercases_in_relative_path(self):
        self.save()
        old = self.full_path
        self.name = self.name.lower()
        rename(old, self.full_path)
        self.fix_directory_name()

    def validate(self):
        """Validates the item and returns a list of issues"""

        issues = self.meta_info.validate()
        if self.question.has_answer_list_section():
            issues.extend(self.question.answer_list.validate())

        # check answer & feedback list
        if self.meta_info.requires_answer_list():
            if not self.question.has_answer_list_section():
                issues.append(Issue("answers", "No answer list defined",
                                    self.fix_add_answer_list))
        else:
            if self.question.has_answer_list_section():
                issues.append(Issue("answers", "Answer list not required"))

        return issues

    def update_solution(self, solution_str):
        if len(solution_str) == 0 and len(self.meta_info.solution) == 0:
            # don't write solution nothing changed (avoid creating of solution
            # is solution_str is empty and parameter is not yet defined)
            return
        self.meta_info.solution = solution_str
        self.meta_info.sort_parameter()
        if self.question.has_answer_list_section():
            self.question.answer_list.solution_str = solution_str

    @staticmethod
    def load(file_path, base_directory):
        if file_path is None:
            return None
        else:
            return RExamItem(RmdFile(file_path,
                                     base_directory=base_directory))

    def markdown(self, enumerator=None, wrap_text_width=0, tag_mark_correct=True, highlight_correct_char=""):
        '''optional counter to enumerate questions'''
        question_str = self.question.str_text(ignore_empty_lines=False,
                                              wrap_text_width=wrap_text_width)

        if self.question.answer_list is not None:
            question_str += "\n\n" + \
                            self.question.answer_list.str_answers(
                                tag_mark_correct=tag_mark_correct,
                                highlight_correct_before_after=highlight_correct_char)

        if len(question_str.strip()):
            rtn = "# Question "
            if enumerator is not None:
                rtn += "{} ".format(enumerator)
            rtn += "({})\n\n{}".format(self.name, question_str)
            return rtn
        else:
            return ""


def check_tag(textline, tag1, tag2):
    """ helper function
    return (found tag[or None], is tab-separated)
    """
    l = textline.strip()
    if l.startswith(tag1 + " "):
        return tag1, False
    elif l.startswith(tag2 + " "):
        return tag2, False
    if l.startswith(tag1 + "\t"):
        return tag1, True  # item, using tab
    elif l.startswith(tag2 + "\t"):
        return tag2, True  # correct, using tab
    else:
        return None, None
