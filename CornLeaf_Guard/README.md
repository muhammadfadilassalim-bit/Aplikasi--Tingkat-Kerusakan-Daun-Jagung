# CornLeaf Guard — Streamlit

Aplikasi deteksi kerusakan daun jagung menggunakan segmentasi YOLOv11 dan HSV Thresholding.

## Struktur proyek

```text
CornLeaf_Guard_Streamlit/
├── streamlit_app.py
├── backend/
│   ├── __init__.py
│   ├── model_loader.py
│   └── image_processing.py
├── frontend/
│   ├── __init__.py
│   ├── styles.py
│   ├── components.py
│   └── results.py
├── models/
│   └── best.pt        # salin model YOLO milik Anda ke sini
├── requirements.txt
├── packages.txt
└── README.md
```

## Menjalankan lokal

1. Buat virtual environment.
2. Install dependensi:

   ```bash
   pip install -r requirements.txt
   ```

3. Pastikan file model tersedia di `models/best.pt`.
4. Jalankan:

   ```bash
   streamlit run streamlit_app.py
   ```

## Deploy ke Streamlit Community Cloud

1. Upload seluruh isi folder proyek ini ke repositori GitHub.
2. Pastikan `models/best.pt` ikut tersedia di repositori (perhatikan batas ukuran file GitHub).
3. Di Streamlit Community Cloud, pilih repositori, branch, dan file utama `streamlit_app.py`.
4. Deploy.

`packages.txt` berisi paket sistem yang dibutuhkan OpenCV. Dockerfile FastAPI/uvicorn dari proyek lama tidak diperlukan untuk deployment Streamlit tunggal ini.

## Catatan

- File bobot `models/best.pt` tidak disertakan dalam arsip starter ini. Salin dari proyek lama Anda.
- Kategori kerusakan dan ambang HSV dipertahankan sesuai implementasi Streamlit yang diberikan.
- Uji aplikasi lokal terlebih dahulu dengan beberapa citra daun jagung sebelum deployment.
