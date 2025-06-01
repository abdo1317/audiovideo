@echo off
echo ===================================
echo Building AudVed Desktop Application with PyInstaller
echo ===================================
echo.

echo Installing required packages...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Building desktop application...
python -m PyInstaller --name="AudVed" --windowed --add-data="bari_logo.svg;." main.py

echo.
echo Build process completed!
echo The executable can be found in the dist/AudVed directory.
echo.

echo To create an installer, please install Inno Setup from:
echo https://jrsoftware.org/isdl.php
echo.
echo After installation, run the following command:
echo "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" inno_setup.iss
echo.

pause