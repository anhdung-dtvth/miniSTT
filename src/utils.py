import os
import base64

def save_uploaded_file(uploaded_file):
    if not os.path.exists("temp"):
        os.makedirs("temp")
    temp_filename = os.path.join("temp", uploaded_file.name)
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_filename

def remove_file(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            pass

def delete_all_data(target_dirs=["data", "temp"]):
    if isinstance(target_dirs, str):
        target_dirs = [target_dirs]
        
    import shutil
    import stat
    import time
    
    def on_rm_error(func, path, exc_info):
        # Attempt to fix read-only files
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            # If it still fails, we want to know
             print(f"Failed to delete {path}: {e}")
             raise e
            
    success = True
    for d in target_dirs:
        if os.path.exists(d):
            try:
                shutil.rmtree(d, onerror=on_rm_error)
                # Small delay to ensure OS releases handles before recreating
                time.sleep(0.1)
                os.makedirs(d, exist_ok=True)
                
                # Double check if it's actually empty/fresh
                if len(os.listdir(d)) > 0:
                     print(f"Warning: {d} appears not empty after recreation.")
                     success = False

            except Exception as e:
                print(f"Error deleting {d}: {e}")
                success = False
                
    return success

def get_audio_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

# --- HÀM XỬ LÝ AUDIO MỚI ---
import csv

def save_segments_to_folder(original_audio_path, segments, output_dir="data"):
    from pydub import AudioSegment
    # 1. Tạo folder tên file audio
    base_name = os.path.splitext(os.path.basename(original_audio_path))[0]
    # Handle weird characters if necessary, but simple is ok for now
    session_dir = os.path.join(output_dir, base_name)
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)

    # 2. Xử lý audio gốc
    audio = AudioSegment.from_file(original_audio_path)
    
    metadata = []
    
    for i, segment in enumerate(segments):
        start_ms = segment["start"] * 1000
        end_ms = segment["end"] * 1000
        
        # Cắt audio
        clip = audio[start_ms:end_ms]
        
        # Lưu file segment
        segment_filename = f"segment_{i+1:03d}.wav"
        segment_path = os.path.join(session_dir, segment_filename)
        clip.export(segment_path, format="wav")
        
        # Lưu info
        metadata.append({
            "filename": segment_filename,
            "transcription": segment["text"].strip()
        })
        
    # 3. Lưu CSV
    csv_path = os.path.join(session_dir, "metadata.csv")
    with open(csv_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "transcription"])
        writer.writeheader()
        writer.writerows(metadata)
        
    return session_dir

def load_session_data(session_dir):
    csv_path = os.path.join(session_dir, "metadata.csv")
    if not os.path.exists(csv_path):
        return []
    
    data = []
    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def update_transcript(session_dir, csv_data):
    csv_path = os.path.join(session_dir, "metadata.csv")
    with open(csv_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "transcription"])
        writer.writeheader()
        writer.writerows(csv_data)

# --- HÀM TẠO GIAO DIỆN (Đã sửa logic CSS) ---
# src/utils.py

# ... (các đoạn code trên giữ nguyên) ...

def create_dashboard_html(file_path, segments, layout_mode="2col"):
    audio_base64 = get_audio_base64(file_path)
    
    # 1. Tạo danh sách hội thoại
    transcript_items = ""
    for segment in segments:
        start = segment["start"]
        time_str = format_time(start)
        text = segment["text"].strip()
        
        item = f"""
        <div class="transcript-row">
            <button class="seek-btn" onclick="seekTo({start})">▶ {time_str}</button>
            <span class="text">{text}</span>
        </div>
        """
        transcript_items += item

    # 2. XỬ LÝ CSS (Dùng mã code tiếng Anh để check)
    if layout_mode == "2col":
        # Giao diện 2 cột
        container_css = "display: flex; gap: 20px; height: 600px;" 
        player_css = "flex: 1; height: fit-content;"
        text_css = "flex: 2; height: auto; overflow-y: auto;" 
    else:
        # Giao diện 1 cột (layout_mode == "1col")
        container_css = "display: block; height: auto;"
        player_css = "width: auto; margin-bottom: 20px;"
        text_css = "width: auto; height: auto; overflow-y: visible;"

    # 3. Tạo HTML tổng hợp
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: sans-serif; margin: 0; padding: 0; }}
            .container {{ {container_css} }}
            .player-col {{ 
                padding: 15px; background: #f8f9fa; border-radius: 8px; border: 1px solid #ddd;
                {player_css}
            }}
            .text-col {{ 
                padding: 15px; border: 1px solid #ddd; border-radius: 8px; background: white;
                {text_css}
            }}
            .transcript-row {{ display: flex; align-items: baseline; margin-bottom: 12px; }}
            .seek-btn {{ 
                cursor: pointer; background: #4CAF50; color: white; border: none; 
                padding: 5px 10px; border-radius: 4px; font-weight: bold; 
                margin-right: 10px; min-width: 70px;
                transition: background 0.2s;
            }}
            .seek-btn:hover {{ background: #45a049; }}
            .text {{ line-height: 1.6; color: #333; }}
            h3 {{ margin-top: 0; color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px;}}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="player-col">
                <h3>🎧 Trình phát</h3>
                <audio id="myAudio" controls style="width: 100%;">
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
            </div>
            <div class="text-col">
                <h3>📝 Nội dung chi tiết</h3>
                {transcript_items}
            </div>
        </div>
        <script>
            function seekTo(seconds) {{
                var audio = document.getElementById("myAudio");
                if (audio) {{
                    audio.currentTime = seconds;
                    audio.play();
                }}
            }}
        </script>
    </body>
    </html>
    """
    return html