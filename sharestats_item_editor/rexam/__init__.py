
# use SSItemMetaInfo
from .rexam_item import RExamItem
from .issue import Issue
from .item_sections import AnswerList, ItemSection, ItemMetaInfo
from .files import RmdFile, FileListBilingual

from ..sharestats.meta_info import SSItemMetaInfo
RExamItem.META_INFO_CLASS = SSItemMetaInfo
