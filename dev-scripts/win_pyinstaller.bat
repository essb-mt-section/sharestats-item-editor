python -m virtualenv venv

.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\pip.exe install sharestats_item_editor

.\venv\Scripts\pip.exe install pyinstaller
.\venv\Scripts\pyinstaller.exe --onefile -w --icon=picts\ESSB_logo.ico sharestats-item-editor.py
% rename exe--> without rendering

.\venv\Scripts\pip.exe install rpy2
.\venv\Scripts\pyinstaller.exe --onefile -w --icon=picts\ESSB_logo.ico sharestats-item-editor.py
% rename exe--> with rendering
