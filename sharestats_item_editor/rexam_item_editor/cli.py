import argparse
from . import sysinfo

def cli(app_name):
    """returns dict with selected command line option"""

    parser = argparse.ArgumentParser(
        description=app_name,
        epilog="(c) O. Lindemann, 2021")

    parser.add_argument("-c", "--clear", action="store_true",
                        help="reset app and clear settings file",
                        default=False)

    parser.add_argument("-i", "--info",
                        action="store_true",
                        help="display system info",
                        default=False)

    parser.add_argument("--monolingual",
                        action="store_true",
                        help="switch to monolingual mode (default is "
                             "bilingual)",
                        default=False)

    parser.add_argument("-e", "--exam",
                        action="store_true",
                        help="run exam compiler",
                        default=False)

    parser.add_argument("-r", "--rcode", nargs='?', metavar="JSON-FILE", type=str,
                        help="convert exam file to r code",
                        default=False)

    parser.add_argument("-m", "--markdown", nargs='?', metavar="JSON-FILE", type=str,
                        help="convert exam file to simple markdown",
                        default=False)

    parser.add_argument("--l2", action="store_true",
                        help="use second language when converting exam",
                        default=False)

    opt = vars(parser.parse_args())

    if opt["info"]:
        print(app_name)
        print("\n".join(sysinfo.info()))

    elif None in (opt["rcode"], opt["markdown"]):
        parser.print_help()
        print("")
        print("Please specify exam file.")

    elif opt["rcode"]:
        from .rexam import exam
        a = exam.Exam(opt["rcode"])
        print(a.rexam_code(use_l2=opt["l2"]))

    elif opt["markdown"]:
        from .rexam import exam
        a = exam.Exam(opt["markdown"])
        print(a.markdown(use_l2=opt["l2"]))

    elif opt["exam"]:
        from .gui.exam_compiler import ExamCompiler
        ExamCompiler().run()

    else:
        return opt

    exit()
