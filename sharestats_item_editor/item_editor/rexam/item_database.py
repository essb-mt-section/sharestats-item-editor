from ..misc import iter_list
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
        self.data = []
        self._idx = []
        cnt = 0
        for rexam_fls, name in zip(self.iter_rexam_files(),
                    self.get_shared_names(bilingual_tag=False)):
            self.data.append([cnt, name, rexam_fls[0], rexam_fls[1]])
            cnt += 1

        self.select() # select all

    @property
    def selected_data(self):
        """selected rows"""
        return [x for x in self.data if x[0] in self._idx]

    @staticmethod
    def _search(items, search_function):
        """searches rexam file in ros using search_function and returns idx,
        if found for at least one of the language"""

        idx = []
        for x in items:
            try:
                found = search_function(x[2])
            except:
                found = -1

            if found<0:
                try:
                    found = search_function(x[3])
                except:
                    found = -1

            if found>=0:
                idx.append(x[0])

        return idx


    def select(self, name=None, question=None, solution=None,
                     meta_information=None, raw_rmd=None,
                     search_logic_or=False):

        search = _SearchSchemata()
        search.add("name", iter_list(name))
        search.add("question", iter_list(question))
        search.add("solution", iter_list(solution))
        search.add("meta_info", iter_list(meta_information))
        search.add("raw_rmd", iter_list(raw_rmd))

        if len(search.functions)==0:
            # select all
            self._idx = range(len(self.data))

        elif search_logic_or:
            # OR
            idx = []
            for fnc in search.functions:
                for x in ItemDatabase._search(self.data, fnc):
                    if x not in idx:
                        idx.append(x)
            self._idx = sorted(idx)
        else:
            # AND
            self._idx = range(len(self.data))
            for fnc in search.functions:
                self._idx = ItemDatabase._search(self.selected_data, fnc)

        return self._idx

    def get_question_overview(self, max_lines=3):
        """returns table with cnt, name, short question a, short question b"""
        rtn = []
        for r in self.selected_data:
            try:
                a_txt = r[2].question.str_text_short(max_lines)
                a_version = r[2].version_id()
            except:
                a_txt = ""
                a_version = ""
            try:
                b_txt = r[3].question.str_text_short(max_lines)
                b_version = r[2].version_id()
            except:
                b_txt = ""
                b_version = ""
            rtn.append([r[0], r[1], a_txt, b_txt, a_version, b_version])

        return rtn