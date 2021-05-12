from collections import OrderedDict

from . import templates, extypes
from .issue import Issue
from ..misc import extract_parameter

class ItemSection(object):

    def __init__(self, parent, label, underline_chr, min_underline_length=4):
        from .rexam_item import RExamItem
        assert(isinstance(parent, (ItemSection, RExamItem)))

        self._parent = parent
        self._underline_chr = underline_chr
        self._underline_string = underline_chr * min_underline_length

        self.label = label
        self.text_array = [] # array of text lines ending with \n (like readlines)
        self.line_range = [None, None]
        self.answer_list = None

    def parse(self):
        # find the section and copy content to object
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
            return rtn

        else:
            return "".join(self.text_array[:max_lines])

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

    def parse(self):
        super().parse()
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
        with open(filename, "r") as fl:
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
        super().__init__(parent, "Meta-information", "=")
        from .rexam_item import RExamItem
        assert(isinstance(self._parent, RExamItem))
        self.parameter = OrderedDict()

    def parse(self, reset_parameter=False):
        super().parse()
        additional_content = []
        if reset_parameter:
            self.parameter = OrderedDict()
        while len(self.text_array)>0:
            l = self.text_array.pop(0)
            para = extract_parameter(l)
            if para is None:
                additional_content.extend(l)
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