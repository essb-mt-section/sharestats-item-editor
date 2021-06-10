import sys
from . import __version__, APPNAME, sysinfo

from .gui.mainwin import MainWin

def run():
    if sys.version_info[0] != 3 or sys.version_info[1] < 5:
        raise RuntimeError("{} {} ".format(APPNAME, __version__) +
                           "is not compatible with Python {0}".format(
                               sysinfo.PYTHON_VERSION) +
                           "\n\nPlease use Python 3.5 or higher.")

    if len(sys.argv) > 1:
        reset = sys.argv[1] == "-r"  # reset
        info = sys.argv[1] == "-i"
    else:
        reset = False
        info = False

    if info:
        print("{} {}".format(APPNAME, __version__))
        print("\n".join(sysinfo.info()))
        exit()

    MainWin(reset_settings=reset).run()

if __name__ == "__main__":
    run()