from . import __version__, APPNAME
from .cli import cli


def run():

    opt = cli("{} {}".format(APPNAME, __version__))

    if opt["exam_compiler"]:
        from .gui.exam_compiler import ExamCompiler
        ExamCompiler().run()
    else:
        from .gui.mainwin import MainWin
        MainWin(reset_settings=opt["reset"],
            monolingual=opt["monolingual"]).run()


if __name__ == "__main__":
    run()
