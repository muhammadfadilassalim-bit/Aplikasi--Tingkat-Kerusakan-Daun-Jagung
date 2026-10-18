# Aplikasi Jagung - CornLeaf Guard

# Judul Aplikasi: Sistem Deteksi dan Analisis Tingkat Kerusakan Daun Jagung Berbasis YOLOv11 Segmentasi dan HSV Thresholding

## Struktur

```text
Aplikasi_Jagung/
├── main.py
├── requirements.txt
├── models/
│   ├── best.pt
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── templates/
    └── index.html
```

## 👥 Anggota Tim & Kontribusi

**Muhammad Fadil Assalim: Mengembangkan API FastAPI, middleware CORS/Ngrok, dan integrasi pipeline inferensi & Pelatihan model YOLOv11, eksperimentasi HSV thresholding, dan ekstraksi piksel mask.
**Vira Septiani: Perancangan UI/UX responsif, dual-input handler (kamera/upload), dan Fetch API integration.
**Bala Wardana Putra: Pengujian skenario penolakan non-daun, deployment Ngrok, dan penyusunan laporan/proposal.

## 🚀 Fitur Utama

* Deteksi penyakit daun jagung menggunakan YOLOv11.
* Segmentasi lesi penyakit dengan HSV Color Thresholding.
* API Backend responsif berbasis FastAPI.
* Antarmuka frontend dual-input (Kamera & Unggah Gambar).

## 🛠️ Cara Instalasi & Menjalankan Aplikasi

1. Clone repositori ini:
   ```bash
   git clone https://github.com
   ```
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan server backend:
   ```bash
   uvicorn main:app --reload
   ```

## 📊 Hasil Pengujian / Demo
<img width="1354" height="643" alt="apl_ui_1" src="https://github.com/user-attachments/assets/ca9a3037-30a7-470c-b262-b74afc8da565" />
