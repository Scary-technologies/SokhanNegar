import tkinter as tk
from tkinter import scrolledtext, messagebox
import speech_recognition as sr
import threading
import queue
import time

class SokhanNegarLive:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("سخن نگار  ")
        self.root.geometry("500x400")
        self.root.configure(bg='#1e1e1e')
        self.root.resizable(True, True)
        
        # تنظیمات
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.audio_queue = queue.Queue()
        
        # تنظیم میکروفون
        self.setup_microphone()
        
        # ایجاد رابط کاربری
        self.create_ui()
        
        # شروع thread گوش دادن
        self.listen_thread = None
    
    def setup_microphone(self):
        """تنظیم میکروفون"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.recognizer.energy_threshold = 4000
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8
                self.recognizer.phrase_threshold = 0.3
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در تنظیم میکروفون: {str(e)}")
    
    def create_ui(self):
        """ایجاد رابط کاربری مینیمال"""
        # عنوان و دکمه
        header_frame = tk.Frame(self.root, bg='#1e1e1e')
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # عنوان برنامه
        title_label = tk.Label(header_frame, text="سخن نگار  ", 
                              font=('Segoe UI', 16, 'bold'), 
                              fg='#ffffff', bg='#1e1e1e')
        title_label.pack(side=tk.LEFT)
        
        # دکمه شروع/توقف
        self.toggle_button = tk.Button(header_frame, text="▶ شروع", 
                                      command=self.toggle_listening,
                                      bg='#4CAF50', fg='white', 
                                      font=('Segoe UI', 12, 'bold'),
                                      relief=tk.FLAT, padx=20, pady=8,
                                      cursor='hand2')
        self.toggle_button.pack(side=tk.RIGHT)
        
        # وضعیت
        self.status_label = tk.Label(self.root, text="● غیرفعال", 
                                    font=('Segoe UI', 10), 
                                    fg='#888888', bg='#1e1e1e')
        self.status_label.pack(padx=15, anchor=tk.W)
        
        # ناحیه متن
        text_frame = tk.Frame(self.root, bg='#1e1e1e')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10, 15))
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            font=('Segoe UI', 12),
            wrap=tk.WORD,
            bg='#2d2d2d',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief=tk.FLAT,
            padx=15,
            pady=15,
            selectbackground='#404040',
            selectforeground='#ffffff',
            borderwidth=0
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # دکمه‌های کوچک در پایین
        bottom_frame = tk.Frame(self.root, bg='#1e1e1e')
        bottom_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        clear_btn = tk.Button(bottom_frame, text="پاک کردن", 
                             command=self.clear_text,
                             bg='#333333', fg='#cccccc', 
                             font=('Segoe UI', 9),
                             relief=tk.FLAT, padx=15, pady=5,
                             cursor='hand2')
        clear_btn.pack(side=tk.LEFT)
        
        copy_btn = tk.Button(bottom_frame, text="کپی", 
                            command=self.copy_text,
                            bg='#333333', fg='#cccccc', 
                            font=('Segoe UI', 9),
                            relief=tk.FLAT, padx=15, pady=5,
                            cursor='hand2')
        copy_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # راهنما
        help_label = tk.Label(bottom_frame, 
                             text="با میکروفون صحبت کنید، متن به صورت زنده نمایش داده می‌شود", 
                             font=('Segoe UI', 8), 
                             fg='#666666', bg='#1e1e1e')
        help_label.pack(side=tk.RIGHT)
        
        # کلیدهای میانبر
        self.root.bind('<Control-Return>', lambda e: self.toggle_listening())
        self.root.bind('<Control-c>', lambda e: self.copy_text())
        self.root.bind('<Control-l>', lambda e: self.clear_text())
        
        # بستن برنامه
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def toggle_listening(self):
        """شروع/توقف گوش دادن"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        """شروع گوش دادن مداوم"""
        self.is_listening = True
        self.toggle_button.config(text="⏸ توقف", bg='#f44336')
        self.status_label.config(text="● در حال گوش دادن...", fg='#4CAF50')
        
        # شروع thread گوش دادن
        self.listen_thread = threading.Thread(target=self.listen_continuously)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
        # شروع thread پردازش
        self.process_thread = threading.Thread(target=self.process_audio_queue)
        self.process_thread.daemon = True
        self.process_thread.start()
    
    def stop_listening(self):
        """توقف گوش دادن"""
        self.is_listening = False
        self.toggle_button.config(text="▶ شروع", bg='#4CAF50')
        self.status_label.config(text="● متوقف شده", fg='#888888')
    
    def listen_continuously(self):
        """گوش دادن مداوم در background"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    # گوش دادن برای صدا
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                if self.is_listening:
                    # اضافه کردن به صف پردازش
                    self.audio_queue.put(audio)
                    
            except sr.WaitTimeoutError:
                # ادامه گوش دادن اگر timeout شد
                continue
            except Exception as e:
                if self.is_listening:
                    print(f"خطا در گوش دادن: {e}")
                break
    
    def process_audio_queue(self):
        """پردازش صف صداها"""
        while self.is_listening:
            try:
                # گرفتن صدا از صف
                audio = self.audio_queue.get(timeout=1)
                
                # تبدیل به متن
                self.root.after(0, self.update_status, "در حال پردازش...")
                
                text = self.recognizer.recognize_google(audio, language='fa-IR')
                
                if text.strip():
                    # اضافه کردن متن به ناحیه متن
                    self.root.after(0, self.add_text, text)
                    self.root.after(0, self.update_status, "● در حال گوش دادن...")
                
            except queue.Empty:
                continue
            except sr.UnknownValueError:
                # اگر نتوانست تشخیص دهد، ادامه بده
                continue
            except sr.RequestError as e:
                self.root.after(0, self.update_status, f"خطا در سرویس: {e}")
                time.sleep(2)
                self.root.after(0, self.update_status, "● در حال گوش دادن...")
            except Exception as e:
                print(f"خطا در پردازش: {e}")
                continue
    
    def add_text(self, text):
        """اضافه کردن متن جدید"""
        current_text = self.text_area.get("1.0", tk.END).strip()
        
        if current_text:
            self.text_area.insert(tk.END, " " + text)
        else:
            self.text_area.insert(tk.END, text)
        
        # اسکرول به انتها
        self.text_area.see(tk.END)
        
        # فلاش کوتاه برای نشان دادن متن جدید
        self.text_area.config(bg='#404040')
        self.root.after(200, lambda: self.text_area.config(bg='#2d2d2d'))
    
    def update_status(self, message):
        """به‌روزرسانی وضعیت"""
        self.status_label.config(text=message)
    
    def clear_text(self):
        """پاک کردن متن"""
        self.text_area.delete("1.0", tk.END)
    
    def copy_text(self):
        """کپی متن"""
        text = self.text_area.get("1.0", tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.update_status("● متن کپی شد")
            self.root.after(2000, lambda: self.update_status("● در حال گوش دادن..." if self.is_listening else "● غیرفعال"))
    
    def on_closing(self):
        """بستن برنامه"""
        self.is_listening = False
        time.sleep(0.5)  # زمان برای توقف thread ها
        self.root.destroy()
    
    def run(self):
        """اجرای برنامه"""
        self.root.mainloop()

def main():
    """تابع اصلی"""
    try:
        # بررسی نصب speech_recognition
        import speech_recognition as sr
        
        app = SokhanNegarLive()
        app.run()
        
    except ImportError:
        print("خطا: کتابخانه speech_recognition نصب نشده است")
        print("برای نصب از دستور زیر استفاده کنید:")
        print("pip install speechrecognition pyaudio")
    except Exception as e:
        print(f"خطا در اجرای برنامه: {e}")

if __name__ == "__main__":
    main()