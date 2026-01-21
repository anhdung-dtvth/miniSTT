import customtkinter as ctk
import os
import threading
import tkinter.messagebox as messagebox
import winsound
import pygame
import time
from src import core, utils

# Configuration
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

MODELS_DIR = os.path.join(os.getcwd(), "models")
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

LANGUAGES = {
    "Tự động nhận diện": "Auto",
    "Tiếng Việt": "vi",
    "Tiếng Anh": "en",
    "Tiếng Nhật": "ja",
    "Tiếng Hàn": "ko",
    "Tiếng Trung": "zh"
}

MODEL_SIZES = {
    "Máy phế (Tiny - Nhanh nhất)": "tiny",
    "Máy cùi (Base)": "base",
    "Máy vừa (Small)": "small",
    "Máy xịn (Medium - Chuẩn hơn)": "medium",
    "Máy khủng (Large - Chậm nhất)": "large"
}

class AudioPlayerFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Audio State
        pygame.mixer.init()
        self.playing = False
        self.audio_path = None
        self.duration = 0
        self.update_job = None
        
        # Grid Layout
        self.grid_columnconfigure(1, weight=1)
        
        # 1. Play Button
        self.play_btn = ctk.CTkButton(self, text="▶", width=40, command=self.toggle_play, font=("Roboto", 16, "bold"))
        self.play_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # 2. Slider
        self.slider = ctk.CTkSlider(self, from_=0, to=100, command=self.on_seek)
        self.slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.slider.set(0)
        
        # 3. Time Label
        self.time_label = ctk.CTkLabel(self, text="00:00 / 00:00", font=("Roboto", 12))
        self.time_label.grid(row=0, column=2, padx=10, pady=10)
        
    def load_audio(self, path):
        self.audio_path = path
        try:
            pygame.mixer.music.load(path)
            # Estimate duration using Sound (loads entire file, not ideal for huge files but ok here)
            # For MP3 compatibility, sometimes Sound works better for length
            try:
                sound = pygame.mixer.Sound(path)
                self.duration = sound.get_length()
            except:
                self.duration = 0 # Fallback
                
            self.slider.configure(to=self.duration)
            self.update_time_label(0)
            self.playing = False
            self.play_btn.configure(text="▶")
        except Exception as e:
            print(f"Error loading audio: {e}")

    def toggle_play(self):
        if not self.audio_path:
            return
            
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False
            self.play_btn.configure(text="▶")
        else:
            if pygame.mixer.music.get_pos() < 0: # Not started
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            self.playing = True
            self.play_btn.configure(text="⏸")
            self.update_progress()
            
    def stop(self):
        if self.playing:
             pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self.playing = False
        self.audio_path = None
        self.play_btn.configure(text="▶")
        self.slider.set(0)
        self.time_label.configure(text="00:00 / 00:00")

    def on_seek(self, value):
        if not self.audio_path:
            return
        # pygame music play start is in seconds
        pygame.mixer.music.play(start=float(value))
        self.playing = True
        self.play_btn.configure(text="⏸")
        self.update_progress()

    def update_progress(self):
        if not self.playing:
            return
        pass 

    def format_time(self, seconds):
        if seconds is None: seconds = 0
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02}:{secs:02}"
        
    def update_time_label(self, current_sec):
        total_str = self.format_time(self.duration)
        curr_str = self.format_time(current_sec)
        self.time_label.configure(text=f"{curr_str} / {total_str}")
        
    def seek(self, second):
        if not self.audio_path: return
        self.slider.set(second)
        self.on_seek(second)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Mini Speech-to-Text Pro 🎙️")
        self.geometry("1100x750")
        
        # Font Configuration
        self.header_font = ctk.CTkFont(family="Roboto", size=20, weight="bold")
        self.label_font = ctk.CTkFont(family="Roboto", size=14)
        self.label_bold_font = ctk.CTkFont(family="Roboto", size=14, weight="bold")
        self.button_font = ctk.CTkFont(family="Roboto", size=14, weight="bold")
        self.text_font = ctk.CTkFont(family="Roboto", size=14)

        # Layout Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) 

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Mini STT Tool", font=self.header_font)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Model Selection
        self.model_label = ctk.CTkLabel(self.sidebar_frame, text="Kích thước Model:", anchor="w", font=self.label_bold_font)
        self.model_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.model_option = ctk.CTkOptionMenu(self.sidebar_frame, values=list(MODEL_SIZES.keys()), font=self.label_font)
        self.model_option.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Language Selection
        self.lang_label = ctk.CTkLabel(self.sidebar_frame, text="Ngôn ngữ:", anchor="w", font=self.label_bold_font)
        self.lang_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.lang_option = ctk.CTkOptionMenu(self.sidebar_frame, values=list(LANGUAGES.keys()), font=self.label_font)
        self.lang_option.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Buttons
        self.open_data_btn = ctk.CTkButton(self.sidebar_frame, text="📂 Mở Data", command=self.open_data_folder, font=self.button_font)
        self.open_data_btn.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        self.delete_data_btn = ctk.CTkButton(self.sidebar_frame, text="🗑️ Xóa Data", fg_color="red", hover_color="darkred", command=self.delete_data, font=self.button_font)
        self.delete_data_btn.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")

        # --- Main Area ---
        self.tabview = ctk.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Transcribe")
        self.tabview.add("Editor")
        
        # Tabs
        self.setup_transcribe_tab()
        self.setup_editor_tab()
        
        # App State
        self.loaded_model = None
        self.current_model_code = None
        self.processing = False
        
        # Handle close for pygame
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_transcribe_tab(self):
        self.tab_transcribe = self.tabview.tab("Transcribe")
        
        # File selector
        self.file_label = ctk.CTkLabel(self.tab_transcribe, text="Drop file here or click 'Select'", height=40, font=("Roboto", 14), fg_color=("gray85", "gray25"), corner_radius=8)
        self.file_label.pack(fill="x", padx=10, pady=(10, 0))
        
        self.select_btn = ctk.CTkButton(self.tab_transcribe, text="📁 Chọn File Audio", command=self.select_file, font=self.button_font)
        self.select_btn.pack(pady=10)
        
        # Start Button
        self.start_btn = ctk.CTkButton(self.tab_transcribe, text="🚀 Bắt đầu Transcribe", font=ctk.CTkFont(family="Roboto", size=16, weight="bold"), height=40, command=self.start_transcription)
        self.start_btn.pack(pady=10)
        
        # Audio Player Frame (Initially hidden)
        self.audio_player = AudioPlayerFrame(self.tab_transcribe)
        # self.audio_player.pack(fill="x", padx=10, pady=5) 
        
        # Status
        self.status_label = ctk.CTkLabel(self.tab_transcribe, text="", font=("Roboto", 12))
        self.status_label.pack(pady=(0, 5))
        
        # Scrollable Transcript Area (Initially hidden)
        self.transcript_scroll = ctk.CTkScrollableFrame(self.tab_transcribe, label_text="Kết quả")
        # self.transcript_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_editor_tab(self):
        self.tab_editor = self.tabview.tab("Editor")
        self.tab_editor.grid_columnconfigure(0, weight=1)
        
        self.refresh_btn = ctk.CTkButton(self.tab_editor, text="🔄 Làm mới danh sách", command=self.refresh_sessions, font=self.button_font)
        self.refresh_btn.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.session_option = ctk.CTkOptionMenu(self.tab_editor, values=["Chưa có dữ liệu"], font=self.label_font)
        self.session_option.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.load_session_btn = ctk.CTkButton(self.tab_editor, text="Load Session", command=self.load_session, font=self.button_font)
        self.load_session_btn.grid(row=2, column=0, padx=20, pady=10)
        
        self.editor_frame = ctk.CTkScrollableFrame(self.tab_editor, label_text="Segments")
        # self.editor_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.tab_editor.grid_rowconfigure(3, weight=1)
        
        self.save_btn = ctk.CTkButton(self.tab_editor, text="Lưu Thay Đổi", fg_color="green", hover_color="darkgreen", command=self.save_editor, font=self.button_font)
        # self.save_btn.grid(row=4, column=0, padx=20, pady=20)

    # --- Actions ---
    def select_file(self):
        file_path = ctk.filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.m4a")])
        if file_path:
            self.selected_file = file_path
            self.file_label.configure(text=os.path.basename(file_path))
            
            # Show Player
            self.audio_player.pack(fill="x", padx=10, pady=5)
            # Re-pack status label to stay below player
            self.status_label.pack_forget()
            self.status_label.pack(pady=(0, 5))
            
            # Load into player immediately for preview
            self.audio_player.load_audio(file_path)

    def start_transcription(self):
        if not hasattr(self, 'selected_file'):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file trước!")
            return
            
        model_name = MODEL_SIZES[self.model_option.get()]
        lang_code = LANGUAGES[self.lang_option.get()]
        
        self.status_label.configure(text="Đang tải model và xử lý... (Vui lòng chờ)", text_color="orange")
        self.start_btn.configure(state="disabled")
        self.processing = True
        
        thread = threading.Thread(target=self.run_transcribe_thread, args=(model_name, lang_code, self.selected_file))
        thread.start()
        
    def run_transcribe_thread(self, model_size, lang, file_path):
        try:
            if self.current_model_code != model_size:
                # Pass MODELS_DIR here
                self.loaded_model = core.load_model(model_size, download_root=MODELS_DIR)
                self.current_model_code = model_size
            
            result = core.transcribe_audio(self.loaded_model, file_path, language=lang)
            segments = result["segments"]
            
            utils.save_segments_to_folder(file_path, segments)
            
            # Show Transcript Area
            self.transcript_scroll.pack(fill="both", expand=True, padx=10, pady=10)
            
            for widget in self.transcript_scroll.winfo_children():
                widget.destroy()

            for s in segments:
                row_frame = ctk.CTkFrame(self.transcript_scroll, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
                
                start_time = s["start"]
                time_str = utils.format_time(start_time)
                
                btn = ctk.CTkButton(
                    row_frame, 
                    text=f"[{time_str}]", 
                    width=80, 
                    font=self.button_font,
                    command=lambda t=start_time: self.audio_player.seek(t)
                )
                btn.pack(side="left", padx=(0, 10))
                # Text - Use Entry for consistency with Editor
                entry = ctk.CTkEntry(row_frame, font=self.text_font)
                entry.insert(0, s["text"].strip())
                # Make it read-only so users don't think they can edit here (unless we add save feature)
                # But for pure visual match with Editor, we might leave it normal. 
                # Let's keep it normal state so they can copy text easily.
                entry.pack(side="left", fill="x", expand=True, padx=5)

            self.status_label.configure(text="✅ Hoàn tất!", text_color="green")
            
        except Exception as e:
            self.status_label.configure(text=f"❌ Lỗi: {str(e)}", text_color="red")
            print(e)
        finally:
            self.start_btn.configure(state="normal")
            self.processing = False

    def open_data_folder(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        os.startfile("data")

    def delete_data(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa toàn bộ dữ liệu (data và temp)?"):
            if utils.delete_all_data():
                 # UI Cleanup Logic
                 self.audio_player.stop()
                 if hasattr(self, 'selected_file'):
                     del self.selected_file
                 self.file_label.configure(text="Drop file here or click 'Select'")
                 self.status_label.configure(text="")
                 
                 for widget in self.transcript_scroll.winfo_children():
                     widget.destroy()
                 
                 # Hide Widgets
                 self.audio_player.pack_forget()
                 self.transcript_scroll.pack_forget()
                 self.editor_frame.grid_forget()
                 self.save_btn.grid_forget()
                     
                 messagebox.showinfo("Thông báo", "Đã xóa thành công!")
                 self.refresh_sessions()
            else:
                 messagebox.showerror("Lỗi", "Có lỗi xảy ra khi xóa!")

    def refresh_sessions(self):
        if not os.path.exists("data"):
            sessions = []
        else:
            sessions = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]
        
        if not sessions:
            self.session_option.configure(values=["Trống"])
            self.session_option.set("Trống")
        else:
            self.session_option.configure(values=sessions)
            self.session_option.set(sessions[0])

    def load_session(self):
        session_name = self.session_option.get()
        if session_name == "Trống" or not session_name:
            return
            
        session_path = os.path.join("data", session_name)
        self.current_session_data = utils.load_session_data(session_path)
        self.current_session_path = session_path
        
        # Show Widgets
        self.editor_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.save_btn.grid(row=4, column=0, padx=20, pady=20)
        
        for widget in self.editor_frame.winfo_children():
            widget.destroy()
            
        self.editor_entries = []
        
        for i, row in enumerate(self.current_session_data):
            row_frame = ctk.CTkFrame(self.editor_frame)
            row_frame.pack(fill="x", padx=5, pady=5)
            
            filename = row.get('filename', row.get('audio_file', ''))
            audio_path = os.path.join(session_path, filename)
            
            def play_audio(path=audio_path):
                if os.path.exists(path):
                    winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                else:
                    messagebox.showerror("Lỗi", "File audio không tồn tại")

            play_btn = ctk.CTkButton(row_frame, text=f"▶ Seg {i+1}", width=60, command=play_audio, font=self.button_font)
            play_btn.pack(side="left", padx=5)
            
            text_val = row.get('transcription', row.get('transcript', ''))
            entry = ctk.CTkEntry(row_frame, font=self.text_font)
            entry.insert(0, text_val)
            entry.pack(side="left", fill="x", expand=True, padx=5)
            
            self.editor_entries.append({"row": row, "entry": entry})

    def save_editor(self):
        if not hasattr(self, 'current_session_path'):
            return
        updated_data = []
        for item in self.editor_entries:
            row = item['row']
            new_text = item['entry'].get()
            row['transcription'] = new_text
            if 'filename' not in row and 'audio_file' in row:
                row['filename'] = row['audio_file']
            updated_data.append(row)
            
        utils.update_transcript(self.current_session_path, updated_data)
        messagebox.showinfo("Thành công", "Đã lưu thay đổi!")
        
    def on_close(self):
        pygame.mixer.quit()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
