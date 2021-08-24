from . import __version__, APPNAME
from .cli import cli


def run():

    opt = cli("{} {}".format(APPNAME, __version__))

    from .gui.mainwin import MainWin
    MainWin(clear_settings=opt["clear"],
            monolingual=opt["monolingual"]).run()


if __name__ == "__main__":
    run()
