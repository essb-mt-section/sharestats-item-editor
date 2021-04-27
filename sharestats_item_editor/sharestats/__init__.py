"""
The module contain all modification of the item editor for the stats share
projects. Import main window of this module an override MainWin in __main__.

(c) O. Lindemann
"""

from .. import consts
consts.APPNAME = "ShareStats Item Editor"

from .meta_info import SSItemMetaInfo
from ..rexam import RExamItem
RExamItem.META_INFO_CLASS = SSItemMetaInfo

from .mainwin import SSItemEditorMainWin