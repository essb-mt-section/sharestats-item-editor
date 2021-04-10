python -m virtualenv venv

.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\pip.exe install --index-url https://test.pypi.org/simple/ sharestats-item-editor
.\venv\Scripts\pyinstaller.exe --onefile -w --icon=picts\ESSB_logo.ico sharestats_item_editor.py
