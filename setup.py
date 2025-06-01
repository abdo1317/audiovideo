import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
builds_dir = 'build/'
build_exe_options = {
    "packages": [
        "os", "sys", "time", "threading", "datetime", "PyQt5", "pyaudio", 
        "soundfile", "numpy", "cv2", "PIL", "yt_dlp", "mutagen", "speech_recognition"
    ],
    "include_files": [
        "bari_logo.svg",  # Include the logo file
    ],
    "build_exe": builds_dir,
    "excludes": ["PyQt5.QtQml"],  # Exclude QML to avoid QmlImportsPath error
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="AudVed",
    version="1.0",
    description="Audio & Video Recorder and Downloader",
    options={"build_exe": build_exe_options},
    executables=[Executable(
        "main.py", 
        base=base,
        target_name="AudVed.exe",
        icon="bari_logo.svg",  # Set the application icon
    )]
)