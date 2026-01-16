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

def get_audio_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

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