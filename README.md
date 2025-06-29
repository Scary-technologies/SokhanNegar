# سخن نگار لایو 🎤

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

**سخن نگار لایو** یک برنامه ساده و قدرتمند برای تبدیل گفتار فارسی به متن در زمان واقعی است. این برنامه با استفاده از میکروفون، کلمات شما را به صورت زنده تشخیص داده و به متن تبدیل می‌کند.

## ✨ ویژگی‌ها

- 🎯 **تشخیص زنده گفتار**: تبدیل فوری صدا به متن
- 🇮🇷 **پشتیبانی کامل از فارسی**: بهینه شده برای زبان فارسی
- 🖥️ **رابط کاربری مینیمال**: طراحی ساده و کاربرپسند
- ⚡ **عملکرد سریع**: حداقل تأخیر در تشخیص
- 🔧 **سهولت استفاده**: نصب و راه‌اندازی آسان

## 📋 پیش‌نیازها

- Python 3.7 یا بالاتر
- میکروفون فعال
- اتصال اینترنت (برای سرویس تشخیص گفتار)

## 🚀 نصب

### 1. دانلود یا کلون کردن پروژه

```bash
git clone https://github.com/Scary-technologies/SokhanNegar.git
cd SokhanNegar
```

### 2. نصب کتابخانه‌های مورد نیاز

```bash
pip install speechrecognition pyaudio
```

#### نصب PyAudio در سیستم‌عامل‌های مختلف:

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum install portaudio-devel
# یا در Fedora جدید:
sudo dnf install portaudio-devel
pip install pyaudio
```

## 🎯 استفاده

### اجرای برنامه

```bash
python SokhanNegar.py
```

### نحوه کار با برنامه

1. **شروع گوش دادن**: روی دکمه "▶ شروع" کلیک کنید
2. **صحبت کردن**: با میکروفون به زبان فارسی صحبت کنید
3. **مشاهده متن**: کلمات شما به صورت زنده در ناحیه متن نمایش داده می‌شود
4. **توقف**: برای توقف روی دکمه "⏸ توقف" کلیک کنید

### کلیدهای میانبر

| کلید | عملکرد |
|------|---------|
| `Ctrl + Enter` | شروع/توقف گوش دادن |
| `Ctrl + C` | کپی کردن متن |
| `Ctrl + L` | پاک کردن متن |

## 🔧 تنظیمات

### تنظیمات میکروفون

برنامه به صورت خودکار میکروفون را تنظیم می‌کند، اما می‌توانید در کد تغییرات زیر را اعمال کنید:

```python
# تنظیم حساسیت میکروفون
self.recognizer.energy_threshold = 4000  # مقدار پیش‌فرض

# تنظیم زمان توقف بین کلمات
self.recognizer.pause_threshold = 0.8  # ثانیه

# تنظیم حداقل طول عبارت
self.recognizer.phrase_threshold = 0.3  # ثانیه
```

### تغییر زبان

برای تغییر زبان تشخیص، در تابع `process_audio_queue` خط زیر را تغییر دهید:

```python
text = self.recognizer.recognize_google(audio, language='fa-IR')
```

زبان‌های پشتیبانی شده:
- `fa-IR`: فارسی ایران
- `en-US`: انگلیسی آمریکا
- `ar-SA`: عربی عربستان


## 🐛 رفع مشکلات

### مشکلات رایج

#### خطای "No module named 'pyaudio'"
**حل:** مطابق بخش نصب، PyAudio را نصب کنید.

#### میکروفون کار نمی‌کند
**حل:** 
- مطمئن شوید میکروفون متصل و فعال است
- دسترسی میکروفون را در تنظیمات سیستم بررسی کنید
- برنامه‌های دیگر که از میکروفون استفاده می‌کنند را ببندید

#### کیفیت تشخیص پایین است
**حل:**
- در محیط کم‌صدا صحبت کنید
- میکروفون را نزدیک‌تر به دهان قرار دهید
- مقدار `energy_threshold` را تنظیم کنید

#### خطای اتصال اینترنت
**حل:** مطمئن شوید اتصال اینترنت فعال است چون سرویس Google برای تشخیص گفتار استفاده می‌شود.

### لاگ‌ها و دیباگ

برای دیدن اطلاعات بیشتر خطاها، می‌توانید برنامه را از ترمینال اجرا کنید:

```bash
python sokhan_negar_.py
```

## 🤝 مشارکت

ما از مشارکت شما استقبال می‌کنیم! برای مشارکت:

1. پروژه را Fork کنید
2. یک شاخه جدید ایجاد کنید (`git checkout -b feature/AmazingFeature`)
3. تغییرات خود را commit کنید (`git commit -m 'Add some AmazingFeature'`)
4. به شاخه خود push کنید (`git push origin feature/AmazingFeature`)
5. یک Pull Request ایجاد کنید

### راهنمای توسعه

```bash
# کلون کردن پروژه
git clone https://github.com/Scary-technologies/SokhanNegar.git
cd SokhanNegar

# ایجاد محیط مجازی
python -m venv venv
source venv/bin/activate  # Linux/macOS
# یا
venv\Scripts\activate     # Windows

# نصب وابستگی‌ها
pip install -r requirements.txt
```

## 📝 مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای جزئیات بیشتر فایل [LICENSE](LICENSE) را مطالعه کنید.

## 👨‍💻 سازنده

**نام شما**
- GitHub: [@Scary-technologies](https://github.com/Scary-technologies)
- Email: your.email@example.com

## 📞 پشتیبانی

اگر با مشکلی مواجه شدید یا سوالی دارید:

1. ابتدا بخش [رفع مشکلات](#-رفع-مشکلات) را بررسی کنید
2. در بخش [Issues](https://github.com/Scary-technologies/SokhanNegar/issues) پروژه سوال خود را مطرح کنید
3. یا از طریق ایمیل با ما تماس بگیرید

## 🙏 تشکر

- از [SpeechRecognition](https://github.com/Uberi/speech_recognition) برای ارائه API تشخیص گفتار
- از Google برای سرویس رایگان Speech-to-Text
- از جامعه توسعه‌دهندگان Python برای ابزارهای فوق‌العاده

## 📈 نسخه‌ها

### v1.0.0 (تاریخ فعلی)
- انتشار اولیه
- تشخیص زنده گفتار فارسی
- رابط کاربری مینیمال
- کلیدهای میانبر

### برنامه‌های آینده
- [ ] افزودن پشتیبانی از زبان‌های بیشتر
- [ ] بهبود دقت تشخیص
- [ ] افزودن تم‌های مختلف
- [ ] ذخیره خودکار متن
- [ ] پشتیبانی از دستورات صوتی

---

⭐ اگر این پروژه برایتان مفید بود، یک ستاره بدهید!

---

**ساخته شده با ❤️ برای جامعه توسعه‌دهندگان ایرانی**