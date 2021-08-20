from os import path
import json as json

from .rexam_item_editor import misc
from .rexam_item_editor.consts import FILE_ENCODING

class Taxonomy(object):

    TAX_KEY = 'Statistics Taxonomy'
    TAGS_KEY = 'Tags'

    def __init__(self):
        with open(path.join(path.dirname(__file__), "taxonomy.json"),
                  'r', encoding=FILE_ENCODING) as fl:
            self._dict = json.load(fl)

    def _get_level(self, type, categories):

        d = self._dict[type]
        if categories is not None:
            d = misc.subdict(d, categories)

        if len(d)==0:
            return None

        rtn = filter(lambda x: x!="name", d.keys()) # all keys except 'name'
        return list(rtn)

    def get_taxonomy_level(self, categories=None):
        """":param categories
                    list of nested categories or single category
        """

        rtn = self._get_level(Taxonomy.TAX_KEY, categories)
        if rtn is None:
            return []
        else:
            return rtn

    def get_tag_types(self):
        rtn = self._get_level(Taxonomy.TAGS_KEY, categories=None)
        for x in ("Program", "Language", "Level"):
            rtn.remove(x)
        return rtn

    def get_tag_programs(self):
        return self._get_level(Taxonomy.TAGS_KEY, "Program")

    def get_tag_languages(self):
        return self._get_level(Taxonomy.TAGS_KEY, "Language")

    def get_tag_levels(self):
        return self._get_level(Taxonomy.TAGS_KEY, "Level")

    def is_valid_taxonomy(self, tax_string):
        """Returns tuple (boolean, level descriptor that is invalid)"""
        if not isinstance(tax_string, str):
            return False, "Not a string"
        cat = []
        for level in map(lambda x:x.strip(), tax_string.split("/")):
            cat.append(level)
            if self._get_level(Taxonomy.TAX_KEY, categories=cat) is None:
                return False, level
        return True, ""



