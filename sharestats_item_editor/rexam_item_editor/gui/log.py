import os
import logging
import appdirs
from .. import APPNAME
from PySimpleGUI import Print

def get_log_file():
    appname = APPNAME.replace(" ", "_").lower()
    cache_dir = appdirs.user_cache_dir(appname)
    try:
        os.mkdir(cache_dir)
    except:
        pass
    return os.path.join(cache_dir, "{}.log".format(appname))


def init_logging():
        log_file = get_log_file()
        logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s]  %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filename=log_file,
                        filemode='a')
        print("Log file: {}".format(log_file))

def log(txt, gui_log=True):

    if txt in (None, False):
        return

    for l in str(txt).split("\n"):
        if gui_log:
            Print(l)
            if l.startswith("WARNING"):
                Print("-" * 80 + "\n")
            elif l.startswith("ERROR"):
                Print("-" * 80 + "\n")

        if len(l)>0:
            if l.startswith("WARNING"):
                logging.warning(l)
            elif l.startswith("ERROR"):
                logging.error(l)
            else:
                logging.info(l)

