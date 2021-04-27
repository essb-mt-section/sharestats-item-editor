from ..rexam import ItemMetaInfo, Issue
from ..sharestats import taxonomy

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
    def level(self):
        return self._try_parameter("exextra[Level]")

    @level.setter
    def level(self, v):
        self.parameter["exextra[Level]"] = v

    def get_invalid_taxonomy_levels(self):
        """returns incorrect level descriptors"""
        incorrect_level = []
        for tax in self.taxonomy.split(","):
            valid, level = SSItemMetaInfo.TAXONOMY.is_valid_taxonomy(tax)
            if not valid:
                incorrect_level.append(level)
        return incorrect_level

    def fix_name(self):
        self.name = self._parent.filename.name


    def validate(self):
        issues = super().validate()

        # item name
        if self._parent.filename.name != self.name:
            issues.append(Issue("Item name (exname) does not match filename",
                                self.fix_name))

        # folder name equals filename
        # (should be always the last one, because of item saving)
        if not self._parent.filename.folder_mirrors_filesname():
            issues.append(Issue("Directory name does not match item name",
                                self._parent.filename.set_mirroring_folder_name))

        # check taxonomy
        invalid_tax = self.get_invalid_taxonomy_levels()
        if len(invalid_tax):
            issues.append(Issue("Invalid taxonomy levels: {}".format(
                ", ".join(invalid_tax))))

        return issues