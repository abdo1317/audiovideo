#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import threading
import time
import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                            QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                            QProgressBar, QComboBox, QLineEdit, QMessageBox,
                            QTabWidget, QGroupBox, QRadioButton, QSpacerItem,
                            QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl, QDir
from PyQt5.QtGui import QFont, QIcon

# تحميل مكتبة yt-dlp إذا كانت متوفرة
try:
    import yt_dlp as youtube_dl
except ImportError:
    import youtube_dl

# محاولة تحميل مكتبة pydub للتعامل مع الملفات الصوتية
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

# القاموس للترجمة
translations = {
    'ar': {
        'app_title': 'مسجل الصوت',
        'record_tab': 'تسجيل الصوت',
        'download_tab': 'تحميل من رابط',
        'start_recording': 'ابدأ التسجيل',
        'stop_recording': 'إيقاف التسجيل',
        'download_button': 'تحميل من رابط',
        'select_folder': 'اختر مجلد الحفظ',
        'status_ready': 'جاهز',
        'status_recording': 'جاري التسجيل...',
        'status_downloading': 'جاري التحميل...',
        'status_complete': 'اكتمل',
        'status_error': 'حدث خطأ',
        'enter_url': 'أدخل رابط الفيديو/الصوت',
        'language': 'اللغة:',
        'open_folder': 'فتح المجلد',
        'file_info': 'معلومات الملف',
        'duration': 'المدة:',
        'size': 'الحجم:',
        'format': 'الصيغة:',
        'convert_to': 'تحويل إلى:',
        'convert_button': 'تحويل',
        'notification_title': 'مسجل الصوت',
        'recording_complete': 'اكتمل التسجيل',
        'download_complete': 'اكتمل التحميل',
        'conversion_complete': 'اكتمل التحويل',
        'audio_format': 'صيغة الصوت:',
        'save_location': 'موقع الحفظ:',
        'browse': 'تصفح',
        'seconds': 'ثانية',
        'minutes': 'دقيقة',
        'hours': 'ساعة',
        'file_saved': 'تم حفظ الملف في:',
        'error_occurred': 'حدث خطأ:',
        'audio_only': 'صوت فقط',
        'video_with_audio': 'فيديو مع صوت',
        'download_type': 'نوع التحميل:',
        'recording_source': 'مصدر التسجيل:',
        'system_audio': 'صوت النظام',
        'microphone': 'الميكروفون',
    },
    'en': {
        'app_title': 'Audio Recorder',
        'record_tab': 'Record Audio',
        'download_tab': 'Download from URL',
        'start_recording': 'Start Recording',
        'stop_recording': 'Stop Recording',
        'download_button': 'Download from URL',
        'select_folder': 'Select Save Folder',
        'status_ready': 'Ready',
        'status_recording': 'Recording...',
        'status_downloading': 'Downloading...',
        'status_complete': 'Complete',
        'status_error': 'Error',
        'enter_url': 'Enter video/audio URL',
        'language': 'Language:',
        'open_folder': 'Open Folder',
        'file_info': 'File Information',
        'duration': 'Duration:',
        'size': 'Size:',
        'format': 'Format:',
        'convert_to': 'Convert to:',
        'convert_button': 'Convert',
        'notification_title': 'Audio Recorder',
        'recording_complete': 'Recording Complete',
        'download_complete': 'Download Complete',
        'conversion_complete': 'Conversion Complete',
        'audio_format': 'Audio Format:',
        'save_location': 'Save Location:',
        'browse': 'Browse',
        'seconds': 'seconds',
        'minutes': 'minutes',
        'hours': 'hours',
        'file_saved': 'File saved at:',
        'error_occurred': 'An error occurred:',
        'audio_only': 'Audio Only',
        'video_with_audio': 'Video with Audio',
        'download_type': 'Download Type:',
        'recording_source': 'Recording Source:',
        'system_audio': 'System Audio',
        'microphone': 'Microphone',
    }
}

# فئة خيط التسجيل
class RecordingThread(QThread):
    update_progress = pyqtSignal(int)
    recording_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, save_path, format='wav', source='microphone'):
        super().__init__()
        self.save_path = save_path
        self.format = format
        self.source = source
        self.is_recording = False
        self.frames = []
        self.sample_rate = 44100
        
    def run(self):
        try:
            self.is_recording = True
            
            # تحديد مصدر التسجيل (الميكروفون هو الخيار الوحيد المتاح حاليًا)
            # ملاحظة: تسجيل صوت النظام يتطلب مكتبات إضافية حسب نظام التشغيل
            
            # بدء التسجيل
            with sd.InputStream(samplerate=self.sample_rate, channels=2, callback=self.audio_callback):
                seconds_elapsed = 0
                while self.is_recording:
                    time.sleep(1)
                    seconds_elapsed += 1
                    self.update_progress.emit(seconds_elapsed)
            
            # حفظ التسجيل
            if len(self.frames) > 0:
                audio_data = np.concatenate(self.frames, axis=0)
                sf.write(self.save_path, audio_data, self.sample_rate)
                self.recording_finished.emit(self.save_path)
            else:
                self.error_occurred.emit("لم يتم تسجيل أي صوت")
                
        except Exception as e:
            self.error_occurred.emit(str(e))
            
    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.frames.append(indata.copy())
        
    def stop(self):
        self.is_recording = False

# فئة خيط التحميل
class DownloadThread(QThread):
    update_progress = pyqtSignal(float)
    download_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, url, save_dir, download_type='audio'):
        super().__init__()
        self.url = url
        self.save_dir = save_dir
        self.download_type = download_type
        self.filename = ""
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%')
            try:
                p_float = float(p.replace('%', ''))
                self.update_progress.emit(p_float)
            except:
                pass
        elif d['status'] == 'finished':
            self.filename = d.get('filename', '')
            
    def run(self):
        try:
            ydl_opts = {
                'progress_hooks': [self.progress_hook],
                'outtmpl': os.path.join(self.save_dir, '%(title)s.%(ext)s'),
            }
            
            if self.download_type == 'audio':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
                
            # إذا كان الملف فارغًا، استخدم اسم الملف من المجلد
            if not self.filename:
                # محاولة العثور على أحدث ملف في المجلد
                files = [os.path.join(self.save_dir, f) for f in os.listdir(self.save_dir)]
                if files:
                    self.filename = max(files, key=os.path.getctime)
                
            self.download_finished.emit(self.filename)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

# فئة خيط التحويل
class ConversionThread(QThread):
    conversion_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, input_file, output_format):
        super().__init__()
        self.input_file = input_file
        self.output_format = output_format
        
    def run(self):
        if not PYDUB_AVAILABLE:
            self.error_occurred.emit("مكتبة pydub غير متوفرة للتحويل")
            return
            
        try:
            # تحديد نوع الملف المدخل
            input_ext = os.path.splitext(self.input_file)[1].lower().replace('.', '')
            
            # إنشاء اسم الملف الجديد
            output_file = os.path.splitext(self.input_file)[0] + '.' + self.output_format
            
            # تحويل الملف
            audio = AudioSegment.from_file(self.input_file, format=input_ext)
            audio.export(output_file, format=self.output_format)
            
            self.conversion_finished.emit(output_file)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

# النافذة الرئيسية
class AudioRecorderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # الإعدادات الأولية
        self.current_language = 'ar'  # اللغة الافتراضية هي العربية
        self.recording_thread = None
        self.download_thread = None
        self.conversion_thread = None
        self.last_file = None
        self.save_directory = os.path.expanduser("~/Music")
        
        # إعداد واجهة المستخدم
        self.init_ui()
        
        # تطبيق اللغة الافتراضية
        self.apply_language()
        
    def init_ui(self):
        # إعداد النافذة الرئيسية
        self.setMinimumSize(600, 500)
        
        # إنشاء التبويبات
        self.tabs = QTabWidget()
        self.record_tab = QWidget()
        self.download_tab = QWidget()
        
        self.tabs.addTab(self.record_tab, "تسجيل الصوت")
        self.tabs.addTab(self.download_tab, "تحميل من رابط")
        
        # إعداد تبويب التسجيل
        self.setup_record_tab()
        
        # إعداد تبويب التحميل
        self.setup_download_tab()
        
        # إعداد شريط الحالة
        self.status_bar = self.statusBar()
        self.status_label = QLabel("جاهز")
        self.status_bar.addWidget(self.status_label)
        
        # إعداد اختيار اللغة
        language_widget = QWidget()
        language_layout = QHBoxLayout(language_widget)
        
        self.language_label = QLabel("اللغة:")
        self.language_combo = QComboBox()
        self.language_combo.addItem("العربية", "ar")
        self.language_combo.addItem("English", "en")
        self.language_combo.currentIndexChanged.connect(self.change_language)
        
        language_layout.addWidget(self.language_label)
        language_layout.addWidget(self.language_combo)
        language_layout.setAlignment(Qt.AlignRight)
        
        # إعداد التخطيط الرئيسي
        main_layout = QVBoxLayout()
        main_layout.addWidget(language_widget)
        main_layout.addWidget(self.tabs)
        
        # إعداد الويدجت المركزي
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
    def setup_record_tab(self):
        layout = QVBoxLayout()
        
        # مجموعة إعدادات التسجيل
        settings_group = QGroupBox("إعدادات التسجيل")
        settings_layout = QVBoxLayout()
        
        # مصدر التسجيل
        source_layout = QHBoxLayout()
        self.source_label = QLabel("مصدر التسجيل:")
        self.source_combo = QComboBox()
        self.source_combo.addItem("الميكروفون", "microphone")
        self.source_combo.addItem("صوت النظام", "system")
        source_layout.addWidget(self.source_label)
        source_layout.addWidget(self.source_combo)
        
        # صيغة الصوت
        format_layout = QHBoxLayout()
        self.format_label = QLabel("صيغة الصوت:")
        self.format_combo = QComboBox()
        self.format_combo.addItem("WAV", "wav")
        self.format_combo.addItem("MP3", "mp3")
        format_layout.addWidget(self.format_label)
        format_layout.addWidget(self.format_combo)
        
        # موقع الحفظ
        location_layout = QHBoxLayout()
        self.location_label = QLabel("موقع الحفظ:")
        self.location_edit = QLineEdit(self.save_directory)
        self.location_edit.setReadOnly(True)
        self.browse_button = QPushButton("تصفح")
        self.browse_button.clicked.connect(self.browse_save_location)
        location_layout.addWidget(self.location_label)
        location_layout.addWidget(self.location_edit)
        location_layout.addWidget(self.browse_button)
        
        settings_layout.addLayout(source_layout)
        settings_layout.addLayout(format_layout)
        settings_layout.addLayout(location_layout)
        settings_group.setLayout(settings_layout)
        
        # أزرار التسجيل
        buttons_layout = QHBoxLayout()
        self.record_button = QPushButton("ابدأ التسجيل")
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setMinimumHeight(50)
        
        self.open_folder_button = QPushButton("فتح المجلد")
        self.open_folder_button.clicked.connect(self.open_save_folder)
        
        buttons_layout.addWidget(self.record_button)
        buttons_layout.addWidget(self.open_folder_button)
        
        # شريط التقدم
        progress_layout = QVBoxLayout()
        self.progress_label = QLabel("0:00")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        # معلومات الملف
        self.file_info_group = QGroupBox("معلومات الملف")
        file_info_layout = QVBoxLayout()
        
        self.file_path_label = QLabel("")
        self.file_duration_label = QLabel("المدة: --")
        self.file_size_label = QLabel("الحجم: --")
        self.file_format_label = QLabel("الصيغة: --")
        
        file_info_layout.addWidget(self.file_path_label)
        file_info_layout.addWidget(self.file_duration_label)
        file_info_layout.addWidget(self.file_size_label)
        file_info_layout.addWidget(self.file_format_label)
        
        # تحويل الصيغة
        convert_layout = QHBoxLayout()
        self.convert_label = QLabel("تحويل إلى:")
        self.convert_combo = QComboBox()
        self.convert_combo.addItem("MP3", "mp3")
        self.convert_combo.addItem("WAV", "wav")
        self.convert_combo.addItem("OGG", "ogg")
        self.convert_combo.addItem("FLAC", "flac")
        
        self.convert_button = QPushButton("تحويل")
        self.convert_button.clicked.connect(self.convert_audio)
        self.convert_button.setEnabled(False)
        
        convert_layout.addWidget(self.convert_label)
        convert_layout.addWidget(self.convert_combo)
        convert_layout.addWidget(self.convert_button)
        
        file_info_layout.addLayout(convert_layout)
        self.file_info_group.setLayout(file_info_layout)
        self.file_info_group.setVisible(False)
        
        # إضافة كل شيء إلى التخطيط الرئيسي
        layout.addWidget(settings_group)
        layout.addLayout(buttons_layout)
        layout.addLayout(progress_layout)
        layout.addWidget(self.file_info_group)
        
        # إضافة مساحة مرنة
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.record_tab.setLayout(layout)
        
    def setup_download_tab(self):
        layout = QVBoxLayout()
        
        # مجموعة إعدادات التحميل
        settings_group = QGroupBox("إعدادات التحميل")
        settings_layout = QVBoxLayout()
        
        # رابط التحميل
        url_layout = QHBoxLayout()
        self.url_label = QLabel("أدخل رابط الفيديو/الصوت:")
        self.url_edit = QLineEdit()
        url_layout.addWidget(self.url_label)
        url_layout.addWidget(self.url_edit)
        
        # نوع التحميل
        type_layout = QHBoxLayout()
        self.type_label = QLabel("نوع التحميل:")
        self.type_combo = QComboBox()
        self.type_combo.addItem("صوت فقط", "audio")
        self.type_combo.addItem("فيديو مع صوت", "video")
        type_layout.addWidget(self.type_label)
        type_layout.addWidget(self.type_combo)
        
        # موقع الحفظ
        location_layout = QHBoxLayout()
        self.dl_location_label = QLabel("موقع الحفظ:")
        self.dl_location_edit = QLineEdit(self.save_directory)
        self.dl_location_edit.setReadOnly(True)
        self.dl_browse_button = QPushButton("تصفح")
        self.dl_browse_button.clicked.connect(self.browse_download_location)
        location_layout.addWidget(self.dl_location_label)
        location_layout.addWidget(self.dl_location_edit)
        location_layout.addWidget(self.dl_browse_button)
        
        settings_layout.addLayout(url_layout)
        settings_layout.addLayout(type_layout)
        settings_layout.addLayout(location_layout)
        settings_group.setLayout(settings_layout)
        
        # أزرار التحميل
        buttons_layout = QHBoxLayout()
        self.download_button = QPushButton("تحميل من رابط")
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setMinimumHeight(50)
        
        self.dl_open_folder_button = QPushButton("فتح المجلد")
        self.dl_open_folder_button.clicked.connect(self.open_download_folder)
        
        buttons_layout.addWidget(self.download_button)
        buttons_layout.addWidget(self.dl_open_folder_button)
        
        # شريط التقدم
        dl_progress_layout = QVBoxLayout()
        self.dl_progress_label = QLabel("0%")
        self.dl_progress_bar = QProgressBar()
        self.dl_progress_bar.setRange(0, 100)
        self.dl_progress_bar.setValue(0)
        
        dl_progress_layout.addWidget(self.dl_progress_label)
        dl_progress_layout.addWidget(self.dl_progress_bar)
        
        # معلومات الملف المحمل
        self.dl_file_info_group = QGroupBox("معلومات الملف")
        dl_file_info_layout = QVBoxLayout()
        
        self.dl_file_path_label = QLabel("")
        self.dl_file_size_label = QLabel("الحجم: --")
        self.dl_file_format_label = QLabel("الصيغة: --")
        
        dl_file_info_layout.addWidget(self.dl_file_path_label)
        dl_file_info_layout.addWidget(self.dl_file_size_label)
        dl_file_info_layout.addWidget(self.dl_file_format_label)
        
        # تحويل الصيغة للملف المحمل
        dl_convert_layout = QHBoxLayout()
        self.dl_convert_label = QLabel("تحويل إلى:")
        self.dl_convert_combo = QComboBox()
        self.dl_convert_combo.addItem("MP3", "mp3")
        self.dl_convert_combo.addItem("WAV", "wav")
        self.dl_convert_combo.addItem("OGG", "ogg")
        self.dl_convert_combo.addItem("FLAC", "flac")
        
        self.dl_convert_button = QPushButton("تحويل")
        self.dl_convert_button.clicked.connect(self.convert_downloaded_audio)
        self.dl_convert_button.setEnabled(False)
        
        dl_convert_layout.addWidget(self.dl_convert_label)
        dl_convert_layout.addWidget(self.dl_convert_combo)
        dl_convert_layout.addWidget(self.dl_convert_button)
        
        dl_file_info_layout.addLayout(dl_convert_layout)
        self.dl_file_info_group.setLayout(dl_file_info_layout)
        self.dl_file_info_group.setVisible(False)
        
        # إضافة كل شيء إلى التخطيط الرئيسي
        layout.addWidget(settings_group)
        layout.addLayout(buttons_layout)
        layout.addLayout(dl_progress_layout)
        layout.addWidget(self.dl_file_info_group)
        
        # إضافة مساحة مرنة
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.download_tab.setLayout(layout)
        
    def apply_language(self):
        # تطبيق اللغة المحددة على واجهة المستخدم
        t = translations[self.current_language]
        
        # عنوان التطبيق
        self.setWindowTitle(t['app_title'])
        
        # التبويبات
        self.tabs.setTabText(0, t['record_tab'])
        self.tabs.setTabText(1, t['download_tab'])
        
        # تبويب التسجيل
        self.record_button.setText(t['start_recording'] if not self.recording_thread or not self.recording_thread.is_recording else t['stop_recording'])
        self.open_folder_button.setText(t['open_folder'])
        self.source_label.setText(t['recording_source'])
        self.format_label.setText(t['audio_format'])
        self.location_label.setText(t['save_location'])
        self.browse_button.setText(t['browse'])
        
        # تحديث عناصر القائمة المنسدلة
        current_source_index = self.source_combo.currentIndex()
        self.source_combo.clear()
        self.source_combo.addItem(t['microphone'], "microphone")
        self.source_combo.addItem(t['system_audio'], "system")
        self.source_combo.setCurrentIndex(current_source_index)
        
        # معلومات الملف
        self.file_info_group.setTitle(t['file_info'])
        self.file_duration_label.setText(f"{t['duration']} --")
        self.file_size_label.setText(f"{t['size']} --")
        self.file_format_label.setText(f"{t['format']} --")
        self.convert_label.setText(t['convert_to'])
        self.convert_button.setText(t['convert_button'])
        
        # تبويب التحميل
        self.url_label.setText(t['enter_url'])
        self.type_label.setText(t['download_type'])
        self.dl_location_label.setText(t['save_location'])
        self.dl_browse_button.setText(t['browse'])
        self.download_button.setText(t['download_button'])
        self.dl_open_folder_button.setText(t['open_folder'])
        
        # تحديث عناصر القائمة المنسدلة
        current_type_index = self.type_combo.currentIndex()
        self.type_combo.clear()
        self.type_combo.addItem(t['audio_only'], "audio")
        self.type_combo.addItem(t['video_with_audio'], "video")
        self.type_combo.setCurrentIndex(current_type_index)
        
        # معلومات الملف المحمل
        self.dl_file_info_group.setTitle(t['file_info'])
        self.dl_file_size_label.setText(f"{t['size']} --")
        self.dl_file_format_label.setText(f"{t['format']} --")
        self.dl_convert_label.setText(t['convert_to'])
        self.dl_convert_button.setText(t['convert_button'])
        
        # اختيار اللغة
        self.language_label.setText(t['language'])
        
        # شريط الحالة
        self.status_label.setText(t['status_ready'])
        
    def change_language(self, index):
        self.current_language = self.language_combo.itemData(index)
        self.apply_language()
        
    def browse_save_location(self):
        folder = QFileDialog.getExistingDirectory(self, "اختر مجلد الحفظ", self.save_directory)
        if folder:
            self.save_directory = folder
            self.location_edit.setText(folder)
            self.dl_location_edit.setText(folder)
            
    def browse_download_location(self):
        folder = QFileDialog.getExistingDirectory(self, "اختر مجلد الحفظ", self.save_directory)
        if folder:
            self.save_directory = folder
            self.location_edit.setText(folder)
            self.dl_location_edit.setText(folder)
            
    def toggle_recording(self):
        t = translations[self.current_language]
        
        if self.recording_thread and self.recording_thread.is_recording:
            # إيقاف التسجيل
            self.recording_thread.stop()
            self.record_button.setText(t['start_recording'])
            self.status_label.setText(t['status_complete'])
        else:
            # بدء التسجيل
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            format_ext = self.format_combo.currentData()
            filename = f"recording_{timestamp}.{format_ext}"
            save_path = os.path.join(self.save_directory, filename)
            
            self.recording_thread = RecordingThread(
                save_path=save_path,
                format=format_ext,
                source=self.source_combo.currentData()
            )
            
            self.recording_thread.update_progress.connect(self.update_recording_progress)
            self.recording_thread.recording_finished.connect(self.on_recording_finished)
            self.recording_thread.error_occurred.connect(self.on_recording_error)
            
            self.recording_thread.start()
            
            self.record_button.setText(t['stop_recording'])
            self.status_label.setText(t['status_recording'])
            self.progress_bar.setValue(0)
            self.progress_label.setText("0:00")
            self.file_info_group.setVisible(False)
            
    def update_recording_progress(self, seconds):
        # تحديث شريط التقدم ومؤشر الوقت
        minutes = seconds // 60
        seconds = seconds % 60
        self.progress_label.setText(f"{minutes}:{seconds:02d}")
        
        # تحديث شريط التقدم (يزيد تدريجيًا حتى 100)
        if seconds < 100:
            self.progress_bar.setValue(seconds)
        else:
            # إعادة ضبط النطاق إذا تجاوز الحد
            max_value = self.progress_bar.maximum()
            if seconds > max_value:
                self.progress_bar.setMaximum(seconds + 60)
            self.progress_bar.setValue(seconds)
            
    def on_recording_finished(self, file_path):
        t = translations[self.current_language]
        
        # تحديث واجهة المستخدم
        self.record_button.setText(t['start_recording'])
        self.status_label.setText(t['status_complete'])
        
        # عرض معلومات الملف
        self.last_file = file_path
        self.show_file_info(file_path)
        
        # عرض إشعار
        QMessageBox.information(self, t['notification_title'], t['recording_complete'])
        
    def on_recording_error(self, error_message):
        t = translations[self.current_language]
        
        # تحديث واجهة المستخدم
        self.record_button.setText(t['start_recording'])
        self.status_label.setText(t['status_error'])
        
        # عرض رسالة الخطأ
        QMessageBox.critical(self, t['notification_title'], f"{t['error_occurred']} {error_message}")
        
    def start_download(self):
        t = translations[self.current_language]
        
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, t['notification_title'], t['enter_url'])
            return
            
        # بدء التحميل
        self.download_thread = DownloadThread(
            url=url,
            save_dir=self.save_directory,
            download_type=self.type_combo.currentData()
        )
        
        self.download_thread.update_progress.connect(self.update_download_progress)
        self.download_thread.download_finished.connect(self.on_download_finished)
        self.download_thread.error_occurred.connect(self.on_download_error)
        
        self.download_thread.start()
        
        self.download_button.setEnabled(False)
        self.status_label.setText(t['status_downloading'])
        self.dl_progress_bar.setValue(0)
        self.dl_progress_label.setText("0%")
        self.dl_file_info_group.setVisible(False)
        
    def update_download_progress(self, percent):
        self.dl_progress_bar.setValue(int(percent))
        self.dl_progress_label.setText(f"{int(percent)}%")
        
    def on_download_finished(self, file_path):
        t = translations[self.current_language]
        
        # تحديث واجهة المستخدم
        self.download_button.setEnabled(True)
        self.status_label.setText(t['status_complete'])
        
        # عرض معلومات الملف
        self.last_file = file_path
        self.show_download_file_info(file_path)
        
        # عرض إشعار
        QMessageBox.information(self, t['notification_title'], t['download_complete'])
        
    def on_download_error(self, error_message):
        t = translations[self.current_language]
        
        # تحديث واجهة المستخدم
        self.download_button.setEnabled(True)
        self.status_label.setText(t['status_error'])
        
        # عرض رسالة الخطأ
        QMessageBox.critical(self, t['notification_title'], f"{t['error_occurred']} {error_message}")
        
    def show_file_info(self, file_path):
        t = translations[self.current_language]
        
        if not os.path.exists(file_path):
            return
            
        # عرض مسار الملف
        self.file_path_label.setText(os.path.basename(file_path))
        
        # حجم الملف
        size_bytes = os.path.getsize(file_path)
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes/1024:.2f} KB"
        else:
            size_str = f"{size_bytes/(1024*1024):.2f} MB"
            
        self.file_size_label.setText(f"{t['size']} {size_str}")
        
        # صيغة الملف
        file_ext = os.path.splitext(file_path)[1].lower().replace('.', '')
        self.file_format_label.setText(f"{t['format']} {file_ext.upper()}")
        
        # محاولة الحصول على مدة الملف
        try:
            audio_info = sf.info(file_path)
            duration_seconds = int(audio_info.duration)
            minutes = duration_seconds // 60
            seconds = duration_seconds % 60
            
            if minutes >= 60:
                hours = minutes // 60
                minutes = minutes % 60
                duration_str = f"{hours} {t['hours']}, {minutes} {t['minutes']}, {seconds} {t['seconds']}"
            else:
                duration_str = f"{minutes} {t['minutes']}, {seconds} {t['seconds']}"
                
            self.file_duration_label.setText(f"{t['duration']} {duration_str}")
        except:
            self.file_duration_label.setText(f"{t['duration']} --")
            
        # تفعيل زر التحويل
        self.convert_button.setEnabled(True)
        
        # إظهار مجموعة معلومات الملف
        self.file_info_group.setVisible(True)
        
    def show_download_file_info(self, file_path):
        t = translations[self.current_language]
        
        if not os.path.exists(file_path):
            return
            
        # عرض مسار الملف
        self.dl_file_path_label.setText(os.path.basename(file_path))
        
        # حجم الملف
        size_bytes = os.path.getsize(file_path)
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes/1024:.2f} KB"
        else:
            size_str = f"{size_bytes/(1024*1024):.2f} MB"
            
        self.dl_file_size_label.setText(f"{t['size']} {size_str}")
        
        # صيغة الملف
        file_ext = os.path.splitext(file_path)[1].lower().replace('.', '')
        self.dl_file_format_label.setText(f"{t['format']} {file_ext.upper()}")
        
        # تفعيل زر التحويل
        self.dl_convert_button.setEnabled(True)
        
        # إظهار مجموعة معلومات الملف
        self.dl_file_info_group.setVisible(True)
        
    def convert_audio(self):
        if not self.last_file or not os.path.exists(self.last_file):
            return
            
        output_format = self.convert_combo.currentData()
        current_format = os.path.splitext(self.last_file)[1].lower().replace('.', '')
        
        if output_format == current_format:
            t = translations[self.current_language]
            QMessageBox.information(self, t['notification_title'], f"الملف بالفعل بصيغة {output_format.upper()}")
            return
            
        self.conversion_thread = ConversionThread(
            input_file=self.last_file,
            output_format=output_format
        )
        
        self.conversion_thread.conversion_finished.connect(self.on_conversion_finished)
        self.conversion_thread.error_occurred.connect(self.on_conversion_error)
        
        self.conversion_thread.start()
        self.convert_button.setEnabled(False)
        
    def convert_downloaded_audio(self):
        if not self.last_file or not os.path.exists(self.last_file):
            return
            
        output_format = self.dl_convert_combo.currentData()
        current_format = os.path.splitext(self.last_file)[1].lower().replace('.', '')
        
        if output_format == current_format:
            t = translations[self.current_language]
            QMessageBox.information(self, t['notification_title'], f"الملف بالفعل بصيغة {output_format.upper()}")
            return
            
        self.conversion_thread = ConversionThread(
            input_file=self.last_file,
            output_format=output_format
        )
        
        self.conversion_thread.conversion_finished.connect(self.on_conversion_finished)
        self.conversion_thread.error_occurred.connect(self.on_conversion_error)
        
        self.conversion_thread.start()
        self.dl_convert_button.setEnabled(False)
        
    def on_conversion_finished(self, output_file):
        t = translations[self.current_language]
        
        # تحديث واجهة المستخدم
        self.convert_button.setEnabled(True)
        self.dl_convert_button.setEnabled(True)
        
        # تحديث الملف الحالي
        self.last_file = output_file
        
        # تحديث معلومات الملف
        if self.tabs.currentIndex() == 0:
            self.show_file_info(output_file)
        else:
            self.show_download_file_info(output_file)
            
        # عرض إشعار
        QMessageBox.information(self, t['notification_title'], f"{t['conversion_complete']}\n{t['file_saved']} {output_file}")
        
    def on_conversion_error(self, error_message):
        t = translations[self.current_language]
        
        # تحديث واجهة المستخدم
        self.convert_button.setEnabled(True)
        self.dl_convert_button.setEnabled(True)
        
        # عرض رسالة الخطأ
        QMessageBox.critical(self, t['notification_title'], f"{t['error_occurred']} {error_message}")
        
    def open_save_folder(self):
        if os.path.exists(self.save_directory):
            # فتح المجلد باستخدام الأمر المناسب حسب نظام التشغيل
            if sys.platform == 'win32':
                os.startfile(self.save_directory)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{self.save_directory}"')
            else:  # Linux
                os.system(f'xdg-open "{self.save_directory}"')
                
    def open_download_folder(self):
        if os.path.exists(self.save_directory):
            # فتح المجلد باستخدام الأمر المناسب حسب نظام التشغيل
            if sys.platform == 'win32':
                os.startfile(self.save_directory)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{self.save_directory}"')
            else:  # Linux
                os.system(f'xdg-open "{self.save_directory}"')

# تشغيل التطبيق
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # تعيين نمط الخط للدعم العربي
    font = QFont("Arial", 10)
    app.setFont(font)
    
    window = AudioRecorderApp()
    window.show()
    
    sys.exit(app.exec_())
