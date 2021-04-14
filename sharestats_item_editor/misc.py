import os
import tempfile

def subdict(d, nested_keys=None):
    """:return the dict nested hierarchically indicated by nested_keys
    or None if key list is incorrect
    :param nested_keys list of keys or a single keys

    """
    if not isinstance(nested_keys, (tuple, list)):
        nested_keys = [nested_keys]
    for k in nested_keys:
        try:
            d = d[k]
        except:
            return {}
    return d

def splitstrip(text, sep):
    return list(map(lambda x: x.strip(), text.split(sep)))

def yesno(bool):
    if bool:
        return "Yes"
    else:
        return "No"


def get_temp_dir(appname, make_dir=True):
    # creates and returns a temp folder

    tmpdir = tempfile.gettempdir()
    tmpdir = os.path.join(tmpdir, appname)
    if make_dir:
        try:
            os.mkdir(tmpdir)
        except:
            pass

    return tmpdir

def remove_all(str_list, element, ignore_cases=False):
    """removes all occurrences of element from string list and ignores
    optionally letter cases"""

    if ignore_cases:
        new_list = [e for e in str_list \
                    if str(e).lower() != str(element).lower()]
    else:
        new_list = [e for e in str_list if e != element]

    if len(str_list) == len(new_list): # no items anymore
        return new_list
    else:
        return remove_all(new_list, element, ignore_cases)


