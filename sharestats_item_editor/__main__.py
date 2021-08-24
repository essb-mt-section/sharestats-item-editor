from . import  __version__, APPNAME, WEBSITE
from .rexam_item_editor.cli import cli

#
# changes in rexam_item_editor for sharestats
#
from . import rexam_item_editor
rexam_item_editor.APPNAME = APPNAME
rexam_item_editor.WEBSITE = WEBSITE

from .rexam_item_editor import consts
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

    opt = cli("{} {}".format(APPNAME, __version__))

    SSItemEditorMainWin(clear_settings=opt["clear"],
                        monolingual=opt["monolingual"]).run()

if __name__ == "__main__":
    run()
