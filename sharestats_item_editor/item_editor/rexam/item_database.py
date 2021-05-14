from ..misc import iter_list, remove_all
from .bilingual import BilingualFileList


class _SearchSchemata(object):

    def __init__(self):
        self.search_types = []
        self.parameter = []
        self.functions = []

    def add(self, search_type, parameter):
        """para: search_type has to be 'name', 'question', 'solution',
        'meta_info' or 'raw_rmd'
        if parameter is iterable (but not a string), it will be multiple
        functions with different parameter.
        """

        if not isinstance(parameter, str) and hasattr(parameter, "__iter__"):
            for p in parameter:
                self._add(search_type, p)
        else:
            self._add(search_type, parameter)

    def _add(self, search_type, parameter):
        if search_type == "name":
            f = lambda x: x.filename.name.find(parameter)
        elif search_type == "question":
            f = lambda x: x.question.str_text.find(parameter)
        elif search_type == "solution":
            f = lambda x: x.solution.str_text.find(parameter)
        elif search_type == "meta_info":
            f = lambda x: x.meta_info.str_text.find(parameter)
        elif search_type == "raw_rmd":
            f = lambda x: str(x).find(parameter)
        else:
            raise RuntimeError("{} is an unknown SearchFunction "
                               "type.".format(search_type))

        self.functions.append(f)
        self.parameter.append(parameter)
        self.search_types.append(search_type)



class ItemDatabase(BilingualFileList):

    def __init__(self, folder):
        """file_list_bilingual: path or file_list_biligual
        """
        super().__init__(folder=folder)
        self.items = []
        self.translations = []
        self.marked_items = []
        self._sel_idx = []

        self.shared_names = self.get_shared_names(bilingual_tag=False)
        self._all_ids = range(len(self.files))

        ## LOAD DATA
        for c in self._all_ids:
            rexam_fls = self.load_rexam_files(c)
            self.items.append(rexam_fls[0])
            self.translations.append(rexam_fls[1])

        #version_ids
        def fnc_version_id(item):
            try:
                return item.version_id()
            except:
                return ""
        self.versions_item = list(map(fnc_version_id, self.items))
        self.versions_translation = list(map(fnc_version_id, self.translations))

        self.select() # select all

    def get_subset_data(self, ids):
        """returns selection
         name, item, translation, item_version,
                    translation_version
        """
        data = zip(self._all_ids, self.shared_names, self.items,
                   self.translations, self.versions_item,
                   self.versions_translation)
        return [d for d in data if d[0] in ids] #TODO make dict here?


    @property
    def selected_data(self):
        """selected name, item, translation, item_version,
                    translation_version"""
        return self.get_subset_data(self._sel_idx)

    @property
    def marked_data(self):
        return self.get_subset_data(self.marked_items)

    def _search(self, search_function, item_ids_subset):
        """searches rexam file using search_function and returns idx,
        if found for at least one of the language.
        Use item_ids_subset (array if ids) to define the the  subset of
        items, in which you want to serach """

        idx = []
        for x in item_ids_subset:

            try:
                found = search_function(self.items[x])
            except:
                found = -1

            if found<0:
                try:
                    found = search_function(self.translations[x])
                except:
                    found = -1

            if found>=0:
                idx.append(x)

        return idx


    def select(self, name=None, question=None, solution=None,
                     meta_information=None, raw_rmd=None,
                     search_logic_or=False):

        # select all
        self._sel_idx = self._all_ids

        search = _SearchSchemata()
        search.add("name", iter_list(name))
        search.add("question", iter_list(question))
        search.add("solution", iter_list(solution))
        search.add("meta_info", iter_list(meta_information))
        search.add("raw_rmd", iter_list(raw_rmd))

        if search_logic_or:
            # OR
            idx = []
            for fnc in search.functions:
                for x in self._search(fnc, item_ids_subset=self._sel_idx):
                    if x not in idx:
                        idx.append(x)
            self._sel_idx = sorted(idx)
        else:
            # AND
            for fnc in search.functions:
                self._sel_idx = self._search(fnc, item_ids_subset=self._sel_idx)

        return self._sel_idx

    def get_question_overview(self, max_lines=3):
        """returns table with item_id, name, short question item,
        short question translation, item_version, tranlsation_version"""

        rtn = []
        for item_id, name, item, translation, ver_item, ver_translation in \
                self.selected_data:
            try:
                a_txt = item.question.str_text_short(max_lines)
            except:
                a_txt = ""
            try:
                b_txt = translation.question.str_text_short(max_lines)
            except:
                b_txt = ""

            rtn.append([item_id, name, a_txt, b_txt, ver_item, ver_translation])

        return rtn

    def add_mark(self, id):
        if id not in self.marked_items:
            self.marked_items.append(id)

    def remove_mark(self, id):
        self.marked_items = [e for e in self.marked_items if e != id]