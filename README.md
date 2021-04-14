# ShareStats Item Editor

**Editor and validator for Rexam items in the ShareStats project**

*Released under the MIT License*

Oliver Lindemann, Erasmus University Rotterdam, NL


![screenshot](https://raw.githubusercontent.com/essb-mt-section/sharestats-item-editor/main/picts/screenshot.png)

---

## Installation 

### Python / Pip

Users familiar with Python are suggested to install `python3`  and use `pip`.

```
python3 -m pip install sharestats-item-editor
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

Optional requirement:
* rpy2 >=3.4


### Windows

Windows user may run *StatsShare-Item-Editor* without installing Python. 
Download the 
latest executable file, `sharestats_item_editor.exe`, via the
[release website](https://github.com/essb-mt-section/sharestats-item-editor/releases/latest)
and execute it. Using the executable file instead of installing the appliaction 
via `pip` results in a slowly launching application.

Note, depending on your security setting, you may receive a security alert 
from Windows defender, because the executable is not registered Windows 
application. 

## Rendering Rmd File

To render Rmd files directly via the *StatsShare-Item-Editor*, you need 
a functioning 
installation of *R* including the *R*-package `exams`. 

If you used the Python installation , just install the 
Python-package `rpy2` (`pip install rpy2`). Windows user find two executable 
files for *StatsShare-Item-Editor*, with and without *R* rendering support. On 
computers without *R* the executable for *StatsShare-Item-Editor* with 
rendering support does not run. 



---

See also [ShareStats Project](https://github.com/ShareStats)

---
**Bugs**: Please [submit](https://github.com/essb-mt-section/sharestats-item-editor/issues/new)
any bug you encounter to the Github issue tracker.
