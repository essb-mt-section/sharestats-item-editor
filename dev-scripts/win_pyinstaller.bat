python -m virtualenv venv

.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\pip.exe install pyinstaller
.\venv\Scripts\pyinstaller.exe --onefile -w --icon=picts\ESSB_logo.ico email_feedback_spss_exam.py