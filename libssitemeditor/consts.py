from os  import path as _path

APPNAME = "ShareStats Item Editor"
_LIB_DIR = _path.dirname(__file__)

UNKNOWN_TYPE = "unknown"
EXTYPES = {"schoice": "Multiple choice",
           "mchoice": "Multiple answer",
           "num": "Fill in the blank numbers",
           "string": "Fill in the blank text/essay",
           "cloze": "Combinations"}

HAVE_ANSWER_LIST = ["schoice", "mchoice", "cloze"]

TEMPLATES = {"schoice":
                 _path.join(_LIB_DIR, "templates/TemplateMultipleChoice.Rmd"),
           "mchoice":
                 _path.join(_LIB_DIR, "templates/TemplateMultipleAnswer.Rmd"),
           "num":
                 _path.join(_LIB_DIR, "templates/TemplateBlankNumber.Rmd"),
           "string":
                 _path.join(_LIB_DIR, "templates/TemplateBlankTextEssay.Rmd"),
           "cloze":
                 _path.join(_LIB_DIR, "templates/TemplateBlankCombination.Rmd")}

COLOR_BKG_INACTIVE = "#8A8A8A"
COLOR_BKG_ACTIVE = "#FFFFFF"
COLOR_QUEST = "#BBBBDD"
COLOR_SOLUTION = "#BBDDBB"
COLOR_MATA_INFO = "#DDBBBB"


