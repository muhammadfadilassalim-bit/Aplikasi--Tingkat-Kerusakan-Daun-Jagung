# Aplikasi Jagung - CornLeaf Guard

Struktur project dirapikan dengan memisahkan CSS dan JavaScript dari template HTML. Logika analisis YOLO + HSV dan markup UI dipertahankan.

## Struktur

```text
Aplikasi_Jagung/
├── main.py
├── requirements.txt
├── models/
│   ├── best.pt              # salin model Anda ke sini
│   └── README.txt
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── templates/
    └── index.html
```

## Menjalankan aplikasi

1. Pastikan Python sudah terpasang.
2. Salin file model `best.pt` milik Anda ke folder `models/`.
3. Buat dan aktifkan virtual environment (opsional tetapi disarankan).
4. Pasang dependensi:

   ```bash
   pip install -r requirements.txt
   ```

5. Jalankan server dari folder project:

   ```bash
   uvicorn main:app --reload
   ```

6. Buka `http://127.0.0.1:8000`.

Catatan: akses kamera browser biasanya memerlukan localhost atau HTTPS. Tailwind CSS masih dimuat melalui CDN seperti pada project asli.
