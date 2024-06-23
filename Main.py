import sys
import speech_recognition as sr
import pyperclip
import pyautogui
import pygetwindow as gw
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLabel, QCheckBox, QMessageBox, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QIcon
import time

# کلاس برای پردازش تشخیص گفتار در یک نخ مجزا
class SpeechRecognitionThread(QThread):
    recognized_text = pyqtSignal(str)  # سیگنال برای متن تشخیص داده شده
    listening_status = pyqtSignal(bool)  # سیگنال برای وضعیت شنیدن

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.running = True

    def run(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.running:
                try:
                    self.listening_status.emit(True)
                    audio = self.recognizer.listen(source)
                    self.listening_status.emit(False)
                    text = self.recognizer.recognize_google(audio, language='fa-IR')
                    self.recognized_text.emit(text)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")

    def stop(self):
        self.running = False
        self.listening_status.emit(False)

# کلاس اصلی برنامه
class SpeechToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('تبدیل صدا به متن')
        self.setGeometry(100, 100, 600, 400)

        # تنظیم آیکون برنامه
        self.setWindowIcon(QIcon('logo.png'))

        self.initUI()
        self.speech_thread = SpeechRecognitionThread()
        self.speech_thread.recognized_text.connect(self.display_text)
        self.speech_thread.listening_status.connect(self.update_listening_status)

    def initUI(self):
        layout = QVBoxLayout()

        # ایجاد ویجت متنی برای نمایش متن تشخیص داده شده
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        layout.addWidget(self.textEdit)

        # ایجاد لایه برای نمایش وضعیت شنیدن
        status_layout = QHBoxLayout()
        self.status_label = QLabel("وضعیت: عدم شنیدن", self)
        status_layout.addWidget(self.status_label)

        # ایجاد نشانگر وضعیت شنیدن
        self.status_indicator = QLabel(self)
        self.status_indicator.setFixedSize(20, 20)
        self.status_indicator.setStyleSheet("background-color: red; border-radius: 10px;")
        status_layout.addWidget(self.status_indicator)
        
        layout.addLayout(status_layout)

        # ایجاد لیبل راهنما
        self.label = QLabel("برای شروع/توقف ضبط دکمه را فشار دهید...", self)
        layout.addWidget(self.label)

        # ایجاد دکمه شروع/توقف ضبط
        self.start_stop_button = QPushButton('شروع ضبط', self)
        self.start_stop_button.setCheckable(True)
        self.start_stop_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.start_stop_button)

        # ایجاد چک‌باکس برای ارسال متن به پنجره فعال
        self.send_to_active_window_checkbox = QCheckBox('ارسال متن به پنجره فعال', self)
        layout.addWidget(self.send_to_active_window_checkbox)

        # تنظیمات ویجت مرکزی
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # متد برای شروع و توقف ضبط صدا
    def toggle_recording(self):
        if self.start_stop_button.isChecked():
            self.start_stop_button.setText('توقف ضبط')
            self.speech_thread.start()
        else:
            self.start_stop_button.setText('شروع ضبط')
            self.speech_thread.stop()

    # متد برای نمایش متن تشخیص داده شده
    def display_text(self, text):
        self.textEdit.append(text)
        if self.send_to_active_window_checkbox.isChecked():
            pyperclip.copy(f' {text}')
            active_window = gw.getActiveWindow()
            if active_window:
                active_window.activate()
                time.sleep(0.5)  # تأخیر کوچک برای اطمینان از فعال شدن پنجره
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)  # تأخیر کوچک برای اطمینان از انجام عملیات پیست

    # متد برای به‌روزرسانی وضعیت شنیدن
    def update_listening_status(self, listening):
        if listening:
            self.status_label.setText("وضعیت: شنیدن...")
            self.status_indicator.setStyleSheet("background-color: green; border-radius: 10px;")
        else:
            self.status_label.setText("وضعیت: عدم شنیدن")
            self.status_indicator.setStyleSheet("background-color: red; border-radius: 10px;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = SpeechToTextApp()
    mainWindow.show()
    sys.exit(app.exec_())
