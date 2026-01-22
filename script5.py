"""
═══════════════════════════════════════════════════════════════════
    FLOREMOTION-LEX-MEDICAL - SISTEM EXPERT BIOMETRIC
    Medic Examinator: Constantin Gina Florentina
    Specialitate: Medic Legist - Expert Biometric
    Tehnologie: Deep Learning (VGG-Face)
═══════════════════════════════════════════════════════════════════
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import cv2
from deepface import DeepFace
import os
import threading
from datetime import datetime

# PALETA DE CULORI CLINICĂ PREMIUM (DESCHISĂ)
C_BGE = "#F9F7F2"  # Fundal crem pal
C_GOLD = "#B08D57"  # Auriu mat (Juridic/Lex)
C_WHITE = "#FFFFFF"
C_TEXT = "#2C3E50"
C_ACCENT = "#E8F0FE"  # Albastru medical deschis


class EmotionDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FLOREMOTION-LEX-MEDICAL | Cabinet Medic Legist")
        self.root.geometry("1100x820")
        self.root.configure(bg=C_BGE)
        self.root.resizable(False, False)

        # Păstrarea variabilelor originale
        self.image_path = None
        self.original_image = None
        self.processing = False

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """Centrează fereastra conform standardelor desktop"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # HEADER MEDICAL OFICIAL
        header_frame = tk.Frame(self.root, bg=C_WHITE, height=135, bd=0,
                                highlightbackground=C_GOLD, highlightthickness=1)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="FLOREMOTION-LEX-MEDICAL",
                 font=('Times New Roman', 28, 'bold'), bg=C_WHITE, fg=C_GOLD).pack(pady=(15, 0))

        tk.Label(header_frame, text="Medic Legist: Constantin Gina Florentina",
                 font=('Arial', 11, 'bold'), bg=C_WHITE, fg=C_TEXT).pack()

        tk.Label(header_frame, text="Sistem Expert Biometric de Analiză Neuronală Forensiс",
                 font=('Arial', 9, 'italic'), bg=C_WHITE, fg="#7F8C8D").pack()

        # TOOLBAR (Butoane stilizate)
        toolbar_frame = tk.Frame(self.root, bg=C_BGE, height=90)
        toolbar_frame.pack(fill='x', pady=10)

        btn_style = {'font': ('Arial', 10, 'bold'), 'fg': 'white', 'padx': 20, 'pady': 10,
                     'relief': 'flat', 'cursor': 'hand2'}

        self.load_btn = tk.Button(toolbar_frame, text="📥 ÎNCARCĂ PROBĂ",
                                  command=self.load_image, bg=C_GOLD, **btn_style)
        self.load_btn.pack(side='left', padx=25)

        self.detect_btn = tk.Button(toolbar_frame, text="🔍 ANALIZĂ FORENSICĂ",
                                    command=self.detect_emotion_threaded, bg="#4A69BD",
                                    state='disabled', **btn_style)
        self.detect_btn.pack(side='left', padx=5)

        self.save_btn = tk.Button(toolbar_frame, text="💾 GENEREAZĂ RAPORT",
                                  command=self.save_result, bg="#27AE60",
                                  state='disabled', **btn_style)
        self.save_btn.pack(side='left', padx=5)

        self.clear_btn = tk.Button(toolbar_frame, text="🗑️ RESETARE",
                                   command=self.clear_all, bg="#E74C3C", **btn_style)
        self.clear_btn.pack(side='right', padx=25)

        # MAIN CONTENT
        main_frame = tk.Frame(self.root, bg=C_BGE)
        main_frame.pack(pady=5, padx=25, fill='both', expand=True)

        # ZONA IMAGINE (STÂNGA)
        image_frame = tk.LabelFrame(main_frame, text=" EXAMINARE PROBĂ ",
                                    font=('Arial', 10, 'bold'), bg=C_WHITE, fg=C_GOLD, bd=1)
        image_frame.pack(side='left', padx=10, fill='both', expand=True)

        self.image_label = tk.Label(image_frame, text="Așteptare document vizual medical...",
                                    font=('Arial', 10), bg=C_WHITE, fg="#95A5A6")
        self.image_label.pack(pady=30, padx=20, expand=True)

        # ZONA REZULTATE (DREAPTA)
        result_frame = tk.LabelFrame(main_frame, text=" VERDICT BIOMETRIC ",
                                     font=('Arial', 10, 'bold'), bg=C_WHITE, fg=C_GOLD, bd=1)
        result_frame.pack(side='right', padx=10, fill='both', expand=True)

        res_inner = tk.Frame(result_frame, bg=C_WHITE)
        res_inner.pack(fill='both', expand=True, pady=10)

        # Rezultat principal
        self.emotion_label = tk.Label(res_inner, text="-", font=('Times New Roman', 26, 'bold'),
                                      bg=C_ACCENT, fg=C_TEXT)
        self.emotion_label.pack(pady=10, padx=20, fill='x')

        self.emoji_label = tk.Label(res_inner, text="", font=('Arial', 55), bg=C_WHITE)
        self.emoji_label.pack()

        self.confidence_label = tk.Label(res_inner, text="Încredere: -",
                                         font=('Arial', 12, 'bold'), bg=C_WHITE, fg=C_GOLD)
        self.confidence_label.pack(pady=5)

        # Zona pentru bare de probabilitate
        self.prob_frame = tk.Frame(res_inner, bg=C_WHITE)
        self.prob_frame.pack(pady=20, padx=20, fill='both', expand=True)

        # STATUS BAR
        self.status_label = tk.Label(self.root, text="📌 Sistem securizat pregătit pentru expertiză legală.",
                                     font=('Arial', 9), bg=C_GOLD, fg="white", anchor='w', padx=15)
        self.status_label.pack(fill='x', side='bottom')

    def load_image(self):
        """Încarcă fotografia conform parametrilor originali"""
        file_path = filedialog.askopenfilename(title="Selectare Probă Judiciară",
                                               filetypes=[("Imagini", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            try:
                self.image_path = file_path
                image = Image.open(file_path)
                self.original_image = image.copy()
                display_image = self.resize_image(image, max_width=450, max_height=450)
                photo = ImageTk.PhotoImage(display_image)
                self.image_label.configure(image=photo, text="")
                self.image_label.image = photo
                self.detect_btn.config(state='normal')
                self.reset_results()
                self.status_label.config(text=f"📌 Probă recepționată: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la recepția probei: {str(e)}")

    def resize_image(self, image, max_width, max_height):
        """Redimensionare cu păstrarea calității"""
        width, height = image.size
        ratio = min(max_width / width, max_height / height)
        return image.resize((int(width * ratio), int(height * ratio)), Image.Resampling.LANCZOS)

    def detect_emotion_threaded(self):
        if not self.processing:
            threading.Thread(target=self.detect_emotion, daemon=True).start()

    def detect_emotion(self):
        """Procesare prin rețele neuronale convoluționale"""
        self.processing = True
        try:
            self.status_label.config(text="⏳ Procesare neuronală DeepFace în curs...")
            self.detect_btn.config(state='disabled')

            result = DeepFace.analyze(img_path=self.image_path, actions=['emotion'],
                                      enforce_detection=False, detector_backend='opencv')
            if isinstance(result, list): result = result[0]

            emotion = result['dominant_emotion']
            emotions_prob = result['emotion']

            emotion_ro = {'angry': 'Furie', 'disgust': 'Dezgust', 'fear': 'Frică',
                          'happy': 'Bucurie', 'sad': 'Tristețe', 'surprise': 'Surpriză', 'neutral': 'Neutru'}
            emotion_emoji = {'angry': '😠', 'disgust': '🤢', 'fear': '😨', 'happy': '😊',
                             'sad': '😢', 'surprise': '😲', 'neutral': '😐'}

            self.emotion_label.config(text=emotion_ro.get(emotion, emotion).upper())
            self.emoji_label.config(text=emotion_emoji.get(emotion, ''))
            self.confidence_label.config(text=f"Încredere: {emotions_prob[emotion]:.1f}%")

            self.show_probabilities(emotions_prob, emotion_ro)
            self.save_btn.config(state='normal')
            self.status_label.config(text="✅ Expertiză biometrică finalizată cu succes.")
        except Exception as e:
            messagebox.showerror("Eroare Tehnică", f"Analiza a eșuat: {str(e)}")
        finally:
            self.processing = False
            self.detect_btn.config(state='normal')

    def show_probabilities(self, probabilities, emotion_ro):
        for widget in self.prob_frame.winfo_children(): widget.destroy()
        sorted_emotions = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)

        for emotion, prob in sorted_emotions:
            row = tk.Frame(self.prob_frame, bg=C_WHITE)
            row.pack(fill='x', pady=3)
            tk.Label(row, text=f"{emotion_ro.get(emotion, emotion)}:",
                     font=('Arial', 9, 'bold'), bg=C_WHITE, width=12, anchor='w').pack(side='left')

            canvas = tk.Canvas(row, width=200, height=14, bg=C_ACCENT, highlightthickness=0)
            canvas.pack(side='left', padx=10)
            canvas.create_rectangle(0, 0, int(prob * 2), 14, fill=C_GOLD, outline='')
            tk.Label(row, text=f"{prob:.1f}%", font=('Arial', 9, 'bold'), bg=C_WHITE).pack(side='left')

    def save_result(self):
        """Generare raport oficial semnat"""
        save_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 title="Salvare Raport Oficial FLOREMOTION-LEX")
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(f"RAPORT EXPERTIZĂ BIOMETRICĂ - FLOREMOTION-LEX-MEDICAL\n")
                f.write(f"Medic Examinator: Constantin Gina Florentina\n")
                f.write(f"Calitate: Medic Legist - Expert Biometric\n")
                f.write(f"Data Analizei: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Probă Analizată: {os.path.basename(self.image_path)}\n")
                f.write(f"Verdict Final: {self.emotion_label.cget('text')}\n")
            messagebox.showinfo("Salvare Reușită", "Raportul oficial a fost generat și salvat.")

    def reset_results(self):
        self.emotion_label.config(text="-")
        self.emoji_label.config(text="")
        self.confidence_label.config(text="Încredere: -")
        for widget in self.prob_frame.winfo_children(): widget.destroy()

    def clear_all(self):
        self.image_path = None
        self.image_label.config(image='', text="Așteptare document vizual medical...")
        self.reset_results()
        self.detect_btn.config(state='disabled')
        self.save_btn.config(state='disabled')
        self.status_label.config(text="📌 Sistem resetat. Gata pentru o nouă expertiză.")


if __name__ == "__main__":
    root = tk.Tk()
    app = EmotionDetectorApp(root)
    root.mainloop()

