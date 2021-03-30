from os import path
import json as json

class Taxonomy(object):

    def __init__(self):
        with open(path.join(path.dirname(__file__), "taxonomy.json")) as fl:
            self._dict = json.load(fl)

    def _get_level(self, type, categories):

        d = self._dict[type]
        if categories is not None:
            d = _subdict(d, categories)

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


def _subdict(d, nested_keys=None):
    """:return the dict nested hierarchically indicated by nested_keys
    or None if key list is incorrect
    :param nested_keys list of keys or a single keys

    """
    if not isinstance(nested_keys, (tuple, list)):
        nested_keys = [nested_keys]
    for k in nested_keys:
        try:
            d = d[k]
        except:
            return {}
    return d

