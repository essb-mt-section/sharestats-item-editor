from .rexam_item_editor.rexam.item import ItemMetaInfo, Issue
from .rexam_item_editor.rexam.rmd_file import RmdFile, TAG_L1, TAG_L2

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
            return TAG_L1[1:]
        elif self.language == "English":
            return TAG_L2[1:]
        else:
            return None

    @language_code.setter
    def language_code(self, v):
        if v == TAG_L2[1:]:
            self.language = "English"
        elif v == TAG_L1[1:]:
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
        self.name = self._parent.name

    def fix_language(self):
        self.language_code = self._parent.language_code

    def validate(self):
        issues = super().validate()

        # item name
        if self._parent.name != self.name:
            issues.append(Issue("exanme",
                        "Item name (exname) does not match filename",
                                self.fix_name))

        # check taxonomy
        invalid_tax = self.get_invalid_taxonomy_levels()
        if len(invalid_tax):
            issues.append(Issue("tax levels",
                                "Invalid taxonomy levels: {}".format(
                ", ".join(invalid_tax))))

        # check language
        if self.language_code != self._parent.language_code:
            if len(self._parent.language_code):
                fix_function = self.fix_language
            else:
                fix_function = None

            issues.append(Issue("language",
                    "Mismatch languages in meta information and filename",
                                fix_function))


        # folder name equals filename
        # (should be always the last one, because of item saving)
        if not self._parent.subdir_mirrors_filename():
            issues.append(Issue("folder",
                    "Directory name does not match item name",
                    self._parent.fix_directory_name,
                    fix_requires_gui_reset=True))

        elif self._parent.relative_path[:-3] != \
                self._parent.relative_path[:-3].lower():
            issues.append(Issue("Uppercases",
                                "Folder or file names contain uppercases",
                                self._parent.fix_uppercases_in_relative_path,
                                fix_requires_gui_reset =\
                                    self._parent.name.lower() + RmdFile.SUFFIX))

        return issues

#TODO fix id lower-uppercase doublicate exist (try:..except:..)
