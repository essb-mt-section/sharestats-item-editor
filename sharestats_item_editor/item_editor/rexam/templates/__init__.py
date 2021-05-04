from os  import path as _path

_fldir = _path.dirname(__file__)

FILES = {"schoice": _path.join(_fldir, "TemplateMultipleChoice.Rmd"),
        "mchoice": _path.join(_fldir, "TemplateMultipleAnswer.Rmd"),
        "num": _path.join(_fldir, "TemplateBlankNumber.Rmd"),
        "string": _path.join(_fldir, "TemplateBlankTextEssay.Rmd"),
        "cloze": _path.join(_fldir, "TemplateBlankCombination.Rmd")}



