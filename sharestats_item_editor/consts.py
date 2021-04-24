import sys as _sys

APPNAME = "ShareStats Item Editor"
PYTHON_VERSION = "{0}.{1}.{2}".format(_sys.version_info[0],
                                      _sys.version_info[1],
                                      _sys.version_info[2])


UNKNOWN_TYPE = "unknown"
EXTYPES = {"schoice": "Multiple choice",
           "mchoice": "Multiple answer",
           "num": "Fill in the blank numbers",
           "string": "Fill in the blank text/essay",
           "cloze": "Combinations"}

HAVE_ANSWER_LIST = ["schoice", "mchoice", "cloze"]

TAG_NL = "-nl"
TAG_ENG = "-en"
TAG_BILINGUAL = "-[nl/en]"

COLOR_THEME = 'SystemDefault1'
COLOR_BKG_INACTIVE = "#8A8A8A"
COLOR_BKG_ACTIVE = "#FFFFFF"
COLOR_BKG_ACTIVE_INFO = "#EEEEEE"
COLOR_BKG_TAX_LIST = "#E0E0D0"
COLOR_QUEST = "#BBBBDD"
COLOR_SOLUTION = "#BBDDBB"
COLOR_META_INFO = "#DDBBBB"
COLOR_RED_BTN = ("black", COLOR_META_INFO)

MAX_RECENT_DIRS = 5
