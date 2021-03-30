from os  import path as _path

APPNAME = "ShareStats Item Editor"
_LIB_DIR = _path.dirname(__file__)

EXTYPES = {"schoice": "Multiple choice",
           "mchoice": "Multiple answer",
           "num": "Fill in the blank numbers",
           "string": "Fill in the blank text/essay",
           "cloze": "Combinations"}

TEMPLATES = {"schoice":
                 _path.join(_LIB_DIR, "templates/TemplateMultipleChoice.Rmd"),
           "mchoice":
                 _path.join(_LIB_DIR, "templates/TemplateMultipleAnswer.Rmd"),
           "num":
                 _path.join(_LIB_DIR, "templates/TemplateBlankNumber.Rmd"),
           "string":
                 _path.join(_LIB_DIR, "templates/TemplateBlankTextEssay.Rmd"),
           "cloze":
                 _path.join(_LIB_DIR, "templates/TemplateBlankCombination.Rmd")}


