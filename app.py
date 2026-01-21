import streamlit as st
import os
import streamlit.components.v1 as components
from src import core, utils 

# 1. Cấu hình trang
st.set_page_config(page_title="Mini STT Pro", page_icon="🎙️")
st.title("🎙️ Mini Speech-to-Text Tool")

# --- KHAI BÁO TỪ ĐIỂN (MAPPING) ---

# [Hiển thị Tiếng Việt] : [Mã Code Tiếng Anh]
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

LAYOUT_OPTIONS = {
    "2 Cột (Ngang)": "2col",
    "1 Cột (Dọc)": "1col"
}

# 2. Sidebar cấu hình
with st.sidebar:
    st.header("Cấu hình")
    
    # --- Chọn Model ---
    selected_model_label = st.selectbox(
        "Kích thước Model", 
        list(MODEL_SIZES.keys()), # Hiển thị list tiếng Việt
        index=0
    )
    # Lấy mã code tiếng Anh (ví dụ: 'tiny')
    model_code = MODEL_SIZES[selected_model_label]
    st.caption("ℹ️ Note: Mặc định là máy phế để load nhanh hơn.")

    st.divider()

    # --- Chọn Ngôn ngữ ---
    selected_lang_label = st.selectbox(
        "Ngôn ngữ âm thanh",
        list(LANGUAGES.keys()), 
        index=0
    )
    # Lấy mã code ngôn ngữ (ví dụ: 'vi', 'en')
    lang_code = LANGUAGES[selected_lang_label]
    st.caption("ℹ️ Note: Nếu chọn sai ngôn ngữ kết quả sẽ rất tệ.")
    
    st.divider()
    
    # --- Chọn Giao diện ---
    selected_layout_label = st.radio(
        "Giao diện hiển thị",
        list(LAYOUT_OPTIONS.keys()),
        index=0 
    )
    # Lấy mã code giao diện ('2col' hoặc '1col')
    layout_code = LAYOUT_OPTIONS[selected_layout_label]
    
    st.divider()
    
    # --- Chế độ làm việc ---
    app_mode = st.radio("Chế độ", ["Transcribe", "Editor"], horizontal=True)
    st.session_state.app_mode = app_mode
    
    st.divider()
    
    # --- Nút mở folder data ---
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📂 Mở Data"):
            if not os.path.exists("data"):
                os.makedirs("data")
            os.startfile("data")
    
    with col_btn2:
        if st.button("🗑️ Xóa Data"):
            if utils.delete_all_data():
                st.success("Đã xóa!", icon="✅")
            else:
                st.error("Lỗi!", icon="❌")

# 3. Load Model (Dùng mã code để load)
with st.spinner("Đang khởi động AI..."):
    model = core.load_model(model_code)
    st.success("AI đã sẵn sàng!")

# --- XỬ LÝ LOGIC CHÍNH ---

if st.session_state.app_mode == "Transcribe":
    # Khởi tạo Session State
    if "transcript_result" not in st.session_state:
        st.session_state.transcript_result = None
    if "temp_audio_path" not in st.session_state:
        st.session_state.temp_audio_path = None

    uploaded_file = st.file_uploader("Tải file ghi âm lên (mp3, wav, m4a)", type=["mp3", "wav", "m4a"])

    if uploaded_file and st.button("🚀 Bắt đầu", type="primary"):
        try:
            with st.spinner("Đang xử lý..."):
                # Lưu file
                temp_path = utils.save_uploaded_file(uploaded_file)
                
                # Chạy AI
                raw_result = core.transcribe_audio(model, temp_path, language=lang_code)
                
                # Lưu kết quả vào Session State
                st.session_state.transcript_result = raw_result["segments"]
                st.session_state.temp_audio_path = temp_path
                
                # --- NEW: Tự động lưu segments và CSV ---
                session_dir = utils.save_segments_to_folder(temp_path, raw_result["segments"])
                st.success(f"Xử lý hoàn tất! Đã lưu data tại: {session_dir}")
                
        except Exception as e:
            st.error(f"Lỗi: {e}")

    # --- HIỂN THỊ KẾT QUẢ ---
    if st.session_state.transcript_result is not None:
        
        segments = st.session_state.transcript_result
        audio_path = st.session_state.temp_audio_path
        
        # Gọi hàm tạo HTML
        dashboard_html = utils.create_dashboard_html(
            audio_path, 
            segments, 
            layout_mode=layout_code 
        )
        
        height = 700 if layout_code == "2col" else 900
        components.html(dashboard_html, height=height, scrolling=True)

elif st.session_state.app_mode == "Editor":
    st.header("📝 Trình chỉnh sửa Transcript")
    
    if not os.path.exists("data"):
        st.info("Chưa có dữ liệu. Hãy chuyển sang Tab 'Transcribe' để xử lý file âm thanh trước.")
    else:
        # Scan folders in data
        sessions = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]
        
        if not sessions:
            st.info("Chưa có session nào.")
        else:
            selected_session = st.selectbox("Chọn Session", sessions)
            session_path = os.path.join("data", selected_session)
            
            # Load data
            csv_data = utils.load_session_data(session_path)
            
            if not csv_data:
                st.warning("Không tìm thấy metadata.csv hoặc file rỗng.")
            else:
                st.write(f"Đang sửa: `{selected_session}` ({len(csv_data)} segments)")
                
                # Form
                with st.form("editor_form"):
                    updated_data = []
                    for i, row in enumerate(csv_data):
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            # CSV only has filename and transcription, so no start/end time
                            st.caption(f"Segment {i+1}")
                            
                            # Handle missing keys gracefully
                            filename = row.get('filename', row.get('audio_file', ''))
                            audio_file = os.path.join(session_path, filename)
                            
                            if os.path.exists(audio_file):
                                st.audio(audio_file)
                            else:
                                st.error(f"Missing audio: {filename}")
                        
                        with col2:
                            current_text = row.get('transcription', row.get('transcript', ''))
                            new_text = st.text_area(
                                label="Nội dung", 
                                value=current_text, 
                                key=f"text_{i}",
                                height=100,
                                label_visibility="collapsed"
                            )
                            # Update row - normalize keys for saving
                            row['transcription'] = new_text
                            # Ensure filename is preserved if we switch from audio_file
                            if 'filename' not in row and 'audio_file' in row:
                                row['filename'] = row['audio_file']
                                
                            updated_data.append(row)
                        
                        st.divider()
                    
                    if st.form_submit_button("Lưu thay đổi", type="primary"):
                        try:
                            utils.update_transcript(session_path, updated_data)
                            st.success("Đã lưu metadata.csv thành công!")
                        except Exception as e:
                            st.error(f"Lỗi khi lưu: {e}")