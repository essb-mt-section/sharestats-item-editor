from .rmd_file import RmdFile, TAG_NL, TAG_ENG, TAG_BILINGUAL
from .item import RExamItem

class EntryItemFileList(object):
    """representation of two RMD Files"""

    def __init__(self, rmd_file_item, rmd_file_translation=None):

        if rmd_file_item is None and rmd_file_translation is not None:
            rmd_file_translation, rmd_file_item = \
                rmd_file_item, rmd_file_translation  # swap

        if isinstance(rmd_file_item, RmdFile):
            a = rmd_file_item
        else:
            a = RmdFile(rmd_file_item)

        if rmd_file_translation is not None:
            if isinstance(rmd_file_translation, RmdFile):
                b = rmd_file_translation
            else:
                b = RmdFile(rmd_file_translation)
            if b.language_code == "nl":  # NL is reference language
                b, a = a, b
        else:
            b = None

        self._item = a
        self._translation = b

    @property
    def rmd_item(self):
        return self._item

    @property
    def rmd_translation(self):
        return self._translation

    def shared_name(self, add_bilingual_tag=True):
        """bilingual_file_list_entry: tuple of two entries"""

        name = self._item.name
        if len(name):
            if self._translation is not None:
                if name.endswith(TAG_NL) or \
                        name.endswith(TAG_ENG):
                    name = name[:-3]
                if add_bilingual_tag:
                    name = name + TAG_BILINGUAL
            return name

        else:
            return self._item.filename

    def is_bilingual(self):
        return self._translation is not None and self._item is not None


class EntryItemDatabase(object):

    def __init__(self, shared_name, item, translation):
        assert isinstance(item, RExamItem) or item is None
        assert isinstance(translation, RExamItem) or translation is None
        self.shared_name = shared_name
        self.item = item
        self.translation = translation
        try:
            self.version_item = item.version_id()
        except:
            self.version_item = ""

        try:
            self.version_translation = translation.version_id()
        except:
            self.version_translation = ""

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

