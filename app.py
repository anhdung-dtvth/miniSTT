import streamlit as st
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

# 3. Load Model (Dùng mã code để load)
with st.spinner("Đang khởi động AI..."):
    model = core.load_model(model_code)
    st.success("AI đã sẵn sàng!")

# --- XỬ LÝ LOGIC CHÍNH ---

# Khởi tạo Session State (tên biến dùng tiếng Anh)
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
            
            # Chạy AI (Truyền các mã code tiếng Anh vào logic)
            raw_result = core.transcribe_audio(model, temp_path, language=lang_code)
            
            # Lưu kết quả vào Session State
            st.session_state.transcript_result = raw_result["segments"]
            st.session_state.temp_audio_path = temp_path
            
            st.success("Xử lý hoàn tất!")
            
    except Exception as e:
        st.error(f"Lỗi: {e}")

# --- HIỂN THỊ KẾT QUẢ ---
if st.session_state.transcript_result is not None:
    
    segments = st.session_state.transcript_result
    audio_path = st.session_state.temp_audio_path
    
    # Gọi hàm tạo HTML (Truyền layout_code là '2col' hoặc '1col')
    dashboard_html = utils.create_dashboard_html(
        audio_path, 
        segments, 
        layout_mode=layout_code 
    )
    
    # Logic tính chiều cao iframe (Dùng code tiếng Anh để so sánh)
    height = 700 if layout_code == "2col" else 900
    components.html(dashboard_html, height=height, scrolling=True)