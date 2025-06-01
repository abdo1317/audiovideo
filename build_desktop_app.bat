@echo off
echo ===================================
echo Building AudVed Desktop Application
echo ===================================
echo.

echo Installing required packages...
pip install -r requirements.txt
pip install cx_Freeze

echo.
echo Building desktop application...
python setup.py build

echo.
echo Creating installer directory...
mkdir installer

echo.
echo To create an installer, please install Inno Setup from:
echo https://jrsoftware.org/isdl.php
echo.
echo After installation, run the following command:
echo "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" inno_setup.iss
echo.
echo Or open inno_setup.iss with Inno Setup Compiler and build the installer.

echo.
echo Build process completed!
echo The executable can be found in the build directory.
echo.

pause