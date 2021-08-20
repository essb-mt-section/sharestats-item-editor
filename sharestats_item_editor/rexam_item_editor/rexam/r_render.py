import os
from .. import APPNAME, misc

try:
    import rpy2.robjects as robjects
    import webbrowser
except:
    robjects = None

RPY2INSTALLED = robjects is not None


class RRender(object):

    HTML_FILE_NAME = "html-test"

    def __init__(self):
        self.html_dir = misc.get_temp_dir(
                    APPNAME.replace(" ","_").lower(), make_dir=True)

        r_code = '''library(exams)
        rmd_to_html <- function(filename) {
                exams2html(filename, quiet=TRUE, ''' + \
                 'dir="{}",'.format(self.html_dir) + \
                 'encoding = "utf8", template = "plain8", ' + \
                 'name="{}"'.format(RRender.HTML_FILE_NAME) + ")}\n"

        if robjects is not None:
            try:
                robjects.r(r_code)
                self.r_init_error = None
            except Exception as error:
                self.r_init_error = error
        else:
            self.r_init_error = "rpy2 is not installed."

    def rmd_to_html(self, file):
        """:return error text or None, if conversion succeeded"""
        if self.r_init_error is not None:
            return self.r_init_error
        r_func = robjects.r['rmd_to_html']
        try:
            r_func(file)
            return None
        except Exception as error:
            return error

    def get_html_file(self):
        return os.path.join(self.html_dir,
                            RRender.HTML_FILE_NAME + "1.html")

    def open_html(self, new=0):
        fl = self.get_html_file()
        if os.path.isfile(fl):
            webbrowser.open(fl, new=new)