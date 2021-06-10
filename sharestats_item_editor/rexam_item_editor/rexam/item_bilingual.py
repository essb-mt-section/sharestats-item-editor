from .rmd_file import RmdFile, TAG_NL, TAG_ENG, TAG_BILINGUAL
from .item import RExamItem

class EntryBiLingFileList(object):
    """representation of two RMD Files
    item is always the reference language (NL)
    """

    REFERENCE_LANGUAGE = "nl"

    def __init__(self, rmd_file_item, rmd_file_translation=None):

        x = []
        for rmd in (rmd_file_item, rmd_file_translation):
            if rmd is None:
                x.append(None)
            else:
                if isinstance(rmd, RmdFile):
                    x.append(rmd)
                else:
                    x.append(RmdFile(rmd))

        if (x[0] is None and x[1] is not None):
            x = x[1], x[0]

        elif x[1] is not None:
            # --> bilingual: swap, if item 1 is NL
            if x[1].language_code == EntryBiLingFileList.REFERENCE_LANGUAGE:
                x = x[1], x[0]

        self._item = x[0]
        self._translation = x[1]

    def __str__(self):
        if self._item is None:
            i = "None"
        else:
            i = self._item.relative_path
        if self._translation is None:
            t = "None"
        else:
            t = self._translation.relative_path

        return "{}: ({}, {})".format(self.shared_name(), i, t)

    @property
    def rmd_item(self):
        return self._item

    @property
    def rmd_translation(self):
        return self._translation

    def shared_name(self, add_bilingual_tag=True, lower_case=True):

        if self._item is not None and self._translation is None:
            return self._item.name.lower()
        elif self._item is None and self._translation is not None:
            return self._translation.name.lower()
        elif self._item is None and self._translation is None:
            return None
        else:
            # is bilingual
            name = self._item.name.lower()
            if name.endswith(TAG_NL) or \
                    name.endswith(TAG_ENG):
                name = name[:-3]
            if add_bilingual_tag:
                name = name + TAG_BILINGUAL
            return name


    def is_bilingual(self):
        return self._translation is not None and self._item is not None


class EntryItemDatabase(object):

    def __init__(self, shared_name, item, translation):
        assert isinstance(item, RExamItem) or item is None
        assert isinstance(translation, RExamItem) or translation is None
        self.shared_name = shared_name
        self.item = item
        self.translation = translation
        self.id = None

    def is_same_as(self, item):
        """compares shared names and version id
        and ignores the id"""

        if isinstance(item, EntryItemDatabase):
            return self.shared_name == item.shared_name and\
                self.version_item == item.version_item and \
                self.version_translation == item.version_translation
        else:
            return False

    @property
    def version_item(self):
        try:
            return self.item.version_id
        except:
            return ""

    @property
    def version_translation(self):
        try:
            return self.translation.version_id
        except:
            return ""

    @property
    def version_item_short(self):
        return self.version_translation[:7]

    @property
    def version_translation_short(self):
        return self.version_item[:7]

    def short_repr(self, max_lines, add_versions=False, short_version=True):
        try:
            a_txt = self.item.question.str_text_short(max_lines)
        except:
            a_txt = ""
        try:
            b_txt = self.translation.question.str_text_short(max_lines)
        except:
            b_txt = ""

        rtn = [self.shared_name, a_txt, b_txt]
        if add_versions:
            if short_version:
                rtn.extend([self.version_item_short,
                            self.version_translation_short])
            else:
                rtn.extend([self.version_item, self.version_translation])
        return rtn

    @staticmethod
    def load(biling_filelist_entry, shared_name_with_bilingual_tag=False):
        assert isinstance(biling_filelist_entry, EntryBiLingFileList)

        if biling_filelist_entry.rmd_item is not None:
            item = RExamItem(biling_filelist_entry.rmd_item.full_path)
        else:
            item = None

        if biling_filelist_entry.rmd_translation is not None:
            translation = RExamItem(
                biling_filelist_entry.rmd_translation.full_path)
        else:
            translation = None

        return EntryItemDatabase(
                shared_name=biling_filelist_entry.shared_name(
                                    add_bilingual_tag=shared_name_with_bilingual_tag),
                item=item,
                translation=translation)