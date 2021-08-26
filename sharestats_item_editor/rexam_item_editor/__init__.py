"""RExam Item Editor

(c) Oliver Lindemann
"""

__version__ = '0.2.11'
__author__ = 'Oliver Lindemann'
APPNAME = "RExam Item Editor"
WEBSITE = "https://github.com/lindemann09/rexam-item-editor"

from sys import version_info as _vi
if _vi[0] != 3 or _vi[1] < 5:
    from .sysinfo import PYTHON_VERSION
    raise RuntimeError("{} {} ".format(APPNAME, __version__) +
                       "is not compatible with Python {0}".format(
                           PYTHON_VERSION) +
                       "\n\nPlease use Python 3.5 or higher.")

