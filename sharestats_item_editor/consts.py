import sys as _sys

APPNAME = "Item Editor"

PYTHON_VERSION = "{0}.{1}.{2}".format(_sys.version_info[0],
                                      _sys.version_info[1],
                                      _sys.version_info[2])

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


WIDTH_ML = 80 # multi line field for text input
LEN_ML_SMALL = 6
LEN_ML_LARGE = 15 # tab layout
LEN_ANSWER_SMALL = 5
LEN_ANSWER_LARGE = 8
TAB_LAYOUT = True

MAX_RECENT_DIRS = 5

def info():
    from .gui.mainwin import sg, RPY2INSTALLED, MainWin
    from .misc import yesno

    settings_file = MainWin().settings.settings_file
    return ["Python {}".format(PYTHON_VERSION),
        "PySimpleGui {}".format(sg.version),
        "RPY2 installed {}".format(yesno(RPY2INSTALLED)),
        "Settings {}".format(settings_file)]