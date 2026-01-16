# 🎙️ MiniSTT Pro - AI Transcription Tool

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Whisper](https://img.shields.io/badge/OpenAI_Whisper-000000?style=for-the-badge&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **"Biến âm thanh thành văn bản - Nhanh, Chuẩn, Bảo mật."**

**MiniSTT Pro** là công cụ chuyển đổi giọng nói thành văn bản (Speech-to-Text) mạnh mẽ, chạy hoàn toàn **Offline** trên máy tính cá nhân. Được xây dựng dựa trên mô hình **OpenAI Whisper** và giao diện **Streamlit**, tool giúp bạn "gỡ băng" bài giảng, cuộc họp, hay video Youtube với độ chính xác cực cao.

---

## ✨ Tính năng nổi bật (Key Features)

* 🧠 **AI Mạnh mẽ:** Hỗ trợ đầy đủ các model từ `Tiny` (siêu tốc) đến `Large` (siêu chuẩn).
* 🌍 **Đa ngôn ngữ:** Tự động nhận diện ngôn ngữ hoặc tùy chọn tiếng Việt, Anh, Nhật, Hàn...
* 🖱️ **Interactive Transcript (Tính năng VIP):**
    * Kết hợp trình phát nhạc và văn bản.
    * **Bấm vào dòng chữ -> Audio tự tua đến đúng giây đó** (tương tự Youtube Transcript).
* 🎨 **Giao diện linh hoạt:**
    * **Chế độ 2 Cột:** Vừa nghe vừa đọc song song (tối ưu cho Desktop).
    * **Chế độ 1 Cột:** Giao diện dọc (tối ưu cho Mobile hoặc màn hình nhỏ).
* 🔒 **Bảo mật tuyệt đối:** Mọi xử lý diễn ra local, không gửi dữ liệu ra ngoài Internet.

## 🛠️ Cài đặt (Installation)

Yêu cầu: Máy tính đã cài **Python 3.8+** và **Git**.

### 1. Clone dự án về máy
```bash
git clone https://github.com/anhdung-dtvth/miniSTT
cd mini-stt-tool

```

### 2. Tạo môi trường ảo (Khuyên dùng)

Để tránh xung đột thư viện với hệ thống.

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

```

### 3. Cài đặt thư viện cần thiết

```bash
pip install -r requirements.txt

```

### 4. ⚠️ Cài đặt FFmpeg (Bắt buộc)

Whisper cần **FFmpeg** để xử lý file âm thanh. Nếu chưa có, bạn cần cài đặt:

* **Windows:** [Hướng dẫn cài đặt](https://www.wikihow.com/Install-FFmpeg-on-Windows) (Hoặc mở CMD gõ `winget install ffmpeg`).
* **macOS:** Mở Terminal gõ `brew install ffmpeg`.
* **Ubuntu/Linux:** `sudo apt install ffmpeg`.

---

## 🚀 Hướng dẫn sử dụng

1. Chạy lệnh khởi động ứng dụng:
```bash
streamlit run app.py

```


2. Trình duyệt sẽ tự mở tại địa chỉ local:
3. **Bước 1:** Mở Sidebar bên trái, chọn **Model Size** (Khuyên dùng `Base` hoặc `Small` cho máy cấu hình trung bình).
4. **Bước 2:** Upload file âm thanh (`.mp3`, `.wav`, `.m4a`).
5. **Bước 3:** Bấm nút **"🚀 Start Transcribing"** và chờ AI xử lý.
6. **Bước 4:** Tận hưởng kết quả! Bấm vào các nút thời gian màu xanh để tua lại đoạn cần nghe.


## 🤝 Đóng góp (Contributing)

Mọi ý kiến đóng góp đều được hoan nghênh!

## 📜 License

Dự án được phát hành dưới giấy phép [MIT](https://www.google.com/search?q=LICENSE). Thoải mái sử dụng và tùy biến.


*Made with ❤️ and Python.*
