from . import __version__, APPNAME
from .cli import cli
from .gui.mainwin import MainWin

def run():

    opt = cli("{} {}".format(APPNAME, __version__))
    if opt["monolingual"]:
        languages = None
    else:
        languages = ("Dutch", "English")

    MainWin(reset_settings=opt["reset"],
            two_languages=languages).run()

if __name__ == "__main__":
    run()