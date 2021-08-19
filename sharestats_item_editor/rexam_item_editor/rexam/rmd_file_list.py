import os
from os import path
from .. import misc
from .rmd_file import RmdFile, CODE_L1, CODE_L2, TAG_L1, TAG_L2, TAG_BILINGUAL


class BiLingualRmdFilePair(object):
    """Two RMD Files, reference language and translation
    """

    def __init__(self, rmd_file_item, rmd_file_translation=None,
                        reference_language_code=None):
        """if reference language_code is defined, items that does not have
        this reference code will be stored as rmd_translation """

        x = []
        for rmd in (rmd_file_item, rmd_file_translation):
            if rmd is None:
                x.append(None)
            else:
                if isinstance(rmd, RmdFile):
                    x.append(rmd)
                else:
                    x.append(RmdFile(rmd))

        if (x[0] is None and x[1] is not None):
            x = x[1], x[0]

        elif x[1] is not None:
            # --> two languages: swap, if x[1] is NL
            if reference_language_code is not None and \
                    x[1].language_code == reference_language_code:
                x = x[1], x[0]

        self._item = x[0]
        self._translation = x[1]

    def __str__(self):
        if self._item is None:
            i = "None"
        else:
            i = self._item.relative_path
        if self._translation is None:
            t = "None"
        else:
            t = self._translation.relative_path

        return "{}: ({}, {})".format(self.shared_name(), i, t)

    @property
    def rmd_item(self):
        return self._item

    @property
    def rmd_translation(self):
        return self._translation

    def shared_name(self, add_bilingual_tag=True):

        if self._item is not None and self._translation is None:
            return self._item.name.lower()
        elif self._item is None and self._translation is not None:
            return self._translation.name.lower()
        elif self._item is None and self._translation is None:
            return None
        else:
            # is bilingual
            name = self._item.name.lower()
            if name.endswith(TAG_L1) or \
                    name.endswith(TAG_L2):
                name = name[:-3]
            if add_bilingual_tag:
                name = name + TAG_BILINGUAL
            return name

    def is_bilingual(self):
        return self._translation is not None and self._item is not None


class BiLingRmdFileList(object):

    Entry = BiLingualRmdFilePair

    def __init__(self, base_directory=None, files_first_level=True,
                                    files_second_level=True,
                                    check_for_bilingual_files=True):
        self.files = []
        self.base_directory = base_directory
        self.files_first_level = files_first_level
        self.files_second_level = files_second_level

        # check for matching languages
        lst = misc.CaseInsensitiveStringList(self.get_rmd_files())

        self._file_list_hash = hash(tuple(lst.get())) # simple hashes for online
        # change detection, this are not the version IDs!

        if check_for_bilingual_files:
            reference_language = CODE_L1
        else:
            reference_language = None
        second = None
        while len(lst) > 0:
            first = RmdFile(file_path=lst.pop(0),
                            base_directory=self.base_directory)

            if check_for_bilingual_files:
                second = first.get_other_language_rmdfile()

            if second is not None and second.full_path in lst:
                # get in correct cases
                second_full_cases = lst.remove(second.full_path)
                lst.remove_all(second_full_cases) # remove all others versions (should not be the case)
                second = RmdFile(file_path=second_full_cases,
                                 base_directory=self.base_directory)
            else:
                second = None

            self.files.append(BiLingRmdFileList.Entry(rmd_file_item=first,
                                                      rmd_file_translation=second,
                                                      reference_language_code=reference_language))

        self.files = sorted(self.files, key=lambda x:x.shared_name())

    def get_count(self):

        rtn = {"total": len(self.files),
                CODE_L1: 0,
                CODE_L2: 0,
                "bilingual": 0,
                "undef": 0}

        for f in self.files:
            if f.is_bilingual():
                rtn["bilingual"] += 1
            else:
                try:
                    lang = f.rmd_item.language_code
                except:
                    lang = None
                try:
                    rtn[lang] += 1
                except:
                    rtn["undef"] += 1

        return rtn

    def is_file_list_changed(self):
        lst = self.get_rmd_files()
        return hash(tuple(lst)) != self._file_list_hash

    def get_shared_names(self, bilingual_tag=True):
        return [x.shared_name(bilingual_tag) for x in self.files]

    def find_shared_name(self, name):
        tmp = self.get_shared_names(bilingual_tag=False)
        try:
            return tmp.index(name)
        except:
            return None

    def find_filename(self, fl_name):
        """find idx by file name of first or second language"""

        for cnt, fl in enumerate(self.files):
            if fl.rmd_item.filename == fl_name or \
                    (fl.rmd_translation is not None and
                     fl.rmd_translation.filename == fl_name):
                return cnt

        return None

    def get_rmd_files(self, suffix=RmdFile.SUFFIX):
        """returns list with Rmd files at the second levels and/or first
        level (depending on files_first_level and files_second_level).

         Second level files: The file with the same name as the folder;
         otherwise first rexam found is this subfolder return.

         returns absolute pathes """

        if self.base_directory is None:
            return []
        lst = []
        for name in os.listdir(self.base_directory):
            fld = path.join(self.base_directory, name)
            if path.isdir(fld) and self.files_second_level:
                good_fl_name = path.join(fld, name + suffix)
                if path.isfile(good_fl_name):
                    lst.append(good_fl_name)
                else:
                    # search for a rexam file in the subdirectory
                    try:
                        subdir_lst = os.listdir(fld)
                    except:
                        subdir_lst = []  # no permission to access dir
                    for fl_name in map(lambda x: path.join(fld, x), subdir_lst):
                        # no permission
                        if fl_name.lower().endswith(suffix.lower()):
                            # best guess
                            lst.append(fl_name)
                            break

            elif path.isfile(fld) and self.files_first_level:
                if fld.lower().endswith(suffix.lower()):
                    lst.append(fld)

        return [path.abspath(x) for x in lst]


