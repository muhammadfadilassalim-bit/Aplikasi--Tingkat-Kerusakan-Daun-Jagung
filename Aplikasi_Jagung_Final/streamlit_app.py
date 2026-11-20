from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from ultralytics import YOLO


# =========================================================
# KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(
    page_title="CornLeaf Guard",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# CSS: MENYESUAIKAN TAMPILAN STREAMLIT DENGAN APLIKASI LAMA
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --green-dark: #08634f;
        --green-main: #079b70;
        --green-soft: #e8f6f0;
        --navy: #17243b;
        --text: #172b4d;
        --muted: #718096;
        --border: #dce5ef;
        --page: #f5f8fc;
        --orange: #df7900;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: var(--page);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"] {
        right: 1rem;
    }

    .block-container {
        max-width: 1240px;
        padding-top: 1.25rem;
        padding-bottom: 1.5rem;
    }

    /* Header aplikasi */
    .app-header {
        background: linear-gradient(105deg, #08634f 0%, #087c70 100%);
        padding: 17px 28px;
        border-radius: 14px;
        margin: 0 0 18px 0;
        color: #ffffff;
        box-shadow: 0 3px 12px rgba(8, 99, 79, 0.13);
    }

    .header-inner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 13px;
    }

    .brand-logo {
        width: 52px;
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 13px;
        background: rgba(255,255,255,0.17);
        font-size: 30px;
    }

    .brand-name {
        font-size: 21px;
        line-height: 1.25;
        font-weight: 800;
        letter-spacing: -0.3px;
    }

    .brand-subtitle {
        color: #d2eee6;
        font-size: 11px;
        margin-top: 4px;
    }

    .model-badge {
        background: rgba(0, 48, 39, 0.55);
        color: #e5fff5;
        border-radius: 30px;
        padding: 7px 14px;
        font-size: 11px;
        font-weight: 700;
        white-space: nowrap;
    }

    /* Kartu konten */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 15px;
        box-shadow: 0 2px 5px rgba(20, 40, 70, 0.055);
    }

    .section-title {
        color: #536d91;
        font-size: 14px;
        font-weight: 800;
        letter-spacing: .45px;
        text-transform: uppercase;
        margin: 7px 0 10px 0;
    }

    .status-line {
        color: #718096;
        font-size: 11px;
        text-align: right;
        padding-top: 9px;
    }

    .criteria-title {
        font-size: 16px;
        font-weight: 800;
        color: #172b4d;
        padding-bottom: 11px;
        margin-bottom: 12px;
        border-bottom: 1px solid #edf1f6;
    }

    .criteria-item {
        border: 1px solid #dce5ef;
        background: #f8fafc;
        border-radius: 12px;
        padding: 12px 13px;
        margin-bottom: 10px;
    }

    .criteria-name {
        font-size: 13px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .criteria-desc {
        color: #526783;
        font-size: 11px;
        line-height: 1.55;
    }

    .criteria-healthy { color: #00865f; }
    .criteria-medium { color: #c45c00; }
    .criteria-severe { color: #d31337; }

    /* Widget Streamlit */
    [data-testid="stFileUploader"] section {
        border: 1px dashed #b9c9dc;
        border-radius: 11px;
        background: #f8fafc;
    }

    [data-testid="stCameraInput"] {
        border-radius: 11px;
        overflow: hidden;
    }

    .stButton > button {
        border-radius: 10px;
        min-height: 43px;
        font-weight: 700;
        border: 1px solid #cbd8e8;
        transition: all .15s ease;
    }

    .stButton > button[kind="primary"] {
        background: #079b70;
        border-color: #079b70;
        color: white;
    }

    .stButton > button:hover {
        border-color: #079b70;
        color: #087c60;
    }

    [data-testid="stMetric"] {
        background: #f7f9fc;
        border: 1px solid #dce5ef;
        border-radius: 10px;
        padding: 12px 14px;
    }

    [data-testid="stMetricLabel"] {
        color: #61748f;
    }

    [data-testid="stMetricValue"] {
        color: #172b4d;
        font-size: 22px;
    }

    [data-testid="stImage"] img {
        border-radius: 9px;
    }

    .result-heading {
        font-size: 17px;
        font-weight: 800;
        color: #172b4d;
    }

    .result-badge {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
    }

    .badge-healthy {
        color: #087c48;
        background: #e1f7e9;
    }

    .badge-medium {
        color: #9a4b00;
        background: #fff1c9;
    }

    .badge-severe {
        color: #b51232;
        background: #ffe2e7;
    }

    .visual-label {
        text-align: center;
        background: #17243b;
        color: #ffffff;
        font-size: 11px;
        font-weight: 700;
        border-radius: 0 0 8px 8px;
        padding: 8px 4px;
        margin-top: -7px;
        margin-bottom: 12px;
    }

    .recommendation-item {
        color: #263d5c;
        font-size: 13px;
        line-height: 1.65;
        margin: 5px 0;
    }

    .empty-result {
        border: 1px dashed #d6e1ee;
        border-radius: 13px;
        background: #ffffff;
        padding: 28px 16px;
        text-align: center;
        color: #8293aa;
        font-size: 13px;
    }

    .warning-panel {
        border: 1px solid #ffd778;
        border-radius: 13px;
        background: #fffbeb;
        padding: 24px 16px;
        text-align: center;
        color: #9a4b00;
    }

    .app-footer {
        border-top: 1px solid #dce5ef;
        margin-top: 28px;
        padding: 14px 8px 4px 8px;
        text-align: center;
        color: #8293aa;
        font-size: 11px;
    }

    @media (max-width: 760px) {
        .block-container {
            padding: .7rem .7rem 1rem .7rem;
        }
        .app-header {
            padding: 14px;
        }
        .brand-name {
            font-size: 18px;
        }
        .brand-logo {
            width: 44px;
            height: 44px;
        }
        .model-badge {
            font-size: 9px;
            padding: 6px 8px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================
st.markdown(
    """
    <div class="app-header">
        <div class="header-inner">
            <div class="brand">
                <div class="brand-logo">🌽</div>
                <div>
                    <div class="brand-name">CornLeaf Guard</div>
                    <div class="brand-subtitle">
                        Sistem Pemantauan Kesehatan Komoditas Jagung
                    </div>
                </div>
            </div>
            <div class="model-badge">YOLOv11 + HSV ACTIVE</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# LOAD MODEL
# =========================================================
@st.cache_resource
def load_yolo_model():
    model_path = BASE_DIR / "models" / "best.pt"
    if not model_path.exists():
        raise FileNotFoundError(
            f"File model tidak ditemukan: {model_path}. "
            "Pastikan best.pt berada di folder models/."
        )
    return YOLO(str(model_path))


try:
    model = load_yolo_model()
except Exception as e:
    st.error(f"Gagal memuat model YOLO pada folder `models/best.pt`. Detail: {e}")
    st.stop()


# =========================================================
# KRITERIA KERUSAKAN
# =========================================================
HSV_LOWER_DISEASE = np.array([10, 40, 40])
HSV_UPPER_DISEASE = np.array([35, 255, 255])


# =========================================================
# AREA INPUT DAN PANEL KRITERIA
# =========================================================
left_col, right_col = st.columns([1.85, 0.95], gap="large")

uploaded_file = None
camera_file = None

with left_col:
    with st.container(border=True):
        input_tab_upload, input_tab_camera = st.tabs(
            ["📁 Upload Foto File", "📷 Kamera Direct"]
        )

        with input_tab_upload:
            uploaded_file = st.file_uploader(
                "Pilih gambar daun jagung",
                type=["jpg", "jpeg", "png"],
                help="Format yang didukung: JPG, JPEG, dan PNG.",
                label_visibility="collapsed",
                key="cornleaf_uploader",
            )

        with input_tab_camera:
            camera_file = st.camera_input(
                "Ambil foto sampel daun jagung",
                label_visibility="collapsed",
                key="cornleaf_camera",
            )

        if uploaded_file is not None:
            selected_file = uploaded_file
            st.caption("🟢 File siap dianalisis")
        elif camera_file is not None:
            selected_file = camera_file
            st.caption("🟢 Foto kamera siap dianalisis")
        else:
            selected_file = None
            st.caption("🔴 Belum ada gambar yang dipilih")

        if selected_file is not None:
            try:
                file_bytes = np.asarray(
                    bytearray(selected_file.getvalue()), dtype=np.uint8
                )
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

                if img is None:
                    st.error("Format gambar tidak valid atau file rusak.")
                    st.stop()

                preview_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                st.image(
                    preview_rgb,
                    caption="Pratinjau gambar daun jagung",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Gagal membaca gambar: {e}")
                st.stop()

with right_col:
    with st.container(border=True):
        st.markdown(
            '<div class="criteria-title">📚 Kriteria Tingkat Kerusakan</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="criteria-item">
                <div class="criteria-name criteria-healthy">🟢 DAUN SEHAT</div>
                <div class="criteria-desc">
                    Luas area bercak/kerusakan pada daun kurang dari 1.0%.
                </div>
            </div>
            <div class="criteria-item">
                <div class="criteria-name criteria-medium">🟡 ADA KERUSAKAN</div>
                <div class="criteria-desc">
                    Luas area bercak/kerusakan pada daun berkisar antara 1.0% - 30.0%.
                </div>
            </div>
            <div class="criteria-item">
                <div class="criteria-name criteria-severe">🔴 RUSAK PARAH</div>
                <div class="criteria-desc">
                    Luas area bercak/kerusakan pada daun lebih dari 30.0%.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# HASIL ANALISIS
# =========================================================
st.markdown(
    '<div class="section-title">🔬 HASIL ANALISIS SEGMENTASI INSTAN</div>',
    unsafe_allow_html=True,
)

if selected_file is None:
    st.markdown(
        """
        <div class="empty-result">
            Silakan aktifkan kamera di atas atau upload file gambar daun
            untuk memulai proses analisis otomatis.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    with st.spinner("Model YOLOv11 + HSV sedang menganalisis gambar..."):
        h, w, _ = img.shape
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 1. Prediksi segmentasi daun menggunakan YOLOv11.
        results = model.predict(img, conf=0.60, verbose=False)[0]

        # 2. Periksa apakah daun terdeteksi.
        if results.masks is None or len(results.masks) == 0:
            analysis_ok = False
        else:
            analysis_ok = True

        if analysis_ok:
            # 3. Buat binary mask total area daun.
            leaf_mask = np.zeros((h, w), dtype=np.uint8)

            for mask_data in results.masks.data:
                mask_np = mask_data.cpu().numpy()
                mask_resized = cv2.resize(
                    mask_np,
                    (w, h),
                    interpolation=cv2.INTER_NEAREST,
                )
                leaf_mask = np.bitwise_or(
                    leaf_mask,
                    (mask_resized > 0.5).astype(np.uint8),
                )

            total_leaf_pixels = int(np.sum(leaf_mask))

            if total_leaf_pixels == 0:
                analysis_ok = False

        if analysis_ok:
            # 4. Deteksi warna kerusakan menggunakan HSV.
            disease_mask_full = cv2.inRange(
                hsv_img,
                HSV_LOWER_DISEASE,
                HSV_UPPER_DISEASE,
            )
            disease_mask = cv2.bitwise_and(
                disease_mask_full,
                disease_mask_full,
                mask=leaf_mask,
            )
            total_disease_pixels = int(np.count_nonzero(disease_mask))

            # 5. Hitung persentase kerusakan.
            damage_percentage = (
                total_disease_pixels / total_leaf_pixels
            ) * 100.0

            # 6. Kategorisasi dan rekomendasi.
            if damage_percentage < 1.0:
                kategori_text = "SEHAT"
                badge_class = "badge-healthy"
                deskripsi = (
                    "Daun terdeteksi dalam kondisi sehat secara umum "
                    "dengan tingkat kerusakan minimal (< 1%)."
                )
                solusi_list = [
                    "Pertahankan pola pengairan yang konsisten.",
                    "Berikan pupuk nitrogen secara berkala.",
                    "Lakukan pemantauan rutin seminggu sekali.",
                ]
            elif 1.0 <= damage_percentage <= 30.0:
                kategori_text = "ADA KERUSAKAN"
                badge_class = "badge-medium"
                deskripsi = (
                    "Terdeteksi adanya bercak/gejala penyakit pada daun "
                    f"dengan tingkat kerusakan ringan-sedang ({damage_percentage:.2f}%)."
                )
                solusi_list = [
                    "Isolasi atau pangkas daun yang terinfeksi jika masih sedikit.",
                    "Semprotkan fungisida organik atau berbahan aktif sesuai dosis anjuran.",
                    "Jaga kebersihan area sekitar lahan tanaman.",
                ]
            else:
                kategori_text = "RUSAK PARAH"
                badge_class = "badge-severe"
                deskripsi = (
                    "Daun mengalami kerusakan parah akibat infeksi "
                    f"bercak/penyakit yang meluas ({damage_percentage:.2f}%)."
                )
                solusi_list = [
                    "Segera aplikasikan fungisida sistemik secara intensif.",
                    "Pindahkan/karantina tanaman terinfeksi dari tanaman sehat.",
                    "Lakukan rotasi tanaman untuk siklus tanam berikutnya.",
                ]

            # 7. Buat visualisasi output.
            visualisasi_img = img_rgb.copy()
            green_overlay = np.zeros_like(visualisasi_img)
            green_overlay[leaf_mask == 1] = [0, 255, 0]
            visualisasi_img = cv2.addWeighted(
                visualisasi_img,
                0.85,
                green_overlay,
                0.15,
                0,
            )
            visualisasi_img[disease_mask > 0] = [255, 0, 0]

            leaf_mask_vis = (leaf_mask * 255).astype(np.uint8)
            disease_mask_vis = (
                (disease_mask > 0).astype(np.uint8) * 255
            )

    if not analysis_ok:
        st.markdown(
            """
            <div class="warning-panel">
                <div style="font-size:34px;">⚠️</div>
                <div style="font-size:17px;font-weight:800;margin:8px 0;">
                    Gambar Bukan Daun Jagung
                </div>
                <div style="font-size:12px;">
                    Daun jagung tidak terdeteksi oleh sistem
                    (confidence di bawah 60%) atau luas mask daun bernilai 0.
                    Silakan pilih atau ambil foto daun jagung secara jelas.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        with st.container(border=True):
            result_col, badge_col = st.columns([1.7, 1])
            with result_col:
                st.markdown(
                    '<div class="result-heading">📋 Hasil Diagnosis Tingkat Kerusakan</div>',
                    unsafe_allow_html=True,
                )
            with badge_col:
                st.markdown(
                    f'<div style="text-align:right;"><span class="result-badge {badge_class}">'
                    f'{kategori_text} ({damage_percentage:.2f}%)'
                    "</span></div>",
                    unsafe_allow_html=True,
                )

            st.divider()

            metric1, metric2, metric3 = st.columns(3)
            metric1.metric(
                "Persentase Kerusakan",
                f"{damage_percentage:.2f}%",
            )
            metric2.metric(
                "Luas Total Daun",
                f"{total_leaf_pixels:,} px",
            )
            metric3.metric(
                "Luas Kerusakan (HSV)",
                f"{total_disease_pixels:,} px",
            )

            st.divider()
            st.markdown("**🎨 VISUALISASI SEGMENTASI AI & HSV**")

            image_col1, image_col2, image_col3 = st.columns(3, gap="small")

            with image_col1:
                st.image(
                    visualisasi_img,
                    use_container_width=True,
                )
                st.markdown(
                    f'<div class="visual-label">Visualisasi Output<br>'
                    f'({kategori_text.lower()}: {damage_percentage:.2f}%)</div>',
                    unsafe_allow_html=True,
                )

            with image_col2:
                st.image(
                    leaf_mask_vis,
                    use_container_width=True,
                    clamp=True,
                )
                st.markdown(
                    '<div class="visual-label">Mask Daun (YOLOv11)</div>',
                    unsafe_allow_html=True,
                )

            with image_col3:
                st.image(
                    disease_mask_vis,
                    use_container_width=True,
                    clamp=True,
                )
                st.markdown(
                    '<div class="visual-label">Mask Kerusakan (HSV)</div>',
                    unsafe_allow_html=True,
                )

            st.divider()
            st.markdown("**KARAKTERISTIK & KONDISI**")
            st.write(deskripsi)

            st.divider()
            st.markdown("**🛡️ REKOMENDASI TINDAKAN**")
            for solusi in solusi_list:
                st.markdown(
                    f'<div class="recommendation-item">➤ {solusi}</div>',
                    unsafe_allow_html=True,
                )


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <div class="app-footer">
        © 2026 CornLeaf Guard - Universitas Pertanian Cerdas AI.
        All Rights Reserved.
    </div>
    """,
    unsafe_allow_html=True,
)
