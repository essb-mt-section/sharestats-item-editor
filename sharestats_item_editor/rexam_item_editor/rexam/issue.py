import types

class Issue(object):
    # issues from the validations

    def __init__(self, label, description, fix_function=None,
                 fix_requires_gui_reset=False):
        self.label = label
        self.description = description
        self.fix_requires_gui_reset = fix_requires_gui_reset
        if isinstance(fix_function, (types.FunctionType, types.MethodType)):
            self.fix_fnc = fix_function
        else:
            self.fix_fnc = None

    def has_fix_function(self):
        return self.fix_fnc is not None

    def fix(self):
        if self.fix_fnc is not None:
            return self.fix_fnc()
        else:
            return False
