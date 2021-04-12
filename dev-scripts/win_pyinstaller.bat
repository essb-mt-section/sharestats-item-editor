python -m virtualenv venv

.\venv\Scripts\pip.exe install pyinstaller
.\venv\Scripts\pip.exe install sharestats-item-editor
.\venv\Scripts\pyinstaller.exe --onefile -w --icon=picts\ESSB_logo.ico sharestats_item_editor.py
