import os
import tempfile
import re


def replace_list_element(lst, source_idx, target_idx):
    """replaces an element in a list"""
    if source_idx < len(lst) and target_idx<len(
    lst):
        tmp = lst.pop(source_idx)
        return lst[:target_idx] + [tmp] + lst[target_idx:]
    else:
        return []

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

class CaseInsensitiveStringList(object):
    """String list that handles string search case insensitive"""

    def __init__(self, str_list=()):
        self._str_list = list(str_list)
        self._str_lower = [x.lower() for x in self._str_list]

    def __len__(self):
        return len(self._str_list)

    def append(self, new_string):
        self._str_list.append(new_string)
        self._str_lower.append(new_string.lower())

    def pop(self, index=-1):
        self._str_lower.pop(index)
        return self._str_list.pop(index)

    def remove(self, element):
        """removes element and returns it, raises exception in not included"""
        element = str(element).lower()
        idx = self._str_lower.index(element)
        self._str_lower.pop(idx)
        return self._str_list.pop(idx)

    def remove_all(self, element):
        element = str(element).lower()
        while True:
            try:
                idx = self._str_lower.index(element)
            except:
                break

            self._str_list.pop(idx)
            self._str_lower.pop(idx)

    def __contains__(self, item):
        return str(item).lower() in self._str_lower

    def get(self):
        return self._str_list

def remove_all(str_list, element, ignore_cases=False):
    """removes all occurrences of element from string list and ignores
    optionally letter cases"""

    if ignore_cases:
        return [e for e in str_list \
                    if str(e).lower() != str(element).lower()]
    else:
        return [e for e in str_list if e != element]

def extract_parameter(txt):
    # extract parameter for text line

    m = re.match(r"\s*\w+[\[\]\w]+:", txt)
    if m is not None:
        return {txt[:m.end()-1].strip(): txt[m.end():].strip()}
    return None

def iter_list(data):
    """Generates iterator over the data.
    If None, iterator over empty list. If data is not a list or a tuple,
    iterator over list with one one element [data]
    """
    if data is None:
        return iter([])
    elif isinstance(data, (list, tuple)):
        return iter(data)
    else:
        return iter([data])

