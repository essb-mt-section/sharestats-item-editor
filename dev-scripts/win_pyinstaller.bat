% download source

python -m virtualenv venv

.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\python sharestats-item-editor.py

.\venv\Scripts\pip.exe install pyinstaller
.\venv\Scripts\pyinstaller.exe --onefile -w --icon=picts\ESSB_logo.ico sharestats-item-editor.py --add-data "sharestats_item_editor\rexam_item_editor\gui\essb.png;sharestats_item_editor\rexam_item_editor\gui" --add-data "sharestats_item_editor\templates;sharestats_item_editor\templates" --add-data "sharestats_item_editor\taxonomy.json;sharestats_item_editor"

% save exe (at another location or upload)
% delete build folder

.\venv\Scripts\pip.exe install rpy2

% make another exe (see cmd above) 
% rename exe--> with rendering
