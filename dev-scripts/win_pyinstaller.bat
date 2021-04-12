python -m virtualenv venv

.\venv\Scripts\pip.exe install pyinstaller
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\pyinstaller.exe --onefile -w --icon=picts\ESSB_logo.ico sharestats-item-editor.py
