import types

class Issue(object):
    # issues from the validations

    def __init__(self, label, description, fix_function=None):
        self.label = label
        self.description = description
        if isinstance(fix_function, (types.FunctionType, types.MethodType)):
            self.fix_fnc = fix_function
        else:
            self.fix_fnc = None

    def fix(self):
        if self.fix_fnc is not None:
            return self.fix_fnc()
        else:
            return False