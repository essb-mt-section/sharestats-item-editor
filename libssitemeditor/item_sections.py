from collections import OrderedDict
from . import consts


class ItemSection(object):

    def __init__(self, parent, tag, underline_chr, min_underline_length=4,
                 has_answer_list=False):
        from .sharestats_item import ShareStatsItem
        assert(isinstance(parent, (ItemSection, ShareStatsItem)))

        self._parent = parent
        self._underline_chr = underline_chr
        self._underline_string = underline_chr * min_underline_length

        self.tag = tag
        self.text_array = []
        self.line_range = [None, None]
        if has_answer_list:
            self.answer_list = AnswerList(self)
        else:
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
                        prev.strip() == self.tag:
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

        self.line_range[1] = cnt

        if self.answer_list is not None:
            self.answer_list.parse()
            a, b = self.answer_list.line_range
            if a is not None and b is not None:
                self.text_array = self.text_array[:a] + self.text_array[b + 1:]

    @property
    def str_markdown_heading(self):
        return "{}\n{}\n".format(self.tag,
                                 str(self._underline_chr * len(self.tag)))

    @property
    def str_text(self):
        return "".join(self.text_array)

    def __str__(self):
        # section as string
        rtn = self.str_markdown_heading + self.str_text
        if self.answer_list is not None:
            return rtn + str(self.answer_list)
        else:
            return rtn



class AnswerList(ItemSection):

    def __init__(self, parent):
        super().__init__(parent, "Answerlist", "-")
        self.answers = []
        self.correct = []

    def parse(self):
        super().parse()
        self.answers = []
        additional_content = []
        while len(self.text_array)>0:
            answer = self.text_array.pop(0)
            if answer.strip().startswith("* "):
                self.answers.append(answer.strip()[2:])
            else:
                additional_content.append(answer)
        self.correct = [False] * len(self.answers) # default all are wrong
        self.text_array = additional_content

    @property
    def str_answers(self):
        rtn = ""
        for ans in self.answers:
            rtn += "* {}\n".format(ans)
        return rtn

    def get_exsolution(self):
        return "".join(map(lambda x: str(int(x)), self.correct))

    def __str__(self):
        return self.str_markdown_heading + self.str_answers + self.str_text


class ItemMetaInfo(ItemSection):

    def __init__(self, parent):
        super().__init__(parent, "Meta-information", "=")
        from .sharestats_item import ShareStatsItem
        assert(isinstance(self._parent, ShareStatsItem))
        self.parameter = OrderedDict()


    def parse(self):
        super().parse()

        additional_content = []
        while len(self.text_array)>0:
            para = self.text_array.pop(0).split(":", maxsplit=1)
            if len(para)<2:
                additional_content.extend(para)
            else:
                self.parameter[para[0].strip()] = para[1].strip()
        self.text_array = additional_content

    @property
    def str_parameter(self):
        rtn = ""
        for k, v in self.parameter.items():
            rtn += "{}: {}\n".format(k, v)
        return rtn

    def __str__(self):
        return self.str_markdown_heading + self.str_parameter + self.str_text

    def _try_parameter(self, label):
        try:
            return self.parameter[label]
        except:
            return ""


    def check_name(self):
        """:returns tuple(good type [boolen], the type)
        """
        p = self.parameter["exname"]
        return p == self._parent.filename.stats_share_name, p

    @property
    def name(self):
       return self._try_parameter("exname")

    @name.setter
    def name(self, v):
        self.parameter["exname"] = v

    @property
    def taxonomy(self):
        return self._try_parameter("exsection")

    @taxonomy.setter
    def taxonomy(self, v):
        self.parameter["exsection"] = v

    @property
    def type(self):
        return self._try_parameter("exextra[Type]")

    @type.setter
    def type(self, v):
        self.parameter["exextra[Type]"] = v

    @property
    def program(self):
        return self._try_parameter("exextra[Program]")

    @program.setter
    def program(self, v):
        self.parameter["exextra[Program]"] = v

    @property
    def language(self):
        return self._try_parameter("exextra[Language]")

    @language.setter
    def language(self, v):
        self.parameter["exextra[Language]"] = v

    @property
    def level(self):
        return self._try_parameter("exextra[Level]")

    @level.setter
    def level(self, v):
        self.parameter["exextra[Level]"] = v


    def check_type(self):
        """:returns tuple(good type [boolen], the type)
        """

        try:
            t = self.parameter["extype"]
        except:
            return (False, "")

        return t in consts.EXTYPES.keys(), t

