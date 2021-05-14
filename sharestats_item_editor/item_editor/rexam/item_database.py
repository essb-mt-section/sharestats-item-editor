from .bilingual import BilingualFileList

class ItemDatabase(object):

    def __init__(self, file_list_bilingual):
        assert isinstance(file_list_bilingual, BilingualFileList)
        self.file_list = file_list_bilingual
        self.data = []
        self._idx = []
        cnt = 0
        for rexam_fls, name in zip(self.file_list.iter_rexam_files(),
                    self.file_list.get_shared_names(bilingual_tag=False)):
            self.data.append([cnt, name, rexam_fls[0], rexam_fls[1]])
            cnt += 1

        self.reset_search()

    def reset_search(self):
        """similar to select all"""
        self._idx = range(len(self.data))

    @property
    def selected_rows(self):
        """selected rows"""
        return [x for x in self.data if x[0] in self._idx]

    def _find_idx(self, search_function):
        """searches rexam file using search_function and returns idx,
        if found for one of the laguages"""
        idx = []
        for x in self.selected_rows:
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

    def search_name(self, text):
        self._idx = self._find_idx(lambda x: x.filename.name.find(text))

    def search_question(self, text):
        self._idx = self._find_idx(lambda x: x.question.str_text.find(text))

    def search_meta_info(self, text):
        self._idx = self._find_idx(lambda x: x.meta_info.str_text.find(text))

    def search_solution(self, text):
        self._idx = self._find_idx(lambda x: x.solution.str_text.find(text))

    def search_raw_rmd(self, text):
        self._idx = self._find_idx(lambda x: str(x).find(text))

    def get_question_overview(self, max_lines=3):
        """returns table with cnt, name, short question a, short question b"""
        rtn = []
        for r in self.selected_rows:
            try:
                a_txt = r[2].question.str_text_short(max_lines)
            except:
                a_txt = ""
            try:
                b_txt = r[3].question.str_text_short(max_lines)
            except:
                b_txt = ""

            rtn.append([r[0], r[1], a_txt, b_txt])

        return rtn