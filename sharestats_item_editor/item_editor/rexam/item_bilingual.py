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
                if isinstance(rmd_file_item, RmdFile):
                    x.append(rmd_file_item)
                else:
                    x.append(RmdFile(rmd_file_item))

        if (x[0] is None and x[1] is not None):
            x = x[1], x[0]
        elif x[1] is not None:
            # --> bilingual: swap, if item 1 is NL
            if x[1].language_code == EntryBiLingFileList.REFERENCE_LANGUAGE:
                x = x[1], x[0]

        self._item = x[0]
        self._translation = x[1]

    @property
    def rmd_item(self):
        return self._item

    @property
    def rmd_translation(self):
        return self._translation

    def shared_name(self, add_bilingual_tag=True):

        if self._item is not None and self._translation is None:
            return  self._item.name
        elif self._item is None and self._translation is not None:
            return  self._translation.name
        elif self._item is None and self._translation is None:
            return None
        else:
            # is bilingual
            name = self._item.name
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
        self._version_item = None
        self._version_translation = None

    @property
    def version_item(self):
        if self._version_item is None:
            try:
                self._version_item = self.item.version_id()
            except:
                self._version_item = ""

        return self._version_item

    @property
    def version_translation(self):
        if self._version_translation is None:
            try:
                self._version_translation = self.translation.version_id()
            except:
                self._version_translation = ""

        return self._version_translation

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
    def load(biling_filelist_entry, add_bilingual_tag=False):
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
                                    add_bilingual_tag=add_bilingual_tag),
                item=item,
                translation=translation)