import os
from os import path


class ShareStatsFilename(object):

    def __init__(self, file_path):
        if file_path is None:
            file_path=""
        self.directory, self.filename = path.split(file_path)

    @staticmethod
    def create(base_directory, university, topic, counter, language):
        try:
            cnt_str = "{0:0=3d}".format(counter)
        except:
            cnt_str = "{}".format(counter)

        name = "{}-{}-{}-{}".format(university, topic, cnt_str, language)
        return ShareStatsFilename(path.join(base_directory, name,
                                            "{}.Rmd".format(name)))

    def get_language(self):
        try:
            return self.get_parts()[3]
        except:
            return ""

    def get_parts(self):
        """None, if filename/path is not in good shape or returns a list of the
         filename parts [University, Topic, Count, Language]
        """

        rtn = self.stats_share_name.split("-")
        if len(rtn) != 4:
            return None
        else:
            try:
                rtn[2] = int(rtn[2])
            except:
                pass
            return rtn

    @property
    def stats_share_name(self):
        file_name = path.splitext(self.filename)[0]
        if file_name == path.split(self.directory)[1]:
            # file name == folder name
            return file_name
        else:
            return ""

    @property
    def path(self):
        return path.join(self.directory, self.filename)

    @property
    def base_directory(self):
        return path.split(self.directory)[0]

    def make_file(self):
        if path.isfile(self.path):
            return False
        try:
            os.makedirs(self.directory)
        except:
            pass

        try:
            open(self.path, "w").close()
            return True
        except:
            return False

    def get_axillary_files(self):
        all = map(lambda x:path.join(self.directory, x), os.listdir(self.directory))
        return filter(path.isfile, all)

    def __cmp__(self, other):
        if not isinstance(other, ShareStatsFilename):
            return False
        else:
            return self.path == other.path

    def __str__(self):
        return str(self.path)

    def get_other_language(self):
        parts = self.get_parts()
        if parts is not None: # file path in good shape
            if parts[3] == "nl":
                lang2 = "en"
            else:
                lang2 = "nl"

            return ShareStatsFilename.create(self.base_directory,
                                             parts[0], parts[1], parts[2], lang2)
        else:
            return None




def _get_rmd_files_second_level(folder):
    """returns list with Rmd files at the second levels that has the same
    name as the folder. Otherwise first rmd found is return."""

    lst = []
    for name in os.listdir(folder):
        fld = path.join(folder, name)
        if path.isdir(fld):
            good_fl_name = path.join(fld, name+".Rmd")
            if path.isfile(good_fl_name):
                lst.append(good_fl_name)
            else:
                # search for rmd file
                for fl_name in map(lambda x: path.join(fld, x), os.listdir(fld)):
                    if fl_name.lower().endswith(".rmd"):
                        # best guess
                        lst.append(fl_name)
                        break

    return sorted(lst)


def rmd_file_list_bilingual(folder):
    lst =  _get_rmd_files_second_level(folder)

    rtn = []
    # check for matching languages
    while len(lst)>0:
        first = ShareStatsFilename(lst.pop(0))
        second = first.get_other_language()

        while True: # remove all instance of second in lst
            try:
                lst.remove(second.path)
            except:
                break

        if second is not None:
            if path.isfile(second.path):
                if second.get_language() == "nl":
                    second, first = first, second #swap
            else:
                second = None

        rtn.append((first, second))

    return sorted(rtn, key=bilinguar_list_name)

def bilinguar_list_name(bilingual_file_list_entry):
    """bilingual_file_list_entry: tuple of two entries"""

    try:
        name = bilingual_file_list_entry[0].stats_share_name
    except:
        return ""
    if len(name) == 0:
        name = bilingual_file_list_entry[0].filename

    if bilingual_file_list_entry[1] is not None:
            name = name + " [BL]"

    return name

