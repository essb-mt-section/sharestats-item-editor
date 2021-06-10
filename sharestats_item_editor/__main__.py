import sys
from . import  __version__, APPNAME, WEBSITE
from .rexam_item_editor import sysinfo

if sys.version_info[0] != 3 or sys.version_info[1] < 5:
    raise RuntimeError("{} {} ".format(APPNAME, __version__) +
                       "is not compatible with Python {0}".format(
                           sysinfo.PYTHON_VERSION) +
                       "\n\nPlease use Python 3.5 or higher.")
#
# changes in rexam_item_editor for sharestats
#
from . import rexam_item_editor
rexam_item_editor.APPNAME = APPNAME
rexam_item_editor.WEBSITE = WEBSITE

from .rexam_item_editor.gui import consts
consts.FILELIST_FIRST_LEVEL_FILES = False
consts.FILELIST_SECOND_LEVEL_FILES = True

from .meta_info import SSItemMetaInfo
from .rexam_item_editor.rexam.item import RExamItem
RExamItem.META_INFO_CLASS = SSItemMetaInfo

from . import templates as states_share_templates
from .rexam_item_editor import templates
templates.FILES = states_share_templates.FILES

from .mainwin import SSItemEditorMainWin

def run():

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

    SSItemEditorMainWin(reset_settings=reset).run()

if __name__ == "__main__":
    run()