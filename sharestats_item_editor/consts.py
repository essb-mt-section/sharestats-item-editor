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

COLOR_BKG_INACTIVE = "#8A8A8A"
COLOR_BKG_ACTIVE = "#FFFFFF"
COLOR_BKG_ACTIVE_INFO = "#f6f6f6"
COLOR_BKG_TAX_LIST = COLOR_BKG_ACTIVE_INFO
COLOR_QUEST = "#BBBBDD"
COLOR_SOLUTION = "#BBDDBB"
COLOR_RED_BTN = ("#000000", "#DDBBBB")
SG_COLOR_THEME = {'BACKGROUND': '#E0E0E2',
                  'TEXT': '#000000',
                  'INPUT': COLOR_BKG_ACTIVE_INFO,
                  'TEXT_INPUT': '#000000',
                  'SCROLL': '#99CC99',
                  'BUTTON': ('#000000', '#d4d7dd'),
                  'PROGRESS': ('#D1826B', '#CC8019'),
                  'BORDER': 1, 'SLIDER_DEPTH': 0,
                  'PROGRESS_DEPTH': 0, }

MAX_RECENT_DIRS = 5
