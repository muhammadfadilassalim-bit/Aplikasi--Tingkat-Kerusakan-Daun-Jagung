from pathlib import Path
import streamlit as st

from backend.model_loader import load_yolo_model
from backend.image_processing import analyze_image
from frontend.styles import apply_styles
from frontend.components import (
    render_header, render_sidebar, render_footer,
    render_input_tabs, render_analysis_section
)
from frontend.results import build_result_html

st.set_page_config(
    page_title="CornLeaf Guard - Dashboard Deteksi Tanaman AI",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent

apply_styles()

try:
    model = load_yolo_model(BASE_DIR / "models" / "best.pt")
except Exception as exc:
    st.error(
        "Peringatan: Gagal memuat model 'models/best.pt'. "
        f"Detail error: {exc}"
    )
    st.stop()

if "analysis_html" not in st.session_state:
    st.session_state.analysis_html = None

render_header()

col_main, col_aside = st.columns([2, 1], gap="large")

with col_main:
    active_file, active_source, file_input, camera_input = render_input_tabs()

    if active_file is not None:
        with st.spinner("Model YOLOv11 + HSV Sedang Menganalisis..."):
            analysis = analyze_image(active_file.getvalue(), model)
        st.session_state.analysis_html = build_result_html(analysis)

    # Reset hasil diagnosis jika kedua input telah dikosongkan.
    if file_input is None and camera_input is None:
        st.session_state.analysis_html = None

    render_analysis_section(st.session_state.analysis_html)

with col_aside:
    render_sidebar()

render_footer()
