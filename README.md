# ShareStats Item Editor

**Editor and validator for Rexam items in the ShareStats project**

Feature overview

* Takes into account the conventions of the [ShareStats Project](https://github.com/ShareStats) 
    * violation checks of file and folder naming and required meta-information 
    * required subfolder structure
    * joining bilingual items in the database (Dutch, English)
* Convenience functions for item editing
    * support for generating and naming new items
    * auto-fix function for some violations of the conventions and *R*  
      markdown syntax
    * multiple choice items: correct answers can be indicated with an `#` 
      (instead of `*`). `exsolution` will be set automatically.
* R markdown rendering check (experimental, requires *R*)


*Released under the MIT License*

Oliver Lindemann, Erasmus University Rotterdam, NL


![screenshot](https://raw.githubusercontent.com/essb-mt-section/sharestats-item-editor/main/picts/screenshot.png)

---

## Installation 

### Python / Pip

Users familiar with Python are suggested to install `python3`  and use `pip`.

```
python3 -m pip install -U sharestats-item-editor
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

If you used the Python installation, install the 
Python-package `rpy2` (`pip install rpy2`). 

Windows user find two executable 
files for *StatsShare-Item-Editor*, one with and one without *R* rendering 
support. *StatsShare-Item-Editor* with rendering does not work on computers 
without a
*R* installation.




---
**Bugs**: Please [submit](https://github.com/essb-mt-section/sharestats-item-editor/issues/new)
any bug you encounter to the Github issue tracker.
