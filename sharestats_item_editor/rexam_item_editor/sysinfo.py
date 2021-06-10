import sys as _sys

PYTHON_VERSION = "{0}.{1}.{2}".format(_sys.version_info[0],
                                      _sys.version_info[1],
                                      _sys.version_info[2])


def info():
    from PySimpleGUI import version as sq_version
    from . import WEBSITE
    from .rexam.r_render import RPY2INSTALLED
    from .gui.mainwin import MainWin
    from .misc import yesno

    settings_file = MainWin().settings.settings_file
    return ["Python {}".format(PYTHON_VERSION),
        "PySimpleGui {}".format(sq_version),
        "RPy2 installed: {}".format(yesno(RPY2INSTALLED)),
        "Settings: {}".format(settings_file),
        "Web: {}".format(WEBSITE)]