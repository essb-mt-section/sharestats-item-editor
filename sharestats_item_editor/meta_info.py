from .item_editor.rexam.item_sections import ItemMetaInfo, Issue
from .item_editor.rexam.file_list import TAG_NL, TAG_ENG

from . import taxonomy

class SSItemMetaInfo(ItemMetaInfo):

    TAXONOMY = taxonomy.Taxonomy()

    @property
    def taxonomy(self):
        return self.section

    @taxonomy.setter
    def taxonomy(self, v):
        self.section = v

    @property
    def type_tag(self):
        return self._try_parameter("exextra[Type]")

    @type_tag.setter
    def type_tag(self, v):
        self.parameter["exextra[Type]"] = v

    @property
    def program(self):
        return self._try_parameter("exextra[Program]")

    @program.setter
    def program(self, v):
        self.parameter["exextra[Program]"] = v

    @property
    def language(self):
        return self._try_parameter("exextra[Language]")

    @language.setter
    def language(self, v):
        self.parameter["exextra[Language]"] = v

    @property
    def language_code(self):
        if self.language == "Dutch":
            return TAG_NL[1:]
        elif self.language == "English":
            return TAG_ENG[1:]
        else:
            return None

    @language_code.setter
    def language_code(self, v):
        if v == TAG_ENG[1:]:
            self.language = "English"
        elif v == TAG_NL[1:]:
            self.language = "Dutch"
        else:
            self.language = ""

    @property
    def level(self):
        return self._try_parameter("exextra[Level]")

    @level.setter
    def level(self, v):
        self.parameter["exextra[Level]"] = v

    def get_invalid_taxonomy_levels(self):
        """returns incorrect level descriptors"""
        incorrect_level = []
        for tax in self.taxonomy.split(","):
            if len(tax):
                valid, level = SSItemMetaInfo.TAXONOMY.is_valid_taxonomy(tax)
                if not valid:
                    incorrect_level.append(level)
        return incorrect_level

    def fix_name(self):
        self.name = self._parent.filename.name

    def fix_language(self):
        self.language_code = self._parent.filename.language_code

    def validate(self):
        issues = super().validate()

        # item name
        if self._parent.filename.name != self.name:
            issues.append(Issue("exanme",
                        "Item name (exname) does not match filename",
                                self.fix_name))

        # folder name equals filename
        # (should be always the last one, because of item saving)
        if not self._parent.filename.folder_mirrors_filename():
            issues.append(Issue("folder",
                    "Directory name does not match item name",
                    self._parent.fix_directory_name))

        # check taxonomy
        invalid_tax = self.get_invalid_taxonomy_levels()
        if len(invalid_tax):
            issues.append(Issue("tax levels",
                                "Invalid taxonomy levels: {}".format(
                ", ".join(invalid_tax))))

        # check language
        if self.language_code != self._parent.filename.language_code:
            if len(self._parent.filename.language_code):
                fix_function = self.fix_language
            else:
                fix_function = None

            issues.append(Issue("language",
                    "Mismatch languages in meta information and filename",
                                fix_function))

        return issues

#FIXME fix id lower-uppercase dublicate exist (try:..except:..)
