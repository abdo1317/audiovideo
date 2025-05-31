# AudVed - Audio & Video Recorder

## أودفيد - مسجل الصوت والفيديو

AudVed is a desktop application for recording system audio, downloading audio/video from links, and recording your screen with audio.

أودفيد هو تطبيق سطح المكتب لتسجيل صوت النظام وتنزيل الصوت/الفيديو من الروابط وتسجيل الشاشة مع الصوت.

## Features / الميزات

- Record system audio / تسجيل صوت النظام
- Record screen with audio / تسجيل الشاشة مع الصوت
- Download audio/video from links (YouTube, etc.) / تنزيل الصوت/الفيديو من الروابط (يوتيوب، إلخ)
- Bilingual interface (Arabic/English) / واجهة ثنائية اللغة (عربي/إنجليزي)
- File information display / عرض معلومات الملف
- Non-blocking operations / عمليات غير متوقفة
- Notifications / إشعارات

## System Requirements / متطلبات النظام

- Operating System: Windows, macOS, or Linux / نظام التشغيل: ويندوز، ماك أو إس، أو لينكس
- Python 3.6 or higher / بايثون 3.6 أو أحدث
- Required libraries (listed in requirements.txt) / المكتبات المطلوبة (مذكورة في ملف requirements.txt)
- FFmpeg (optional, required for screen recording with audio and media conversion) / برنامج FFmpeg (اختياري، مطلوب لتسجيل الشاشة مع الصوت وتحويل الوسائط)

## Installation / التثبيت

1. Clone or download this repository / قم بتنزيل أو استنساخ هذا المستودع
2. Install required libraries / قم بتثبيت المكتبات المطلوبة:
   ```
   pip install -r requirements.txt
   ```
3. Install FFmpeg (optional but recommended) / قم بتثبيت FFmpeg (اختياري ولكن موصى به):
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg` or equivalent for your distribution
4. Run the application / قم بتشغيل التطبيق:
   ```
   python main.py
   ```

## Usage / الاستخدام

### Audio Recording / تسجيل الصوت
- Go to the "Audio Recording" tab / انتقل إلى تبويب "تسجيل الصوت"
- Select output folder / اختر مجلد الحفظ
- Click "Start Recording" to begin / اضغط على "بدء التسجيل" لبدء تسجيل الصوت
- Click "Stop Recording" when finished / اضغط على "إيقاف التسجيل" عند الانتهاء

### Screen Recording with Audio / تسجيل الشاشة مع الصوت
- Go to the "Screen Recording" tab / انتقل إلى تبويب "تسجيل الشاشة"
- Select output folder / اختر مجلد الحفظ
- Click "Start Recording" to begin / اضغط على "بدء التسجيل" لبدء تسجيل الشاشة
- The application will record both your screen and system audio / سيقوم التطبيق بتسجيل الشاشة والصوت معًا
- Click "Stop Recording" when finished / اضغط على "إيقاف التسجيل" عند الانتهاء
- Note: FFmpeg is required for merging audio and video / ملاحظة: يتطلب دمج الصوت والفيديو وجود برنامج FFmpeg

### Media Download / تحميل الوسائط
- Go to the "Download Media" tab / انتقل إلى تبويب "تحميل الوسائط"
- Enter the video or audio URL / أدخل رابط الفيديو أو الصوت
- Select download type (audio or video) / اختر نوع التحميل (صوت أو فيديو)
- Select output folder / اختر مجلد الحفظ
- Click "Download" / اضغط على "تحميل"

## License / الترخيص

This project is licensed under the MIT License. See the LICENSE file for details.

هذا المشروع مرخص تحت رخصة MIT. انظر ملف LICENSE للمزيد من المعلومات.

---

# AudVed - Audio & Video Recorder

A multilingual (Arabic/English) desktop application for recording system audio, screen recording, and downloading media from the internet.

## Features

- Record system audio with a button click
- Record computer screen
- Download audio and video from internet links (like YouTube)
- Bilingual user interface (Arabic/English)
- Save files in multiple formats
- Display file information (duration, size)
- Notifications when tasks are completed

## System Requirements

- Python 3.7 or newer
- Libraries mentioned in the requirements.txt file

## Installation

1. Install Python from the [official website](https://www.python.org/downloads/)
2. Download or clone this project
3. Open Command Prompt in the project folder
4. Install the requirements:

```
pip install -r requirements.txt
```

## Usage

To run the application:

```
python main.py
```

## Functions

- **Audio Recording**: Records audio from the system
- **Screen Recording**: Records the computer screen
- **Download from Link**: Downloads audio or video from an internet link
- **Format Conversion**: Supports converting audio files to different formats
- **Information Display**: Shows information about recorded or downloaded files

## License

This project is open source and available for use and modification.