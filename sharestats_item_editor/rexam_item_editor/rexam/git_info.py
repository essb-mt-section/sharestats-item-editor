from os import path
import yaml

class GitInfo(object):

    def __init__(self, folder):
        self._git = path.join(folder, ".git")
        try:
            with open(path.join(self._git, "HEAD"), "r") as fl:
                self._head = yaml.safe_load(fl)
        except:
            self._head = None

    @property
    def is_repository(self):
        return self._head is not None

    @property
    def folder(self):
        return self._git[:-4]


    @property
    def branch(self):
        if self._head is None:
            return ""

        elif isinstance(self._head, dict):
            return self._head['ref'].split(path.sep)[-1]
        else:
            return self._head.strip()

    @property
    def head(self):
        if self._head is None:
            return ""

        elif isinstance(self._head, dict):
            fl = path.join(self._git, self._head['ref'])
            with open(fl, "r") as fl:
                return fl.read().strip()
        else:
            return self._head.strip()
