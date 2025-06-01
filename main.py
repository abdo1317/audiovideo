import sys
import os
import time
import threading
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QFileDialog, QTabWidget,
                             QLineEdit, QProgressBar, QMessageBox, QRadioButton, QButtonGroup,
                             QGroupBox, QGridLayout, QSpacerItem, QSizePolicy, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl, QSize, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QFont
import pyaudio
import soundfile as sf
import numpy as np
import cv2
from PIL import ImageGrab
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
import speech_recognition as sr

# Language dictionaries
EN = {
    "title": "AudVed - Audio & Video Recorder",
    "audio_tab": "Audio Recording",
    "video_tab": "Screen Recording",
    "download_tab": "Download Media",
    "start_recording": "Start Recording",
    "stop_recording": "Stop Recording",
    "select_folder": "Select Folder",
    "recording_status": "Status: Ready",
    "recording": "Status: Recording...",
    "stopped": "Status: Stopped",
    "saved": "File saved to: {}",
    "download_url": "Enter URL:",
    "download_button": "Download",
    "download_audio": "Audio",
    "download_video": "Video",
    "downloading": "Downloading...",
    "download_complete": "Download Complete",
    "download_error": "Download Error",
    "recording_error": "Recording Error",
    "error": "Error",
    "language": "Language",
    "file_info": "File Information",
    "duration": "Duration: {}",
    "size": "Size: {} MB",
    "notification": "Notification",
    "task_complete": "Task Completed",
    "select_output_folder": "Select Output Folder",
    "transcribe_audio": "Transcribe Audio",
    "transcribing": "Transcribing audio...",
    "transcription_complete": "Transcription Complete",
    "transcription_error": "Transcription Error",
    "transcription_result": "Transcription Result",
    "record_with_audio": "Record with Audio"
}

AR = {
    "title": "أودفيد - مسجل الصوت والفيديو",
    "audio_tab": "تسجيل الصوت",
    "video_tab": "تسجيل الشاشة",
    "download_tab": "تحميل الوسائط",
    "start_recording": "بدء التسجيل",
    "stop_recording": "إيقاف التسجيل",
    "select_folder": "اختيار المجلد",
    "recording_status": "الحالة: جاهز",
    "recording": "الحالة: جاري التسجيل...",
    "stopped": "الحالة: متوقف",
    "saved": "تم حفظ الملف في: {}",
    "download_url": "أدخل الرابط:",
    "download_button": "تحميل",
    "download_audio": "صوت",
    "download_video": "فيديو",
    "downloading": "جاري التحميل...",
    "download_complete": "اكتمل التحميل",
    "download_error": "خطأ في التحميل",
    "recording_error": "خطأ في التسجيل",
    "error": "خطأ",
    "language": "اللغة",
    "file_info": "معلومات الملف",
    "duration": "المدة: {}",
    "size": "الحجم: {} ميجابايت",
    "notification": "إشعار",
    "task_complete": "اكتملت المهمة",
    "select_output_folder": "اختر مجلد الإخراج",
    "transcribe_audio": "تحويل الصوت إلى نص",
    "transcribing": "جاري تحويل الصوت إلى نص...",
    "transcription_complete": "اكتمل تحويل الصوت إلى نص",
    "transcription_error": "خطأ في تحويل الصوت إلى نص",
    "transcription_result": "نتيجة تحويل الصوت إلى نص",
    "record_with_audio": "تسجيل مع الصوت"
}

IT = {
    "title": "AudVed - Registratore Audio e Video",
    "audio_tab": "Registrazione Audio",
    "video_tab": "Registrazione Schermo",
    "download_tab": "Scarica Media",
    "start_recording": "Avvia Registrazione",
    "stop_recording": "Ferma Registrazione",
    "select_folder": "Seleziona Cartella",
    "recording_status": "Stato: Pronto",
    "recording": "Stato: Registrazione in corso...",
    "stopped": "Stato: Fermato",
    "saved": "File salvato in: {}",
    "download_url": "Inserisci URL:",
    "download_button": "Scarica",
    "download_audio": "Audio",
    "download_video": "Video",
    "downloading": "Scaricamento in corso...",
    "download_complete": "Scaricamento Completato",
    "download_error": "Errore di Scaricamento",
    "recording_error": "Errore di Registrazione",
    "error": "Errore",
    "language": "Lingua",
    "file_info": "Informazioni sul File",
    "duration": "Durata: {}",
    "size": "Dimensione: {} MB",
    "notification": "Notifica",
    "task_complete": "Attività Completata",
    "select_output_folder": "Seleziona Cartella di Output",
    "transcribe_audio": "Trascrivi Audio",
    "transcribing": "Trascrizione audio in corso...",
    "transcription_complete": "Trascrizione Completata",
    "transcription_error": "Errore di Trascrizione",
    "transcription_result": "Risultato della Trascrizione",
    "record_with_audio": "Registra con Audio"
}


class AudioRecorder(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    
    def __init__(self, save_path):
        super().__init__()
        self.save_path = save_path
        self.is_recording = False
        self.audio_frames = []
        
    def run(self):
        self.is_recording = True
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                           channels=1,  # Changed from 2 to 1 for mono recording
                           rate=44100,
                           input=True,
                           frames_per_buffer=1024)
        
        self.audio_frames = []
        
        while self.is_recording:
            data = stream.read(1024)
            self.audio_frames.append(data)
            
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save the recorded audio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.save_path, f"audio_{timestamp}.wav")
        
        wf = sf.SoundFile(filename, mode='w', samplerate=44100,
                         channels=1, subtype='PCM_16')  # Changed from 2 to 1 for mono recording
        
        # Convert audio frames to numpy array
        audio_data = b''.join(self.audio_frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        wf.write(audio_array)
        wf.close()
        
        self.finished_signal.emit(filename)
        
    def stop(self):
        self.is_recording = False


class ScreenRecorder(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, save_path, record_with_audio=True):
        super().__init__()
        self.save_path = save_path
        self.is_recording = False
        self.process = None
        self.output_file = None
        self.record_with_audio = record_with_audio
        
    def run(self):
        try:
            self.is_recording = True
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_file = os.path.join(self.save_path, f"screen_{timestamp}.mp4")
            
            # Get screen size
            screen = ImageGrab.grab()
            width, height = screen.size
            
            # Use FFmpeg to capture screen with or without audio
            import subprocess
            
            if self.record_with_audio:
                self.update_signal.emit("Recording screen with audio...")
            else:
                self.update_signal.emit("Recording screen without audio...")
            
            # Command to capture screen with or without audio
            if os.name == 'nt':  # Windows
                if self.record_with_audio:
                    cmd = [
                        'ffmpeg',
                        '-f', 'gdigrab',
                        '-framerate', '30',
                        '-i', 'desktop',
                        '-f', 'dshow',
                        '-i', '@device_cm_{33D9A762-90C8-11D0-BD43-00A0C911CE86}\wave_{34691939-1F6D-40B2-A5A6-10AAD183BEB7}',  # Default microphone
                        '-c:v', 'libx264',
                        '-r', '30',
                        '-preset', 'medium',
                        '-crf', '18',
                        '-b:v', '4M',
                        '-c:a', 'aac',
                        '-strict', 'experimental',
                        '-b:a', '192k',
                        self.output_file
                    ]
                else:
                    cmd = [
                        'ffmpeg',
                        '-f', 'gdigrab',
                        '-framerate', '30',
                        '-i', 'desktop',
                        '-c:v', 'libx264',
                        '-r', '30',
                        '-preset', 'medium',
                        '-crf', '18',
                        '-b:v', '4M',
                        self.output_file
                    ]
            else:  # Linux/Mac
                if self.record_with_audio:
                    cmd = [
                        'ffmpeg',
                        '-f', 'x11grab',
                        '-framerate', '30',
                        '-i', ':0.0',
                        '-f', 'pulse',
                        '-i', 'default',
                        '-c:v', 'libx264',
                        '-r', '30',
                        '-preset', 'medium',
                        '-crf', '18',
                        '-b:v', '4M',
                        '-c:a', 'aac',
                        '-strict', 'experimental',
                        '-b:a', '192k',
                        self.output_file
                    ]
                else:
                    cmd = [
                        'ffmpeg',
                        '-f', 'x11grab',
                        '-framerate', '30',
                        '-i', ':0.0',
                        '-c:v', 'libx264',
                        '-r', '30',
                        '-preset', 'medium',
                        '-crf', '18',
                        '-b:v', '4M',
                        self.output_file
                    ]
            
            # Run the command
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait until recording is stopped
            while self.is_recording and self.process.poll() is None:
                time.sleep(0.1)
            
            # If recording was stopped by user
            if self.is_recording and self.process.poll() is not None:
                # Process ended unexpectedly
                stdout, stderr = self.process.communicate()
                error_msg = stderr.decode('utf-8', errors='ignore')
                self.error_signal.emit(f"Error during recording: {error_msg}")
                self.is_recording = False
                return
            
            # If we get here, recording was stopped by user
            if self.process.poll() is None:
                # Send 'q' to stop ffmpeg
                self.process.terminate()
                self.process.wait()
            
            self.finished_signal.emit(self.output_file)
            
        except Exception as e:
            self.error_signal.emit(f"Error during recording: {str(e)}")
            self.is_recording = False
            if hasattr(self, 'process') and self.process and self.process.poll() is None:
                self.process.terminate()
        
    def stop(self):
        self.is_recording = False


class AudioTranscriber(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, audio_file):
        super().__init__()
        self.audio_file = audio_file
        
    def run(self):
        try:
            self.update_signal.emit("Transcribing audio...")
            
            # Initialize recognizer
            recognizer = sr.Recognizer()
            
            # Load audio file
            with sr.AudioFile(self.audio_file) as source:
                # Record audio data
                audio_data = recognizer.record(source)
                
                # Recognize speech using Google Speech Recognition
                text = recognizer.recognize_google(audio_data)
                
                self.finished_signal.emit(text)
                
        except sr.UnknownValueError:
            self.error_signal.emit("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            self.error_signal.emit(f"Could not request results from Speech Recognition service; {e}")
        except Exception as e:
            self.error_signal.emit(f"Error during transcription: {str(e)}")



class MediaDownloader(QThread):
    update_signal = pyqtSignal(str, int)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, url, save_path, download_type):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.download_type = download_type  # 'audio' or 'video'
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                # Try to get more accurate progress information
                if d.get('total_bytes'):
                    percentage = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif d.get('total_bytes_estimate'):
                    percentage = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                else:
                    # Fall back to string percentage if available
                    p = d.get('_percent_str', '0%')
                    p = p.replace('%', '')
                    percentage = float(p)
                
                # Ensure we're sending integer updates
                self.update_signal.emit('downloading', int(percentage))
            except Exception as e:
                # If we can't calculate percentage, at least show activity
                self.update_signal.emit('downloading', -1)
        elif d['status'] == 'finished':
            self.update_signal.emit('processing', 100)
            
    def run(self):
        try:
            ydl_opts = {
                'progress_hooks': [self.progress_hook],
                'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
                'no_check_certificate': True,
                'ignoreerrors': True,
            }
            
            if self.download_type == 'audio':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    # Skip post-processing if FFmpeg is not available
                    'postprocessor_args': ['-update_interval', '1'],
                    'prefer_ffmpeg': False  # Don't require FFmpeg
                })
            else:  # video
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }],
                    'merge_output_format': 'mp4',
                })
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(self.url, download=True)
                    if info is None:
                        self.error_signal.emit("Could not download the video. Please check the URL.")
                        return
                        
                    filename = ydl.prepare_filename(info)
                    
                    # Handle postprocessed files (for audio)
                    if self.download_type == 'audio':
                        base, _ = os.path.splitext(filename)
                        possible_filename = f"{base}.mp3"
                        if os.path.exists(possible_filename):
                            filename = possible_filename
                        else:
                            # If FFmpeg failed, we'll still have the original file
                            self.update_signal.emit('processing', 100)
                            
                    self.finished_signal.emit(filename)
                except Exception as e:
                    self.error_signal.emit(f"Download error: {str(e)}")
            
        except Exception as e:
            self.error_signal.emit(f"Error: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Default settings
        self.current_language = "EN"
        self.texts = EN
        self.save_path = os.path.expanduser("~/Downloads")
        
        # Define color scheme
        self.colors = {
            "primary": "#3498db",     # Blue
            "secondary": "#2ecc71",  # Green
            "accent": "#e74c3c",     # Red
            "background": "#f5f5f5", # Light gray
            "text": "#2c3e50",       # Dark blue/gray
            "light_text": "#7f8c8d"  # Gray
        }
        
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle(self.texts["title"])
        self.setMinimumSize(800, 600)
        
        # Set application icon
        # Try to use ICO file first, fall back to SVG if ICO is not available
        if os.path.exists("bari_logo.ico"):
            app_icon = QIcon("bari_logo.ico")
        else:
            app_icon = QIcon("bari_logo.svg")
        self.setWindowIcon(app_icon)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create language selection with improved styling
        lang_layout = QHBoxLayout()
        lang_label = QLabel(self.texts["language"] + ": ")
        lang_label.setStyleSheet(f"color: {self.colors['text']}; font-weight: bold;")
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "العربية", "Italiano"])
        self.lang_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {self.colors['primary']};
                border-radius: 4px;
                padding: 5px 10px;
                background-color: white;
                color: {self.colors['text']};
                min-width: 120px;
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {self.colors['primary']};
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }}
            
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            
            QComboBox QAbstractItemView {{
                border: 1px solid {self.colors['primary']};
                selection-background-color: {self.colors['primary']};
                selection-color: white;
                background-color: white;
                color: {self.colors['text']};
            }}
        """)
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        
        lang_layout.addStretch()
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        main_layout.addLayout(lang_layout)
        
        # Apply stylesheet
        self.apply_stylesheet()
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.audio_tab = QWidget()
        self.video_tab = QWidget()
        self.download_tab = QWidget()
        
        self.setup_audio_tab()
        self.setup_video_tab()
        self.setup_download_tab()
        
        # Add tabs to widget
        self.tabs.addTab(self.audio_tab, self.texts["audio_tab"])
        self.tabs.addTab(self.video_tab, self.texts["video_tab"])
        self.tabs.addTab(self.download_tab, self.texts["download_tab"])
        
        main_layout.addWidget(self.tabs)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Initialize variables
        self.audio_recorder = None
        self.screen_recorder = None
        self.media_downloader = None
        
    def setup_audio_tab(self):
        layout = QVBoxLayout(self.audio_tab)
        
        # Folder selection with improved styling
        folder_layout = QHBoxLayout()
        folder_label = QLabel(self.texts["select_output_folder"] + ": ")
        self.audio_folder_path = QLineEdit(self.save_path)
        self.audio_folder_path.setReadOnly(True)
        folder_btn = QPushButton(self.texts["select_folder"])
        folder_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['text']};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #34495e;
            }}
        """)
        folder_btn.clicked.connect(lambda: self.select_folder(self.audio_folder_path))
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.audio_folder_path)
        folder_layout.addWidget(folder_btn)
        
        layout.addLayout(folder_layout)
        
        # Control buttons with improved styling
        btn_layout = QHBoxLayout()
        self.audio_start_btn = QPushButton(self.texts["start_recording"])
        self.audio_start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['secondary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #27ae60;
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
                color: #ecf0f1;
            }}
        """)
        
        self.audio_stop_btn = QPushButton(self.texts["stop_recording"])
        self.audio_stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
                color: #ecf0f1;
            }}
        """)
        self.audio_stop_btn.setEnabled(False)
        
        self.audio_start_btn.clicked.connect(self.start_audio_recording)
        self.audio_stop_btn.clicked.connect(self.stop_audio_recording)
        
        btn_layout.addWidget(self.audio_start_btn)
        btn_layout.addWidget(self.audio_stop_btn)
        
        layout.addLayout(btn_layout)
        
        # Status
        self.audio_status = QLabel(self.texts["recording_status"])
        layout.addWidget(self.audio_status)
        
        # File info
        self.audio_info_group = QGroupBox(self.texts["file_info"])
        self.audio_info_group.setVisible(False)
        info_layout = QVBoxLayout(self.audio_info_group)
        
        self.audio_file_path = QLabel("")
        self.audio_duration = QLabel("")
        self.audio_size = QLabel("")
        
        info_layout.addWidget(self.audio_file_path)
        info_layout.addWidget(self.audio_duration)
        info_layout.addWidget(self.audio_size)
        
        # Transcribe button
        self.transcribe_btn = QPushButton(self.texts["transcribe_audio"])
        self.transcribe_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['primary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
                color: #ecf0f1;
            }}
        """)
        self.transcribe_btn.setEnabled(False)
        self.transcribe_btn.clicked.connect(self.transcribe_audio)
        info_layout.addWidget(self.transcribe_btn)
        
        # Transcription result
        self.transcription_group = QGroupBox(self.texts["transcription_result"])
        self.transcription_group.setVisible(False)
        transcription_layout = QVBoxLayout(self.transcription_group)
        
        self.transcription_text = QTextEdit()
        self.transcription_text.setReadOnly(True)
        self.transcription_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: white;
                color: {self.colors['text']};
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        transcription_layout.addWidget(self.transcription_text)
        
        layout.addWidget(self.audio_info_group)
        layout.addWidget(self.transcription_group)
        layout.addStretch()
        
    def setup_video_tab(self):
        layout = QVBoxLayout(self.video_tab)
        
        # Folder selection
        folder_layout = QHBoxLayout()
        folder_label = QLabel(self.texts["select_output_folder"] + ": ")
        self.video_folder_path = QLineEdit(self.save_path)
        self.video_folder_path.setReadOnly(True)
        folder_btn = QPushButton(self.texts["select_folder"])
        folder_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['text']};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #34495e;
            }}
        """)
        folder_btn.clicked.connect(lambda: self.select_folder(self.video_folder_path))
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.video_folder_path)
        folder_layout.addWidget(folder_btn)
        
        layout.addLayout(folder_layout)
        
        # Audio option
        audio_option_layout = QHBoxLayout()
        self.record_with_audio_checkbox = QRadioButton(self.texts["record_with_audio"])
        self.record_with_audio_checkbox.setChecked(True)  # Default to recording with audio
        self.record_with_audio_checkbox.setStyleSheet(f"""
            QRadioButton {{
                color: {self.colors['text']};
                font-weight: bold;
            }}
            QRadioButton::indicator {{
                width: 15px;
                height: 15px;
            }}
            QRadioButton::indicator:checked {{
                background-color: {self.colors['secondary']};
                border: 2px solid {self.colors['secondary']};
                border-radius: 7px;
            }}
            QRadioButton::indicator:unchecked {{
                border: 2px solid {self.colors['text']};
                border-radius: 7px;
            }}
        """)
        audio_option_layout.addWidget(self.record_with_audio_checkbox)
        audio_option_layout.addStretch()
        
        layout.addLayout(audio_option_layout)
        
        # Control buttons with improved styling
        btn_layout = QHBoxLayout()
        self.video_start_btn = QPushButton(self.texts["start_recording"])
        self.video_start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['secondary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #27ae60;
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
                color: #ecf0f1;
            }}
        """)
        
        self.video_stop_btn = QPushButton(self.texts["stop_recording"])
        self.video_stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
                color: #ecf0f1;
            }}
        """)
        self.video_stop_btn.setEnabled(False)
        
        self.video_start_btn.clicked.connect(self.start_screen_recording)
        self.video_stop_btn.clicked.connect(self.stop_screen_recording)
        
        btn_layout.addWidget(self.video_start_btn)
        btn_layout.addWidget(self.video_stop_btn)
        
        layout.addLayout(btn_layout)
        
        # Status
        self.video_status = QLabel(self.texts["recording_status"])
        layout.addWidget(self.video_status)
        
        # File info
        self.video_info_group = QGroupBox(self.texts["file_info"])
        self.video_info_group.setVisible(False)
        info_layout = QVBoxLayout(self.video_info_group)
        
        self.video_file_path = QLabel("")
        self.video_duration = QLabel("")
        self.video_size = QLabel("")
        
        info_layout.addWidget(self.video_file_path)
        info_layout.addWidget(self.video_duration)
        info_layout.addWidget(self.video_size)
        
        # Transcribe button for video
        self.video_transcribe_btn = QPushButton(self.texts["transcribe_audio"])
        self.video_transcribe_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['primary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
                color: #ecf0f1;
            }}
        """)
        self.video_transcribe_btn.setEnabled(False)
        self.video_transcribe_btn.clicked.connect(self.transcribe_video_audio)
        info_layout.addWidget(self.video_transcribe_btn)
        
        # Video transcription result
        self.video_transcription_group = QGroupBox(self.texts["transcription_result"])
        self.video_transcription_group.setVisible(False)
        video_transcription_layout = QVBoxLayout(self.video_transcription_group)
        
        self.video_transcription_text = QTextEdit()
        self.video_transcription_text.setReadOnly(True)
        self.video_transcription_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: white;
                color: {self.colors['text']};
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        video_transcription_layout.addWidget(self.video_transcription_text)
        
        layout.addWidget(self.video_info_group)
        layout.addWidget(self.video_transcription_group)
        layout.addStretch()
        
    def setup_download_tab(self):
        layout = QVBoxLayout(self.download_tab)
        
        # URL input
        url_layout = QHBoxLayout()
        url_label = QLabel(self.texts["download_url"])
        self.url_input = QLineEdit()
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        
        layout.addLayout(url_layout)
        
        # Download type
        type_layout = QHBoxLayout()
        self.audio_radio = QRadioButton(self.texts["download_audio"])
        self.video_radio = QRadioButton(self.texts["download_video"])
        self.audio_radio.setChecked(True)
        
        type_layout.addWidget(self.audio_radio)
        type_layout.addWidget(self.video_radio)
        
        layout.addLayout(type_layout)
        
        # Folder selection
        folder_layout = QHBoxLayout()
        folder_label = QLabel(self.texts["select_output_folder"] + ": ")
        self.download_folder_path = QLineEdit(self.save_path)
        self.download_folder_path.setReadOnly(True)
        folder_btn = QPushButton(self.texts["select_folder"])
        folder_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['text']};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #34495e;
            }}
        """)
        folder_btn.clicked.connect(lambda: self.select_folder(self.download_folder_path))
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.download_folder_path)
        folder_layout.addWidget(folder_btn)
        
        layout.addLayout(folder_layout)
        
        # Download button with improved styling
        self.download_btn = QPushButton(self.texts["download_button"])
        self.download_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['primary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
                color: #ecf0f1;
            }}
        """)
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)
        
        # Progress bar
        self.download_progress = QProgressBar()
        self.download_progress.setVisible(False)
        layout.addWidget(self.download_progress)
        
        # Status
        self.download_status = QLabel("")
        layout.addWidget(self.download_status)
        
        # File info
        self.download_info_group = QGroupBox(self.texts["file_info"])
        self.download_info_group.setVisible(False)
        info_layout = QVBoxLayout(self.download_info_group)
        
        self.download_file_path = QLabel("")
        self.download_duration = QLabel("")
        self.download_size = QLabel("")
        
        info_layout.addWidget(self.download_file_path)
        info_layout.addWidget(self.download_duration)
        info_layout.addWidget(self.download_size)
        
        layout.addWidget(self.download_info_group)
        layout.addStretch()
        
    def select_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, self.texts["select_output_folder"], 
                                                line_edit.text())
        if folder:
            line_edit.setText(folder)
            
    def change_language(self, index):
        if index == 0:  # English
            self.current_language = "EN"
            self.texts = EN
        elif index == 1:  # Arabic
            self.current_language = "AR"
            self.texts = AR
        else:  # Italian
            self.current_language = "IT"
            self.texts = IT
            
        # Update UI text
        self.update_ui_text()
        
    def update_ui_text(self):
        # Update window title
        self.setWindowTitle(self.texts["title"])
        
        # Update tabs
        self.tabs.setTabText(0, self.texts["audio_tab"])
        self.tabs.setTabText(1, self.texts["video_tab"])
        self.tabs.setTabText(2, self.texts["download_tab"])
        
        # Update audio tab
        self.audio_tab.layout().itemAt(0).layout().itemAt(0).widget().setText(self.texts["select_output_folder"] + ": ")
        self.audio_tab.layout().itemAt(0).layout().itemAt(2).widget().setText(self.texts["select_folder"])
        self.audio_start_btn.setText(self.texts["start_recording"])
        self.audio_stop_btn.setText(self.texts["stop_recording"])
        self.audio_status.setText(self.texts["recording_status"])
        self.audio_info_group.setTitle(self.texts["file_info"])
        
        # Update video tab
        self.video_tab.layout().itemAt(0).layout().itemAt(0).widget().setText(self.texts["select_output_folder"] + ": ")
        self.video_tab.layout().itemAt(0).layout().itemAt(2).widget().setText(self.texts["select_folder"])
        self.video_start_btn.setText(self.texts["start_recording"])
        self.video_stop_btn.setText(self.texts["stop_recording"])
        self.video_status.setText(self.texts["recording_status"])
        self.video_info_group.setTitle(self.texts["file_info"])
        
        # Update download tab
        self.download_tab.layout().itemAt(0).layout().itemAt(0).widget().setText(self.texts["download_url"])
        self.audio_radio.setText(self.texts["download_audio"])
        self.video_radio.setText(self.texts["download_video"])
        self.download_tab.layout().itemAt(2).layout().itemAt(0).widget().setText(self.texts["select_output_folder"] + ": ")
        self.download_tab.layout().itemAt(2).layout().itemAt(2).widget().setText(self.texts["select_folder"])
        self.download_btn.setText(self.texts["download_button"])
        self.download_info_group.setTitle(self.texts["file_info"])
        
        # Reapply stylesheet to ensure consistent styling after language change
        self.apply_stylesheet()
        
    def start_audio_recording(self):
        save_path = self.audio_folder_path.text()
        self.audio_recorder = AudioRecorder(save_path)
        self.audio_recorder.update_signal.connect(self.update_audio_status)
        self.audio_recorder.finished_signal.connect(self.audio_recording_finished)
        self.audio_recorder.start()
        
        self.audio_start_btn.setEnabled(False)
        self.audio_stop_btn.setEnabled(True)
        self.audio_stop_btn.setStyleSheet(f"background-color: {self.colors['accent']};")
        self.audio_status.setText(self.texts["recording"])
        self.audio_info_group.setVisible(False)
        
    def stop_audio_recording(self):
        if self.audio_recorder and self.audio_recorder.is_recording:
            self.audio_recorder.stop()
            self.audio_status.setText(self.texts["stopped"])
            self.audio_stop_btn.setStyleSheet("")  # Reset button style
            
    def update_audio_status(self, status):
        self.audio_status.setText(status)
        
    def audio_recording_finished(self, filename):
        self.audio_start_btn.setEnabled(True)
        self.audio_stop_btn.setEnabled(False)
        self.audio_status.setText(self.texts["saved"].format(filename))
        
        # Show file info
        self.audio_file_path.setText(filename)
        
        try:
            audio = MP3(filename)
            duration = time.strftime('%M:%S', time.gmtime(audio.info.length))
            self.audio_duration.setText(self.texts["duration"].format(duration))
            
            size_mb = os.path.getsize(filename) / (1024 * 1024)
            self.audio_size.setText(self.texts["size"].format(round(size_mb, 2)))
            
            self.audio_info_group.setVisible(True)
            
            # Enable transcribe button
            self.transcribe_btn.setEnabled(True)
        except:
            pass
            
        # Show notification
        self.show_notification(self.texts["task_complete"], filename)
        
    def start_screen_recording(self):
        save_path = self.video_folder_path.text()
        record_with_audio = self.record_with_audio_checkbox.isChecked()
        self.screen_recorder = ScreenRecorder(save_path, record_with_audio)
        self.screen_recorder.update_signal.connect(self.update_video_status)
        self.screen_recorder.finished_signal.connect(self.screen_recording_finished)
        self.screen_recorder.error_signal.connect(self.video_recording_error)
        self.screen_recorder.start()
        
        self.video_start_btn.setEnabled(False)
        self.video_stop_btn.setEnabled(True)
        self.video_stop_btn.setStyleSheet(f"background-color: {self.colors['accent']};")
        self.video_status.setText(self.texts["recording"])
        self.video_info_group.setVisible(False)
        
    def stop_screen_recording(self):
        if self.screen_recorder and self.screen_recorder.is_recording:
            self.screen_recorder.stop()
            self.video_status.setText(self.texts["stopped"])
            self.video_stop_btn.setStyleSheet("")  # Reset button style
            
    def update_video_status(self, status):
        self.video_status.setText(status)
        
    def screen_recording_finished(self, filename):
        self.video_start_btn.setEnabled(True)
        self.video_stop_btn.setEnabled(False)
        self.video_status.setText(self.texts["saved"].format(filename))
        
        # Show file info
        self.video_file_path.setText(filename)
        
        try:
            video = MP4(filename)
            duration = time.strftime('%M:%S', time.gmtime(video.info.length))
            self.video_duration.setText(self.texts["duration"].format(duration))
            
            size_mb = os.path.getsize(filename) / (1024 * 1024)
            self.video_size.setText(self.texts["size"].format(round(size_mb, 2)))
            
            self.video_info_group.setVisible(True)
            
            # Enable transcribe button if video was recorded with audio
            if self.record_with_audio_checkbox.isChecked():
                self.video_transcribe_btn.setEnabled(True)
            else:
                self.video_transcribe_btn.setEnabled(False)
        except:
            pass
            
        # Show notification
        self.show_notification(self.texts["task_complete"], filename)
        
    def video_recording_error(self, error_msg):
        self.video_start_btn.setEnabled(True)
        self.video_stop_btn.setEnabled(False)
        self.video_status.setText(self.texts["recording_error"] + ": " + error_msg)
        self.video_status.setStyleSheet(f"color: {self.colors['accent']};")
        
        # Show styled error message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.texts["error"])
        msg_box.setText(error_msg)
        msg_box.setIcon(QMessageBox.Warning)
        
        # Style the message box
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
                color: {self.colors['text']};
            }}
            QPushButton {{
                background-color: {self.colors['accent']};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
        """)
        
        msg_box.exec_()
        
    def transcribe_video_audio(self):
        # Get the video file path
        video_file = self.video_file_path.text()
        if not video_file or not os.path.exists(video_file):
            QMessageBox.warning(self, self.texts["error"], "No video file available for transcription.")
            return
            
        # Extract audio from video to a temporary file
        temp_audio_file = os.path.splitext(video_file)[0] + "_temp_audio.wav"
        
        try:
            # Use FFmpeg to extract audio
            import subprocess
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian format
                '-ar', '44100',  # 44.1kHz sampling rate
                '-ac', '1',  # Mono
                temp_audio_file
            ]
            
            subprocess.run(cmd, check=True)
            
            # Start transcription
            self.video_status.setText(self.texts["transcribing"])
            self.video_transcribe_btn.setEnabled(False)
            
            # Create and start the transcriber thread
            self.audio_transcriber = AudioTranscriber(temp_audio_file)
            self.audio_transcriber.update_signal.connect(self.update_video_status)
            self.audio_transcriber.finished_signal.connect(self.transcription_finished)
            self.audio_transcriber.error_signal.connect(self.transcription_error)
            self.audio_transcriber.start()
            
        except Exception as e:
            QMessageBox.critical(self, self.texts["error"], f"Error extracting audio: {str(e)}")
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
                
    def transcription_finished(self, text):
        # Display the transcription result
        self.video_transcription_text.setText(text)
        self.video_transcription_group.setVisible(True)
        self.video_status.setText(self.texts["transcription_complete"])
        self.video_transcribe_btn.setEnabled(True)
        
        # Clean up temporary audio file
        video_file = self.video_file_path.text()
        temp_audio_file = os.path.splitext(video_file)[0] + "_temp_audio.wav"
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
            
    def transcription_error(self, error_msg):
        self.video_status.setText(self.texts["transcription_error"])
        self.video_transcribe_btn.setEnabled(True)
        QMessageBox.critical(self, self.texts["error"], error_msg)
        
        # Clean up temporary audio file
        video_file = self.video_file_path.text()
        temp_audio_file = os.path.splitext(video_file)[0] + "_temp_audio.wav"
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
    
    def transcribe_audio(self):
        # Get the audio file path
        audio_file = self.audio_file_path.text()
        if not audio_file or not os.path.exists(audio_file):
            QMessageBox.warning(self, self.texts["error"], "No audio file available for transcription.")
            return
        
        # Start transcription
        self.audio_status.setText(self.texts["transcribing"])
        self.transcribe_btn.setEnabled(False)
        
        # Create and start the transcriber thread
        self.audio_transcriber = AudioTranscriber(audio_file)
        self.audio_transcriber.update_signal.connect(self.update_audio_status)
        self.audio_transcriber.finished_signal.connect(self.audio_transcription_finished)
        self.audio_transcriber.error_signal.connect(self.audio_transcription_error)
        self.audio_transcriber.start()
    
    def audio_transcription_finished(self, text):
        # Display the transcription result
        self.transcription_text.setText(text)
        self.transcription_group.setVisible(True)
        self.audio_status.setText(self.texts["transcription_complete"])
        self.transcribe_btn.setEnabled(True)
    
    def audio_transcription_error(self, error_msg):
        self.audio_status.setText(self.texts["transcription_error"])
        self.transcribe_btn.setEnabled(True)
        QMessageBox.critical(self, self.texts["error"], error_msg)
        
    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            return
            
        save_path = self.download_folder_path.text()
        download_type = 'audio' if self.audio_radio.isChecked() else 'video'
        
        self.download_btn.setEnabled(False)
        self.download_btn.setStyleSheet(f"background-color: {self.colors['light_text']};")
        self.download_progress.setValue(0)
        self.download_progress.setVisible(True)
        self.download_status.setText(self.texts["downloading"])
        self.download_info_group.setVisible(False)
        
        self.media_downloader = MediaDownloader(url, save_path, download_type)
        self.media_downloader.update_signal.connect(self.update_download_progress)
        self.media_downloader.finished_signal.connect(self.download_finished)
        self.media_downloader.error_signal.connect(self.download_error)
        self.media_downloader.start()
        
    def update_download_progress(self, status, percentage):
        if status == 'downloading':
            if percentage >= 0:
                self.download_progress.setValue(percentage)
                
                # Change progress bar color based on percentage
                if percentage < 30:
                    color = self.colors['accent']  # Red for early progress
                elif percentage < 70:
                    color = self.colors['primary']  # Blue for mid progress
                else:
                    color = self.colors['secondary']  # Green for near completion
            else:
                # Handle indeterminate progress (when percentage is -1)
                # Set to indeterminate mode
                self.download_progress.setRange(0, 0)  # Makes it an indeterminate progress bar
                color = self.colors['primary']  # Use primary color for indeterminate
                
            self.download_progress.setStyleSheet(f"""
                QProgressBar {{  
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    text-align: center;
                    height: 20px;
                }}
                
                QProgressBar::chunk {{  
                    background-color: {color};
                    width: 10px;
                    margin: 0.5px;
                }}
            """)
        elif status == 'processing':
            self.download_status.setText(self.texts["download_complete"])
            self.download_progress.setValue(100)
            self.download_progress.setStyleSheet(f"""
                QProgressBar {{  
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    text-align: center;
                    height: 20px;
                }}
                
                QProgressBar::chunk {{  
                    background-color: {self.colors['secondary']};
                    width: 10px;
                    margin: 0.5px;
                }}
            """)
            
    def download_finished(self, filename):
        self.download_btn.setEnabled(True)
        self.download_btn.setStyleSheet("")  # Reset button style
        self.download_status.setText(self.texts["download_complete"])
        
        # Reset progress bar to normal mode if it was in indeterminate mode
        self.download_progress.setRange(0, 100)
        self.download_progress.setValue(100)
        
        # Show file info
        self.download_file_path.setText(filename)
        
        try:
            # Check if audio or video
            if filename.endswith('.mp3'):
                media = MP3(filename)
            else:
                media = MP4(filename)
                
            duration = time.strftime('%M:%S', time.gmtime(media.info.length))
            self.download_duration.setText(self.texts["duration"].format(duration))
            
            size_mb = os.path.getsize(filename) / (1024 * 1024)
            self.download_size.setText(self.texts["size"].format(round(size_mb, 2)))
            
            self.download_info_group.setVisible(True)
        except:
            pass
            
        # Show notification
        self.show_notification(self.texts["task_complete"], filename)
        
    def download_error(self, error_msg):
        self.download_btn.setEnabled(True)
        self.download_btn.setStyleSheet("")  # Reset button style
        self.download_progress.setVisible(False)
        self.download_status.setText(self.texts["download_error"] + ": " + error_msg)
        self.download_status.setStyleSheet(f"color: {self.colors['accent']};")
        # Show styled error message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.texts["error"])
        msg_box.setText(error_msg)
        msg_box.setIcon(QMessageBox.Warning)
        
        # Style the message box
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
                color: {self.colors['text']};
            }}
            QPushButton {{
                background-color: {self.colors['accent']};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
        """)
        
        msg_box.exec_()
        
    def transcribe_video_audio(self):
        # Get the video file path
        video_file = self.video_file_path.text()
        if not video_file or not os.path.exists(video_file):
            QMessageBox.warning(self, self.texts["error"], "No video file available for transcription.")
            return
            
        # Extract audio from video to a temporary file
        temp_audio_file = os.path.splitext(video_file)[0] + "_temp_audio.wav"
        
        try:
            # Use FFmpeg to extract audio
            import subprocess
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian format
                '-ar', '44100',  # 44.1kHz sampling rate
                '-ac', '1',  # Mono
                temp_audio_file
            ]
            
            subprocess.run(cmd, check=True)
            
            # Start transcription
            self.video_status.setText(self.texts["transcribing"])
            self.video_transcribe_btn.setEnabled(False)
            
            # Create and start the transcriber thread
            self.audio_transcriber = AudioTranscriber(temp_audio_file)
            self.audio_transcriber.update_signal.connect(self.update_video_status)
            self.audio_transcriber.finished_signal.connect(self.transcription_finished)
            self.audio_transcriber.error_signal.connect(self.transcription_error)
            self.audio_transcriber.start()
            
        except Exception as e:
            QMessageBox.critical(self, self.texts["error"], f"Error extracting audio: {str(e)}")
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
                
    def transcription_finished(self, text):
        # Display the transcription result
        self.video_transcription_text.setText(text)
        self.video_transcription_group.setVisible(True)
        self.video_status.setText(self.texts["transcription_complete"])
        self.video_transcribe_btn.setEnabled(True)
        
        # Clean up temporary audio file
        video_file = self.video_file_path.text()
        temp_audio_file = os.path.splitext(video_file)[0] + "_temp_audio.wav"
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
            
    def transcription_error(self, error_msg):
        self.video_status.setText(self.texts["transcription_error"])
        self.video_transcribe_btn.setEnabled(True)
        QMessageBox.critical(self, self.texts["error"], error_msg)
        
        # Clean up temporary audio file
        video_file = self.video_file_path.text()
        temp_audio_file = os.path.splitext(video_file)[0] + "_temp_audio.wav"
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
        
    def show_notification(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        
        # Style the message box
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
                color: {self.colors['text']};
            }}
            QPushButton {{
                background-color: {self.colors['primary']};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
        """)
        
        msg_box.exec_()
        
    def transcribe_video_audio(self):
        # Get the video file path
        video_file = self.video_file_path.text()
        if not video_file or not os.path.exists(video_file):
            QMessageBox.warning(self, self.texts["error"], "No video file available for transcription.")
            return
            
        # Extract audio from video to a temporary file
        temp_audio_file = os.path.splitext(video_file)[0] + "_temp_audio.wav"
        
        try:
            # Use FFmpeg to extract audio
            import subprocess
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian format
                '-ar', '44100',  # 44.1kHz sampling rate
                '-ac', '1',  # Mono
                temp_audio_file
            ]
            
            subprocess.run(cmd, check=True)
            
            # Start transcription
            self.video_status.setText(self.texts["transcribing"])
            self.video_transcribe_btn.setEnabled(False)
            
            # Create and start the transcriber thread
            self.audio_transcriber = AudioTranscriber(temp_audio_file)
            self.audio_transcriber.update_signal.connect(self.update_video_status)
            self.audio_transcriber.finished_signal.connect(self.transcription_finished)
            self.audio_transcriber.error_signal.connect(self.transcription_error)
            self.audio_transcriber.start()
            
        except Exception as e:
            QMessageBox.critical(self, self.texts["error"], f"Error extracting audio: {str(e)}")
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
                
    def transcription_finished(self, text):
        # Display the transcription result
        self.video_transcription_text.setText(text)
        self.video_transcription_group.setVisible(True)
        self.video_status.setText(self.texts["transcription_complete"])
        self.video_transcribe_btn.setEnabled(True)
        
        # Clean up temporary audio file
        video_file = self.video_file_path.text()
        temp_audio_file = os.path.splitext(video_file)[0] + "_temp_audio.wav"
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
            
    def transcription_error(self, error_msg):
        self.video_status.setText(self.texts["transcription_error"])
        self.video_transcribe_btn.setEnabled(True)
        QMessageBox.critical(self, self.texts["error"], error_msg)
        
        # Clean up temporary audio file
        video_file = self.video_file_path.text()
        temp_audio_file = os.path.splitext(video_file)[0] + "_temp_audio.wav"
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)


    def apply_stylesheet(self):
        # Create stylesheet
        stylesheet = f"""
        QMainWindow, QWidget {{
            background-color: {self.colors['background']};
            color: {self.colors['text']};
        }}
        
        QTabWidget::pane {{  
            border: 1px solid #cccccc;
            background-color: white;
            border-radius: 5px;
            top: -1px;
        }}
        
        QTabBar::tab {{  
            background-color: #e6e6e6;
            color: {self.colors['light_text']};
            padding: 10px 20px;
            border: 1px solid #cccccc;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 3px;
            font-weight: bold;
            min-width: 120px;
            text-align: center;
        }}
        
        QTabBar::tab:hover {{
            background-color: #f0f0f0;
            color: {self.colors['primary']};
        }}
        
        QTabBar::tab:selected {{  
            background-color: white;
            color: {self.colors['primary']};
            border-bottom: 3px solid {self.colors['primary']};
        }}
        
        QPushButton {{  
            background-color: {self.colors['primary']};
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{  
            background-color: #2980b9;
        }}
        
        QPushButton:disabled {{  
            background-color: #bdc3c7;
        }}
        
        QLineEdit {{  
            padding: 10px;
            border: 1px solid #cccccc;
            border-radius: 5px;
            background-color: white;
            color: {self.colors['text']};
            selection-background-color: {self.colors['primary']};
            selection-color: white;
        }}
        
        QLineEdit:hover {{  
            border: 1px solid {self.colors['primary']};
        }}
        
        QLineEdit:focus {{  
            border: 2px solid {self.colors['primary']};
        }}
        
        QLineEdit:disabled {{  
            background-color: #f5f5f5;
            color: #7f8c8d;
        }}
        
        QComboBox {{  
            padding: 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: white;
        }}
        
        QProgressBar {{  
            border: 1px solid #cccccc;
            border-radius: 4px;
            text-align: center;
            height: 20px;
        }}
        
        QProgressBar::chunk {{  
            background-color: {self.colors['secondary']};
            width: 10px;
            margin: 0.5px;
        }}
        
        QGroupBox {{  
            border: 1px solid #cccccc;
            border-radius: 6px;
            margin-top: 20px;
            padding-top: 20px;
            padding: 10px;
            background-color: white;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
        }}
        
        QGroupBox::title {{  
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 2px 10px;
            color: {self.colors['primary']};
            font-weight: bold;
            background-color: white;
            border: 1px solid #cccccc;
            border-radius: 3px;
        }}
        
        QGroupBox QLabel {{  
            padding: 5px;
            color: {self.colors['text']};
        }}
        
        QRadioButton {{  
            spacing: 8px;
            color: {self.colors['text']};
            font-weight: bold;
        }}
        
        QRadioButton:hover {{  
            color: {self.colors['primary']};
        }}
        
        QRadioButton::indicator {{  
            width: 16px;
            height: 16px;
            border: 2px solid {self.colors['light_text']};
            border-radius: 9px;
        }}
        
        QRadioButton::indicator:unchecked:hover {{  
            border: 2px solid {self.colors['primary']};
        }}
        
        QRadioButton::indicator:checked {{  
            background-color: {self.colors['secondary']};
            border: 2px solid {self.colors['secondary']};
            border-radius: 9px;
        }}
        
        QRadioButton::indicator:checked:hover {{  
            background-color: #27ae60;
            border: 2px solid #27ae60;
        }}
        """
        
        # Apply stylesheet
        self.setStyleSheet(stylesheet)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())