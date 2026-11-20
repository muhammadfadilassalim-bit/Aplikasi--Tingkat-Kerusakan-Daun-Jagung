from pathlib import Path
import cv2
import numpy as np
import streamlit as st
from ultralytics import YOLO

# Konfigurasi Halaman
st.set_page_config(
    page_title="Deteksi Tingkat Kerusakan Daun Jagung",
    page_icon="🌽",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

# Load Model YOLOv11 Segmentasi dengan Cache agar cepat
@st.cache_resource
def load_yolo_model():
    model_path = BASE_DIR / "models" / "best.pt"
    return YOLO(str(model_path))

try:
    model = load_yolo_model()
except Exception as e:
    st.error(f"Gagal memuat model 'models/best.pt'. Error: {e}")
    st.stop()

# Rentang HSV untuk mendeteksi warna bercak/penyakit
HSV_LOWER_DISEASE = np.array([10, 40, 40])
HSV_UPPER_DISEASE = np.array([35, 255, 255])

# Header Aplikasi
st.title("🌽 Sistem Deteksi Tingkat Kerusakan Daun Jagung")
st.markdown("Unggah foto atau gunakan kamera untuk mendeteksi tingkat kerusakan daun jagung menggunakan **YOLOv11 Instance Segmentation** dan **OpenCV HSV Thresholding**.")

# Input Gambar (Upload atau Kamera)
tab_upload, tab_camera = st.tabs(["📁 Unggah Gambar", "📷 Ambil Foto Kamera"])

uploaded_file = None
with tab_upload:
    file_input = st.file_uploader("Pilih gambar daun jagung (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])
    if file_input is not None:
        uploaded_file = file_input

with tab_camera:
    camera_input = st.camera_input("Ambil foto sampel daun jagung")
    if camera_input is not None:
        uploaded_file = camera_input

if uploaded_file is not None:
    # Baca file gambar
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img is None:
        st.error("❌ Format gambar tidak valid atau korup.")
        st.stop()

    with st.spinner("Sedang menganalisis citra daun jagung..."):
        h, w, _ = img.shape
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 1. Predict Segmentasi Daun dengan YOLOv11
        results = model.predict(img, conf=0.60, verbose=False)[0]

        # Jika objek bukan daun jagung / tidak terdeteksi
        if results.masks is None or len(results.masks) == 0:
            st.warning("⚠️ **Gambar Bukan Daun Jagung**\n\nDaun jagung tidak terdeteksi oleh sistem (confidence < 60%). Silakan pilih atau ambil foto sampel daun jagung secara jelas.")
            st.image(img_rgb, caption="Gambar yang Diunggah", width=400)
            st.stop()

        # 2. Buat Binary Mask Total Area Daun
        leaf_mask = np.zeros((h, w), dtype=np.uint8)
        for mask_data in results.masks.data:
            mask_np = mask_data.cpu().numpy()
            mask_resized = cv2.resize(mask_np, (w, h), interpolation=cv2.INTER_NEAREST)
            leaf_mask = np.bitwise_or(leaf_mask, (mask_resized > 0.5).astype(np.uint8))

        total_leaf_pixels = int(np.sum(leaf_mask))

        if total_leaf_pixels == 0:
            st.warning("⚠️ **Luas Area Daun 0 Piksel**")
            st.stop()

        # 3. Deteksi Warna Kerusakan/Bercak Menggunakan HSV Thresholding
        disease_mask_full = cv2.inRange(hsv_img, HSV_LOWER_DISEASE, HSV_UPPER_DISEASE)
        disease_mask = cv2.bitwise_and(disease_mask_full, disease_mask_full, mask=leaf_mask)
        total_disease_pixels = int(np.count_nonzero(disease_mask))

        # 4. Hitung Persentase Kerusakan
        damage_percentage = (total_disease_pixels / total_leaf_pixels) * 100.0

        # 5. Pengkategorian Tingkat Kerusakan
        if damage_percentage < 1.0:
            kategori_text = "SEHAT"
            status_fn = st.success
            deskripsi = "Daun terdeteksi dalam kondisi sehat secara umum dengan tingkat kerusakan minimal (< 1%)."
            solusi_list = [
                "Pertahankan pola pengairan yang konsisten.",
                "Berikan pupuk nitrogen secara berkala.",
                "Lakukan pemantauan rutin seminggu sekali."
            ]
        elif 1.0 <= damage_percentage <= 30.0:
            kategori_text = "ADA KERUSAKAN"
            status_fn = st.warning
            deskripsi = f"Terdeteksi adanya bercak/gejala penyakit pada daun dengan tingkat kerusakan ringan-sedang ({damage_percentage:.2f}%)."
            solusi_list = [
                "Isolasi atau pangkas daun yang terinfeksi jika masih sedikit.",
                "Semprotkan fungisida organik atau berbahan aktif sesuai dosis anjuran.",
                "Jaga kebersihan area sekitar lahan tanaman."
            ]
        else:
            kategori_text = "RUSAK PARAH"
            status_fn = st.error
            deskripsi = f"Daun mengalami kerusakan parah akibat infeksi bercak/penyakit yang meluas ({damage_percentage:.2f}%)."
            solusi_list = [
                "Segera aplikasikan fungisida sistemik secara intensif.",
                "Pindahkan/karantina tanaman terinfeksi dari tanaman sehat.",
                "Lakukan rotasi tanaman untuk siklus tanam berikutnya."
            ]

        # 6. Pembuatan Visualisasi Gambar
        visualisasi_img = img_rgb.copy()
        green_overlay = np.zeros_like(visualisasi_img)
        green_overlay[leaf_mask == 1] = [0, 255, 0]
        visualisasi_img = cv2.addWeighted(visualisasi_img, 0.85, green_overlay, 0.15, 0)
        visualisasi_img[disease_mask > 0] = [255, 0, 0]  # Merah RGB untuk kerusakan

        leaf_mask_vis = (leaf_mask * 255).astype(np.uint8)
        disease_mask_vis = (disease_mask > 0).astype(np.uint8) * 255

    # --- TAMPILAN HASIL DIAGNOSIS ---
    st.divider()
    st.subheader("📋 Hasil Diagnosis Tingkat Kerusakan")
    
    status_fn(f"**Status: {kategori_text} ({damage_percentage:.2f}%)**")

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Persentase Kerusakan", f"{damage_percentage:.2f}%")
    col_m2.metric("Luas Total Daun", f"{total_leaf_pixels:,} px")
    col_m3.metric("Luas Kerusakan (HSV)", f"{total_disease_pixels:,} px")

    st.subheader("🎨 Visualisasi Segmentasi AI & HSV")
    col_img1, col_img2, col_img3 = st.columns(3)
    with col_img1:
        st.image(visualisasi_img, caption=f"Visualisasi Output ({kategori_text.lower()}: {damage_percentage:.2f}%)", use_container_width=True)
    with col_img2:
        st.image(leaf_mask_vis, caption="Mask Daun (YOLOv11)", use_container_width=True)
    with col_img3:
        st.image(disease_mask_vis, caption="Mask Kerusakan (HSV)", use_container_width=True)

    st.subheader("📝 Karakteristik & Kondisi")
    st.write(deskripsi)

    st.subheader("🛡️ Rekomendasi Tindakan")
    for solusi in solusi_list:
        st.markdown(f"- ➤ {solusi}")
