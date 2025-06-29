import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import queue
import sounddevice as sd
import vosk
import wave
import json
import os
from docx import Document
from fpdf import FPDF
import pyperclip
import numpy as np
from scipy.io import wavfile
import noisereduce as nr
import arabic_reshaper
from bidi.algorithm import get_display

class RealTimeTranscriber:
    def __init__(self, root):
        self.root = root
        self.root.title("سخن‌نگار - تبدیل گفتار به متن")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        model_path = "model/vosk-model-small-fa-0.42"
        if not os.path.exists(model_path):
            messagebox.showerror("خطا", f"مدل Vosk در مسیر {model_path} یافت نشد. لطفاً مدل را دانلود کنید.")
            raise Exception(f"Vosk model not found at {model_path}")
        self.model = vosk.Model(model_path)
        self.sample_rate = 16000

        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.transcribed_text = ""

        self.setup_gui()

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        self.text_box = tk.Text(main_frame, height=20, width=90, wrap="word", font=("Arial", 12))
        self.text_box.pack(pady=10, fill="both", expand=True)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=5)

        self.start_button = ttk.Button(control_frame, text="شروع ضبط", command=self.start_listening)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(control_frame, text="توقف ضبط", command=self.stop_listening, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=5)

        ttk.Button(control_frame, text="بارگذاری فایل صوتی", command=self.load_audio_file).grid(row=0, column=2, padx=5)

        ttk.Label(control_frame, text="زبان:").grid(row=0, column=3, padx=5)
        self.lang_var = tk.StringVar(value="fa-IR")
        lang_menu = ttk.OptionMenu(control_frame, self.lang_var, "fa-IR", "fa-IR", "en-US")
        lang_menu.grid(row=0, column=4, padx=5)

        save_frame = ttk.Frame(main_frame)
        save_frame.pack(pady=5)
        ttk.Button(save_frame, text="ذخیره TXT", command=lambda: self.save_file("txt")).grid(row=0, column=0, padx=5)
        ttk.Button(save_frame, text="ذخیره DOCX", command=lambda: self.save_file("docx")).grid(row=0, column=1, padx=5)
        ttk.Button(save_frame, text="ذخیره PDF", command=lambda: self.save_file("pdf")).grid(row=0, column=2, padx=5)
        ttk.Button(save_frame, text="کپی به کلیپ‌بورد", command=self.copy_to_clipboard).grid(row=0, column=3, padx=5)

        self.status_var = tk.StringVar(value="آماده")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")

    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_var.set("در حال ضبط...")
            threading.Thread(target=self._audio_callback, daemon=True).start()
            threading.Thread(target=self._process_audio, daemon=True).start()

    def stop_listening(self):
        self.is_listening = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_var.set("متوقف شده")

    def _audio_callback(self):
        def callback(indata, frames, time, status):
            if self.is_listening:
                self.audio_queue.put(indata.copy())

        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16', callback=callback):
            while self.is_listening:
                sd.sleep(100)

    def _process_audio(self):
        rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
        while self.is_listening:
            try:
                data = self.audio_queue.get(timeout=1)
                reduced_noise = nr.reduce_noise(y=data.flatten(), sr=self.sample_rate)
                audio_data = reduced_noise.astype(np.int16).tobytes()
                if rec.AcceptWaveform(audio_data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if text:
                        self.transcribed_text += text + " "
                        self.text_box.delete(1.0, tk.END)
                        self.text_box.insert(tk.END, self.transcribed_text)
                else:
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get("partial", "")
                    if partial_text:
                        self.text_box.delete(1.0, tk.END)
                        self.text_box.insert(tk.END, self.transcribed_text + partial_text)
            except queue.Empty:
                continue

    def load_audio_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.aac")])
        if file_path:
            self.status_var.set("در حال پردازش فایل صوتی...")
            threading.Thread(target=self._transcribe_file, args=(file_path,), daemon=True).start()

    def _transcribe_file(self, file_path):
        try:
            if file_path.endswith(".wav"):
                wf = wave.open(file_path, "rb")
            else:
                wf = self._convert_to_wav(file_path)
                if not os.path.exists("temp.wav"):
                    raise FileNotFoundError("تبدیل فایل به WAV ناموفق بود. لطفاً FFmpeg را نصب کنید.")
            
            rec = vosk.KaldiRecognizer(self.model, wf.getframerate())
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if text:
                        self.transcribed_text += text + " "
                        self.text_box.delete(1.0, tk.END)
                        self.text_box.insert(tk.END, self.transcribed_text)
            wf.close()
            if not file_path.endswith(".wav"):
                os.remove("temp.wav")
            self.status_var.set("پردازش فایل تکمیل شد")
        except Exception as e:
            self.status_var.set("خطا در پردازش فایل")
            messagebox.showerror("خطا", f"خطا در پردازش فایل صوتی: {str(e)}")

    def _convert_to_wav(self, file_path):
        output_path = "temp.wav"
        ffmpeg_cmd = f"ffmpeg -i \"{file_path}\" -ar 16000 -ac 1 \"{output_path}\" -y"
        result = os.system(ffmpeg_cmd)
        if result != 0:
            raise RuntimeError("FFmpeg نصب نشده یا خطا در تبدیل فایل رخ داده است.")
        return wave.open(output_path, "rb")

    def save_file(self, file_type):
        if not self.transcribed_text.strip():
            messagebox.showwarning("هشدار", "متن برای ذخیره وجود ندارد!")
            return
        filename = filedialog.asksaveasfilename(defaultextension=f".{file_type}", filetypes=[(file_type.upper(), f".{file_type}")])
        if filename:
            try:
                if file_type == "txt":
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(self.transcribed_text)
                elif file_type == "docx":
                    doc = Document()
                    doc.add_paragraph(self.transcribed_text)
                    doc.save(filename)
                elif file_type == "pdf":
                    pdf = FPDF()
                    pdf.add_page()
                    font_path = "DejaVuSans.ttf"
                    if not os.path.exists(font_path):
                        messagebox.showerror("خطا", "فونت DejaVuSans.ttf یافت نشد. لطفاً آن را دانلود کنید.")
                        return
                    pdf.add_font("DejaVu", "", font_path, uni=True)
                    pdf.set_font("DejaVu", size=12)
                    reshaped_text = arabic_reshaper.reshape(self.transcribed_text)
                    bidi_text = get_display(reshaped_text)
                    pdf.multi_cell(0, 10, bidi_text)
                    pdf.output(filename)
                messagebox.showinfo("موفقیت", f"فایل در {filename} ذخیره شد.")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در ذخیره فایل: {str(e)}")

    def copy_to_clipboard(self):
        if self.transcribed_text.strip():
            pyperclip.copy(self.transcribed_text)
            messagebox.showinfo("موفقیت", "متن به کلیپ‌بورد کپی شد.")
        else:
            messagebox.showwarning("هشدار", "متن برای کپی وجود ندارد!")

    def insert_symbol(self, symbol):
        self.text_box.insert(tk.END, symbol)

def main():
    root = tk.Tk()
    app = RealTimeTranscriber(root)
    root.mainloop()

if __name__ == "__main__":
    main()
