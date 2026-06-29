@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Building ClaudeLight.exe...
pyinstaller --onefile --windowed --name ClaudeLight --icon=resources/icon.ico main.py

echo Done. Output: dist\ClaudeLight.exe
