import whisper
import streamlit as st

@st.cache_resource
def load_model(model_size, download_root=None):
    print(f"Loading Whisper model: {model_size}...")
    if download_root:
        return whisper.load_model(model_size, download_root=download_root)
    return whisper.load_model(model_size)

def transcribe_audio(model, file_path, language = None):
    if language == "Auto":
        result = model.transcribe(file_path)
    else:
        result = model.transcribe(file_path, language=language)
        
    return result