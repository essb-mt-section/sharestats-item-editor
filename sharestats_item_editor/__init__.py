"""
"""

__version__ = '0.1.14.4'
__author__ = 'Oliver Lindemann'

DEVELOPER_VERSION = False # include preliminary features
APPNAME = "ShareStats Item Editor"

import sys as _sys
from .json_settings import JSONSettings as _JSONSettings


if DEVELOPER_VERSION:
    __version__ += "-dev"

PYTHON_VERSION = "{0}.{1}.{2}".format(_sys.version_info[0],
                                      _sys.version_info[1],
                                      _sys.version_info[2])

if _sys.version_info[0] != 3 or _sys.version_info[1]<5:

    raise RuntimeError("{} {} ".format(APPNAME, __version__) +
                      "is not compatible with Python {0}".format(
                          PYTHON_VERSION) +
                      "\n\nPlease use Python 3.5 or higher.")

if len(_sys.argv)>1:
    _reset = _sys.argv[1] == "-r" # reset
    _info = _sys.argv[1] == "-i"
else:
    _reset = False
    _info = False

settings = _JSONSettings(appname=APPNAME.replace(" ", "_").lower(),
                         settings_file_name="settings.json",
                         defaults= {"recent_dirs": []},
                         reset=_reset)

def info():
    from .gui.mainwin import sg, RPY2INSTALLED
    from .misc import yesno

    return ["Python {}".format(PYTHON_VERSION),
        "PySimpleGui {}".format(sg.version),
        "RPY2 installed {}".format(yesno(RPY2INSTALLED)),
        "Settings {}".format(settings.settings_file)]

if _info:
    print("{} {}".format(APPNAME, __version__))
    print("\n".join(info()))
    exit()


#FIXME improve pyinstaller settings