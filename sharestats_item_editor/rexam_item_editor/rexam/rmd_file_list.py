import os
from os import path
from .. import misc
from .rmd_file import RmdFile, CODE_L1, CODE_L2, TAG_L1, TAG_L2, TAG_BILINGUAL
from .git_info import GitInfo

class BiLingualRmdFilePair(object):
    """Two RMD Files: l1 and l2
    """

    def __init__(self, rmd_file_a, rmd_file_b=None,
                 reference_language_code=None):
        """if reference language_code is defined, items that does not have
        this reference code will be stored as rmd_l2 """

        x = []
        for rmd in (rmd_file_a, rmd_file_b):
            if rmd is None:
                x.append(None)
            else:
                if isinstance(rmd, RmdFile):
                    x.append(rmd)
                else:
                    x.append(RmdFile(rmd))

        if x[0] is None and x[1] is not None:
            x = x[1], x[0]

        elif x[1] is not None:
            # --> two languages: swap, if x[1] is NL
            if reference_language_code is not None and \
                    x[1].language_code == reference_language_code:
                x = x[1], x[0]

        self._l1 = x[0]
        self._l2 = x[1]

    def __str__(self):
        if self._l1 is None:
            i = "None"
        else:
            i = self._l1.relative_path
        if self._l2 is None:
            t = "None"
        else:
            t = self._l2.relative_path

        return "{}: ({}, {})".format(self.shared_name(), i, t)

    @property
    def rmdfile_l1(self):
        return self._l1

    @property
    def rmdfile_l2(self):
        return self._l2

    def shared_name(self, add_bilingual_tag=True):

        if self._l1 is not None and self._l2 is None:
            return self._l1.name.lower()
        elif self._l1 is None and self._l2 is not None:
            return self._l2.name.lower()
        elif self._l1 is None and self._l2 is None:
            return None
        else:
            # is bilingual
            name = self._l1.name.lower()
            if name.endswith(TAG_L1) or \
                    name.endswith(TAG_L2):
                name = name[:-3]
            if add_bilingual_tag:
                name = name + TAG_BILINGUAL
            return name

    def is_bilingual(self):
        return self._l2 is not None and self._l1 is not None


class BiLingRmdFileList(object):

    def __init__(self, base_directory=None, files_first_level=True,
                                    files_second_level=True,
                                    check_for_bilingual_files=True):
        self.files = []
        self.base_directory = base_directory
        self.files_first_level = files_first_level
        self.files_second_level = files_second_level
        self.check_for_bilingual_files = check_for_bilingual_files

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

            self.files.append(BiLingualRmdFilePair(rmd_file_a=first,
                                                   rmd_file_b=second,
                                                   reference_language_code=reference_language))

        self.files = sorted(self.files, key=lambda x:x.shared_name())

    def get_current_git_head_basedir(self):
        """returns the current git head of the based directory"""
        if self.base_directory is None:
            return ""
        else:
            return GitInfo(self.base_directory).head


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
                    lang = f.rmdfile_l1.language_code
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
            if fl.rmdfile_l1.filename == fl_name or \
                    (fl.rmdfile_l2 is not None and
                     fl.rmdfile_l2.filename == fl_name):
                return cnt

        return None

    def get_rmd_files(self, suffix=RmdFile.SUFFIX):
        """returns list with Rmd files at the second levels and/or first
        level (depending on files_first_level and files_second_level).

         Second level files: The file with the same name as the folder;
         otherwise first rexam found is this subfolder return.

         returns absolute paths """

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


