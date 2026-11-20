import base64
from pathlib import Path
import cv2
import numpy as np
import streamlit as st
from ultralytics import YOLO

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="CornLeaf Guard - Dashboard Deteksi Tanaman AI",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = Path(__file__).resolve().parent

# 2. Custom CSS untuk Menyamakan Tampilan dengan Desain Asli
st.markdown("""
<style>
    header[data-testid="stHeader"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 1180px !important;
    }
    html, body, [class*="css"] {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: #f8fafc;
        color: #0f172a;
    }

    /* Header Gradien Hijau */
    .custom-header {
        background: linear-gradient(to right, #065f46, #0f766e);
        color: white;
        padding: 16px 24px;
        border-radius: 0 0 16px 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    .logo-flex { display: flex; align-items: center; gap: 12px; }
    .logo-icon {
        background-color: rgba(255, 255, 255, 0.2);
        padding: 8px 12px;
        border-radius: 12px;
        font-size: 24px;
    }
    .badge-active {
        font-size: 12px;
        background-color: #064e3b;
        padding: 5px 14px;
        border-radius: 9999px;
        color: #d1fae5;
        font-weight: 600;
        border: 1px solid rgba(167, 243, 208, 0.25);
    }

    /* Kartu & Kontainer */
    .custom-card {
        background-color: white;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        padding: 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
    }
    .section-label {
        margin-top: 8px;
        margin-bottom: 12px;
        font-weight: 700;
        color: #64748b;
        font-size: 13px;
        letter-spacing: 0.05em;
    }
    .placeholder-box {
        padding: 36px 24px;
        text-align: center;
        font-size: 14px;
        color: #94a3b8;
        border: 1px dashed #cbd5e1;
        border-radius: 16px;
        background-color: white;
    }

    /* Styling Tab Streamlit */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #e2e8f0;
        color: #475569;
        border-radius: 8px;
        padding: 6px 16px;
        font-weight: 600;
        font-size: 13px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #059669 !important;
        color: white !important;
    }

    /* Kartu Kriteria Kanan */
    .kriteria-item {
        padding: 12px 14px;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin-bottom: 12px;
    }

    /* Visualisasi Grid */
    .vis-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-top: 10px;
    }
    @media (max-width: 768px) {
        .vis-grid { grid-template-columns: 1fr; }
    }
    .vis-card {
        background-color: #0f172a;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #cbd5e1;
        text-align: center;
    }
    .vis-card img {
        width: 100%;
        height: 175px;
        object-fit: cover;
        display: block;
    }
    .vis-caption {
        padding: 8px;
        background-color: #1e293b;
        color: white;
        font-weight: 600;
        font-size: 11px;
    }

    /* Footer */
    .custom-footer {
        width: 100%;
        background-color: white;
        border-top: 1px solid #e2e8f0;
        text-align: center;
        padding: 14px 0;
        font-size: 12px;
        color: #94a3b8;
        font-weight: 500;
        margin-top: 32px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Load Model YOLOv11 Segmentasi dengan Cache
@st.cache_resource
def load_yolo_model():
    model_path = BASE_DIR / "models" / "best.pt"
    return YOLO(str(model_path))

try:
    model = load_yolo_model()
except Exception as e:
    st.error(f"Peringatan: Gagal memuat model 'models/best.pt'. Error: {e}")
    st.stop()

# Rentang HSV untuk mendeteksi warna bercak/penyakit
HSV_LOWER_DISEASE = np.array([10, 40, 40])
HSV_UPPER_DISEASE = np.array([35, 255, 255])

def mat_to_base64(img_mat):
    """Mengonversi array gambar OpenCV (BGR) ke string Base64."""
    _, buffer = cv2.imencode('.jpg', img_mat)
    return base64.b64encode(buffer).decode('utf-8')

# 4. Header Aplikasi
st.markdown("""<div class="custom-header"><div class="logo-flex"><div class="logo-icon">🌽</div><div><div style="font-weight: 700; font-size: 20px; line-height: 1.2;">CornLeaf Guard</div><div style="font-size: 11px; color: #a7f3d0; margin-top: 2px;">Sistem Pemantauan Kesehatan Komoditas Jagung</div></div></div><div><span class="badge-active">YOLOv11 + HSV ACTIVE</span></div></div>""", unsafe_allow_html=True)

# 5. Layout Utama 2 Kolom (2fr : 1fr)
col_main, col_aside = st.columns([2, 1], gap="large")

with col_main:
    with st.container():
        tab_upload, tab_camera = st.tabs(["📁 Upload Foto File", "📸 Kamera Direct"])

        uploaded_file = None
        with tab_upload:
            file_input = st.file_uploader(
                "Pilih gambar daun jagung dari perangkat",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed"
            )
            if file_input is not None:
                uploaded_file = file_input

        with tab_camera:
            camera_input = st.camera_input(
                "Potret gambar daun jagung",
                label_visibility="collapsed"
            )
            if camera_input is not None:
                uploaded_file = camera_input

    st.markdown('<div class="section-label">🔬 HASIL ANALISIS SEGMENTASI INSTAN</div>', unsafe_allow_html=True)

    if uploaded_file is None:
        st.markdown("""<div class="placeholder-box">Silakan aktifkan kamera di atas atau upload file gambar daun untuk memicu proses analisis otomatis.</div>""", unsafe_allow_html=True)
    else:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img is None:
            st.markdown("""<div style="padding: 16px; background-color: #fef2f2; border: 1px solid #fecaca; color: #b91c1c; border-radius: 12px; text-align: center;"><strong>❌ Gagal Menganalisis Gambar</strong><p style="font-size: 12px; margin-top: 4px;">Format gambar tidak valid atau korup.</p></div>""", unsafe_allow_html=True)
        else:
            with st.spinner("Model YOLOv11 + HSV Sedang Menganalisis..."):
                h, w, _ = img.shape
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

                # 1. Predict Segmentasi Daun dengan YOLOv11
                results = model.predict(img, conf=0.60, verbose=False)[0]

                if results.masks is None or len(results.masks) == 0:
                    st.markdown("""<div style="padding: 20px; background-color: #fffbeb; border: 1px solid #fde68a; color: #92400e; border-radius: 16px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.05);"><div style="font-size: 28px;">⚠️</div><p style="font-weight: 700; font-size: 16px; color: #78350f; margin: 6px 0 4px 0;">Gambar Bukan Daun Jagung</p><p style="font-size: 12px; color: #b45309; margin: 0;">Daun jagung tidak terdeteksi oleh sistem. Silakan pilih atau ambil foto sampel daun jagung secara jelas.</p></div>""", unsafe_allow_html=True)
                else:
                    # 2. Buat Binary Mask Total Area Daun
                    leaf_mask = np.zeros((h, w), dtype=np.uint8)
                    for mask_data in results.masks.data:
                        mask_np = mask_data.cpu().numpy()
                        mask_resized = cv2.resize(mask_np, (w, h), interpolation=cv2.INTER_NEAREST)
                        leaf_mask = np.bitwise_or(leaf_mask, (mask_resized > 0.5).astype(np.uint8))

                    total_leaf_pixels = int(np.sum(leaf_mask))

                    if total_leaf_pixels == 0:
                        st.markdown("""<div style="padding: 20px; background-color: #fffbeb; border: 1px solid #fde68a; color: #92400e; border-radius: 16px; text-align: center;"><div style="font-size: 28px;">⚠️</div><p style="font-weight: 700; font-size: 16px; margin: 6px 0 0 0;">Luas Area Daun 0 Piksel</p></div>""", unsafe_allow_html=True)
                    else:
                        # 3. Deteksi Warna Kerusakan/Bercak Menggunakan HSV Thresholding
                        disease_mask_full = cv2.inRange(hsv_img, HSV_LOWER_DISEASE, HSV_UPPER_DISEASE)
                        disease_mask = cv2.bitwise_and(disease_mask_full, disease_mask_full, mask=leaf_mask)
                        total_disease_pixels = int(np.count_nonzero(disease_mask))

                        # 4. Hitung Persentase Kerusakan
                        damage_percentage = (total_disease_pixels / total_leaf_pixels) * 100.0

                        # 5. Pengkategorian Tingkat Kerusakan
                        if damage_percentage < 1.0:
                            kategori_text = "SEHAT"
                            badge_style = "background-color: #dcfce7; color: #166534;"
                            deskripsi = "Daun terdeteksi dalam kondisi sehat secara umum dengan tingkat kerusakan minimal (< 1%)."
                            solusi_list = [
                                "Pertahankan pola pengairan yang konsisten.",
                                "Berikan pupuk nitrogen secara berkala.",
                                "Lakukan pemantauan rutin seminggu sekali."
                            ]
                        elif 1.0 <= damage_percentage <= 30.0:
                            kategori_text = "ADA KERUSAKAN"
                            badge_style = "background-color: #fef3c7; color: #92400e;"
                            deskripsi = f"Terdeteksi adanya bercak/gejala penyakit pada daun dengan tingkat kerusakan ringan-sedang ({damage_percentage:.2f}%)."
                            solusi_list = [
                                "Isolasi atau pangkas daun yang terinfeksi jika masih sedikit.",
                                "Semprotkan fungisida organik atau berbahan aktif sesuai dosis anjuran.",
                                "Jaga kebersihan area sekitar lahan tanaman."
                            ]
                        else:
                            kategori_text = "RUSAK PARAH"
                            badge_style = "background-color: #fee2e2; color: #991b1b;"
                            deskripsi = f"Daun mengalami kerusakan parah akibat infeksi bercak/penyakit yang meluas ({damage_percentage:.2f}%)."
                            solusi_list = [
                                "Segera aplikasikan fungisida sistemik secara intensif.",
                                "Pindahkan/karantina tanaman terinfeksi dari tanaman sehat.",
                                "Lakukan rotasi tanaman untuk siklus tanam berikutnya."
                            ]

                        # 6. Pembuatan 3 Visualisasi Gambar
                        visualisasi_img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                        green_overlay = np.zeros_like(visualisasi_img)
                        green_overlay[leaf_mask == 1] = [0, 255, 0]
                        visualisasi_img = cv2.addWeighted(visualisasi_img, 0.85, green_overlay, 0.15, 0)
                        visualisasi_img[disease_mask > 0] = [0, 0, 255]

                        leaf_mask_vis = (leaf_mask * 255).astype(np.uint8)
                        disease_mask_vis = (disease_mask > 0).astype(np.uint8) * 255

                        b64_visual = mat_to_base64(visualisasi_img)
                        b64_leaf_mask = mat_to_base64(leaf_mask_vis)
                        b64_disease_mask = mat_to_base64(disease_mask_vis)

                        solusi_html = "".join([
                            f"<li style='display: flex; align-items: flex-start; margin-bottom: 6px;'><span style='color: #10b981; margin-right: 8px;'>➤</span><span>{s}</span></li>"
                            for s in solusi_list
                        ])

                        # Render Kartu Hasil Diagnosis Tanpa Indentasi Spasi agar tidak terbaca sebagai Code Block
                        html_result = (
                            f'<div class="custom-card">'
                            f'<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 14px; flex-wrap: wrap; gap: 8px;">'
                            f'<h3 style="font-weight: 700; font-size: 18px; color: #1e293b; margin: 0;">📋 Hasil Diagnosis Tingkat Kerusakan</h3>'
                            f'<span style="padding: 4px 12px; font-size: 12px; font-weight: 700; border-radius: 9999px; {badge_style}">{kategori_text} ({damage_percentage:.2f}%)</span>'
                            f'</div>'
                            f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 12px; background-color: #f8fafc; padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 16px;">'
                            f'<div><span style="color: #64748b; display: block;">Luas Total Daun:</span><strong style="color: #1e293b; font-size: 15px;">{total_leaf_pixels:,} px</strong></div>'
                            f'<div><span style="color: #64748b; display: block;">Luas Kerusakan (HSV):</span><strong style="color: #e11d48; font-size: 15px;">{total_disease_pixels:,} px</strong></div>'
                            f'</div>'
                            f'<div style="border-top: 1px solid #e2e8f0; padding-top: 14px; margin-bottom: 16px;">'
                            f'<h4 style="font-weight: 700; color: #334155; font-size: 13px; text-transform: uppercase; letter-spacing: 0.04em; margin: 0 0 8px 0;">🎨 Visualisasi Segmentasi AI & HSV:</h4>'
                            f'<div class="vis-grid">'
                            f'<div class="vis-card"><img src="data:image/jpeg;base64,{b64_visual}" alt="Visualisasi Overlay"><div class="vis-caption">Visualisasi Output<br><span style="color: #fbbf24;">({kategori_text.lower()}: {damage_percentage:.2f}%)</span></div></div>'
                            f'<div class="vis-card"><img src="data:image/jpeg;base64,{b64_leaf_mask}" alt="Mask Daun"><div class="vis-caption">Mask Daun (YOLOv11)</div></div>'
                            f'<div class="vis-card"><img src="data:image/jpeg;base64,{b64_disease_mask}" alt="Mask Kerusakan"><div class="vis-caption">Mask Kerusakan (HSV)</div></div>'
                            f'</div>'
                            f'</div>'
                            f'<div style="border-top: 1px dashed #e2e8f0; padding-top: 12px; margin-bottom: 14px;">'
                            f'<h4 style="font-weight: 700; color: #334155; font-size: 13px; text-transform: uppercase; letter-spacing: 0.04em; margin: 0 0 6px 0;">Karakteristik & Kondisi:</h4>'
                            f'<p style="color: #475569; font-size: 14px; line-height: 1.6; margin: 0;">{deskripsi}</p>'
                            f'</div>'
                            f'<div style="border-top: 1px dashed #e2e8f0; padding-top: 12px;">'
                            f'<h4 style="font-weight: 700; color: #047857; font-size: 13px; text-transform: uppercase; letter-spacing: 0.04em; margin: 0 0 8px 0;">🛡️ Rekomendasi Tindakan:</h4>'
                            f'<ul style="color: #475569; font-size: 14px; list-style: none; padding: 0; margin: 0; font-weight: 500;">{solusi_html}</ul>'
                            f'</div>'
                            f'</div>'
                        )
                        st.markdown(html_result, unsafe_allow_html=True)

# 6. Sektor Kanan: Panel Informasi Kriteria Tingkat Kerusakan (Tanpa Indentasi Spasi)
with col_aside:
    html_aside = (
        '<div class="custom-card">'
        '<div style="border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 16px;">'
        '<h2 style="font-weight: 700; color: #1e293b; font-size: 16px; margin: 0;">📚 Kriteria Tingkat Kerusakan</h2>'
        '</div>'
        '<div class="kriteria-item">'
        '<div style="font-weight: 700; font-size: 14px; color: #047857;">🟢 DAUN SEHAT</div>'
        '<p style="font-size: 12px; color: #475569; margin: 4px 0 0 0;">Luas area bercak/kerusakan pada daun kurang dari 1.0%.</p>'
        '</div>'
        '<div class="kriteria-item">'
        '<div style="font-weight: 700; font-size: 14px; color: #b45309;">🟡 ADA KERUSAKAN</div>'
        '<p style="font-size: 12px; color: #475569; margin: 4px 0 0 0;">Luas area bercak/kerusakan pada daun berkisar antara 1.0% - 30.0%.</p>'
        '</div>'
        '<div class="kriteria-item" style="margin-bottom: 0;">'
        '<div style="font-weight: 700; font-size: 14px; color: #be123c;">🔴 RUSAK PARAH</div>'
        '<p style="font-size: 12px; color: #475569; margin: 4px 0 0 0;">Luas area bercak/kerusakan pada daun lebih dari 30.0%.</p>'
        '</div>'
        '</div>'
    )
    st.markdown(html_aside, unsafe_allow_html=True)

# 7. Footer
st.markdown("""<div class="custom-footer">&copy; 2026 CornLeaf Guard - Universitas Pertanian Cerdas AI. All Rights Reserved.</div>""", unsafe_allow_html=True)
