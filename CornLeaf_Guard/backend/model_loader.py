from pathlib import Path
import streamlit as st
from ultralytics import YOLO


@st.cache_resource
def load_yolo_model(model_path: Path):
    """Memuat model YOLO satu kali dan menyimpannya dalam cache Streamlit."""
    if not model_path.is_file():
        raise FileNotFoundError(
            f"File model tidak ditemukan: {model_path}. "
            "Pastikan models/best.pt tersedia di repositori."
        )
    return YOLO(str(model_path))
