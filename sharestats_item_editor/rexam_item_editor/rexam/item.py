from os import path, rename
from collections import OrderedDict
import hashlib
from copy import deepcopy

from . import templates, extypes
from .rmd_file import RmdFile
from .issue import Issue
from ..misc import extract_parameter

FILE_ENCODING = 'utf-8'

class ItemSection(object):

    def __init__(self, parent, label, underline_chr, min_underline_length=4):

        assert(isinstance(parent, (ItemSection, RExamItem)))

        self._parent = parent
        self._underline_chr = underline_chr
        self._underline_string = underline_chr * min_underline_length

        self.label = label
        self.text_array = [] # array of text lines ending with \n (like readlines)
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
                    self.line_range[0] = cnt-1
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

    @property
    def str_markdown_heading(self):
        return "{}\n{}\n".format(self.label,
                                 str(self._underline_chr * len(self.label)))

    @property
    def str_text(self):
        return "".join(self.text_array).rstrip()

    def str_text_short(self, max_lines=2, ignore_empty_lines=True):
        """return x lines for the section and ignores empty lines"""
        if ignore_empty_lines:
            cnt = 0
            rtn = ""
            for x in self.text_array:
                x = x.strip()
                if len(x):
                    rtn += x + "\n"
                    cnt += 1
                    if cnt >= max_lines:
                        break
            return rtn.strip()

        else:
            return "".join(self.text_array[:max_lines]).strip()

    def __str__(self):
        # section as string
        rtn = self.str_markdown_heading + self.str_text
        if self.answer_list is not None:
            return rtn + "\n\n" + str(self.answer_list)
        else:
            return rtn


class AnswerList(ItemSection):

    TAG_CORRECT = "# "
    TAG_ITEM = "* "

    def __init__(self, parent):
        super().__init__(parent, "Answerlist", "-")
        self.answers = []
        self._correct = []

    def parse(self, parent=None):
        super().parse(parent=parent)
        self.answers = []
        self._correct = []
        unparsed_content = []
        while len(self.text_array)>0:
            answer = self.text_array.pop(0)
            if answer.strip().startswith(AnswerList.TAG_ITEM):
                self.answers.append(answer[2:].strip())
                self._correct.append(False)
            elif answer.strip().startswith(AnswerList.TAG_CORRECT):
                self.answers.append(answer[2:].strip())
                self._correct.append(True)
            else:
                unparsed_content.append(answer)

        self.text_array = unparsed_content

    @staticmethod
    def extract_solution(markdown):
        """extracts solution from markdown string that used TAG_CORRECT"""

        solution = ""
        for l in markdown.split("\n"):
            if l.startswith(AnswerList.TAG_ITEM):
                solution += "0"
            elif l.startswith(AnswerList.TAG_CORRECT):
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

    @property
    def str_answers(self):
        return self.get_str_answers_marked(mark_correct_solutions=False)

    def get_str_answers_marked(self, mark_correct_solutions=True):
        rtn = ""
        for ans, correct in zip(self.answers, self._correct):
            if mark_correct_solutions and correct:
                tag = AnswerList.TAG_CORRECT
            else:
                tag = AnswerList.TAG_ITEM
            rtn += "{}{}\n".format(tag, ans)

        return rtn

    def __str__(self):
        rtn =  self.str_markdown_heading + self.str_answers + self.str_text
        return rtn.strip()


def _get_required_parameter_from_templates():
    rtn ={}
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
    return rtn


class ItemMetaInfo(ItemSection):

    REQUIRED_PARAMETER = _get_required_parameter_from_templates()

    def __init__(self, parent):
        assert(isinstance(parent, RExamItem))
        super().__init__(parent, "Meta-information", "=")
        self.parameter = OrderedDict()

    def parse(self, parent=None, reset_parameter=False):
        super().parse(parent=parent)
        additional_content = []
        if reset_parameter:
            self.parameter = OrderedDict()
        while len(self.text_array)>0:
            l = self.text_array.pop(0)
            para = extract_parameter(l)
            if para is None:
                additional_content.append(l)
            else:
                self.parameter.update(para)
        self.text_array = additional_content

    @property
    def str_parameter(self):
        rtn = ""
        for k, v in self.parameter.items():
            rtn += "{}: {}\n".format(k, v)
        return rtn

    def __str__(self):
        rtn = self.str_markdown_heading + self.str_parameter + "\n" \
             + self.str_text
        return rtn.strip()

    def _try_parameter(self, label):
        try:
            return self.parameter[label]
        except:
            return ""

    def sort_parameter(self):
        # sorting parameter based on Templates (in place)
        try:
            req_para = ItemMetaInfo.REQUIRED_PARAMETER[self.type].keys()
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
        try:
            parameter = ItemMetaInfo.REQUIRED_PARAMETER[self.type]
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
        assert isinstance(file_path, str) or file_path is None
        super().__init__(file_path)
        self.question = ItemSection(self, "Question", "=")
        self.solution = ItemSection(self, "Solution", "=")
        self.meta_info = RExamItem.META_INFO_CLASS(self)

        self.header = []
        self.text_array = []
        self._version_id = None

        if path.isfile(self.full_path):
            self.import_file(self.full_path)

    @property
    def version_id(self):
        """question id is based on the filename and file folder"""

        if self._version_id is None:
            txt = str(self.question) + str(self.solution) + str(self.meta_info)
            self._version_id = hashlib.md5(txt.encode()).hexdigest()

        return self._version_id


    def import_file(self, text_file):
        """import a text file as content"""
        self.header = []
        self.text_array = []
        with open(text_file, "r", encoding=FILE_ENCODING) as fl:
            self.parse(fl.readlines())

    def parse(self, source_text, reset_meta_information=False):
        """parse file or source text is specified"""
        if isinstance(source_text, str):
            self.text_array = list(map(lambda x: x+"\n",
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
        rename(self.directory, self.get_mirroring_dir_name())

    def fix_uppercases_in_relative_path(self):
        self.save()
        old = self.full_path
        self.name = self.name.lower()
        rename(old, self.full_path)
        self.fix_directory_name()


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

    @staticmethod
    def load(file_path):
        if file_path is None:
            return None
        else:
            return RExamItem(file_path)