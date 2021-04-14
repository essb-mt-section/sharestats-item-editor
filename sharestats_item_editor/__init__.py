"""
"""

__version__ = '0.1.8'
__author__ = 'Oliver Lindemann'

DEVELOPER_VERSION = False # include preliminary features


import sys as _sys
from . import consts
from .json_settings import JSONSettings as _JSONSettings

if _sys.version_info[0] != 3 or _sys.version_info[1]<5:

    raise RuntimeError("{} {} ".format(consts.APPNAME, __version__) +
                      "is not compatible with Python {0}.{1}.".format(
                                                    _sys.version_info[0],
                                                    _sys.version_info[1]) +
                      "\n\nPlease use Python 3.5 or higher.")

settings = _JSONSettings(appname=consts.APPNAME.replace(" ", "_").lower(),
                         settings_file_name="settings.json",
                         defaults= {"recent_dirs": []})

if DEVELOPER_VERSION:
    __version__ += "-dev"