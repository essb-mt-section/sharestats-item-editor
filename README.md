# ShareStats Item Editor

**Editor and validator for Rexam items in the ShareStats project**

*Released under the MIT License*

Oliver Lindemann, Erasmus University Rotterdam, NL


![screenshot](picts/screenshot.png)

---

## Installation 

### Python / Pip

Users familiar with Python are suggested to install `python3`  and use `pip` 
for installation.

```
python3 -m pip install pysimplegui
python3 -m pip install --index-url https://test.pypi.org/simple/ sharestats-item-editor
```

To run ShareStatsItemEditor call

```
sharestats-item-editor
```
or
```
python3 -m sharestats_item_editor
```


**Dependencies:** Python 3.5+ and the following libraries 
(see [requirements.txt](requirements.txt)):
* PySimpleGUI
* appdirs

### Windows

Windows user may run the application without installing Python. Download the 
latest executable file, `sharestats_item_editor.exe`, via the
[release website](https://github.com/essb-mt-section/sharestats-item-editor/releases/latest)
and execute it. Using the executable file instead of installing the appliaction 
via `pip` results in a slowly launching application.

Note, depending on your security setting, you may receive a security alert 
from Windows defender, because the executable is not registered Windows 
application. 

---

See also [ShareStats Project](https://github.com/ShareStats)

---
**Bugs**: Please [submit](https://github.com/essb-mt-section/sharestats-item-editor/issues/new)
any bug you encounter to the Github issue tracker.
