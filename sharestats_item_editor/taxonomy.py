from os import path
import json as json

from sharestats_item_editor import misc

class Taxonomy(object):

    def __init__(self):
        with open(path.join(path.dirname(__file__), "taxonomy.json")) as fl:
            self._dict = json.load(fl)

    def _get_level(self, type, categories):

        d = self._dict[type]
        if categories is not None:
            d = misc.subdict(d, categories)

        rtn = filter(lambda x: x!="name", d.keys()) # all keys except 'name'
        return list(rtn)

    def get_taxonomy_level(self, categories=None):
        """":param categories
                    list of nested categories or single category
        """

        return self._get_level('Statistics Taxonomy', categories)

    def get_tags_type(self):
        rtn = self._get_level('Tags', categories=None)
        for x in ("Program", "Language", "Level"):
            rtn.remove(x)
        return rtn

    def get_tags_program(self):
        return self._get_level('Tags', "Program")

    def get_tags_language(self):
        return self._get_level('Tags', "Language")

    def get_tags_level(self):
        return self._get_level('Tags', "Level")

#FIXME validate taxonomy entries