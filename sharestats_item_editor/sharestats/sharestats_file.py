from sharestats_item_editor.rexam.files import RmdFile
#TODO redundent file

class ShareStatsFile(RmdFile):

    @staticmethod
    def create(base_directory, university, topic, counter, language):
        try:
            cnt_str = "{0:0=3d}".format(counter)
        except:
            cnt_str = "{}".format(counter)

        name = "{}-{}-{}-{}".format(university.lower(), topic.lower(), cnt_str,
                                    language.lower())
        return ShareStatsFile(RmdFile.make_path(base_directory, name))

    def get_ss_name_parts(self):
        """None, if filename/path is not in good shape or returns a list of the
         filename parts [University, Topic, Count, Language]
        """

        rtn = self.name.split("-")
        if len(rtn) != 4:
            return None
        else:
            try:
                rtn[2] = int(rtn[2])
            except:
                pass
            return rtn

    def is_good_name(self):
        x = self.name.split("-")
        if len(x) != 4:
            return False
        else:
            try:
                int(x[2]) # is not a number
                return True
            except:
                return False