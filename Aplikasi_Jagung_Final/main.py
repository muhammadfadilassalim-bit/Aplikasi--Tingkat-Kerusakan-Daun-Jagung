import io
from pathlib import Path
import cv2
import base64
import numpy as np
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Sistem Deteksi Tingkat Kerusakan Daun Jagung")

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Middleware Ngrok Skip Warning Header
@app.middleware("http")
async def add_ngrok_skip_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# 3. Load Model YOLOv11 Segmentasi
try:
    model = YOLO(str(BASE_DIR / "models" / "best.pt"))
except Exception as e:
    print(f"Peringatan: Gagal memuat model 'models/best.pt'. Error: {e}")
    model = None

# Rentang HSV untuk mendeteksi warna bercak/penyakit (Cokelat / Kuning Tua / Layu)
HSV_LOWER_DISEASE = np.array([10, 40, 40])
HSV_UPPER_DISEASE = np.array([35, 255, 255])

def mat_to_base64(img_mat):
    """Fungsi pembantu mengonversi array gambar OpenCV ke string Base64."""
    _, buffer = cv2.imencode('.jpg', img_mat)
    return base64.b64encode(buffer).decode('utf-8')

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Merender halaman utama website."""
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/predict", response_class=HTMLResponse)
async def predict(file: UploadFile = File(...)):
    if model is None:
        return HTMLResponse(content="<div class='p-4 bg-red-100 text-red-700 rounded-lg'>Model AI gagal dimuat di server.</div>")
    
    try:
        # Baca file gambar dari form upload / kamera
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Format gambar tidak valid atau korup.")

        h, w, _ = img.shape
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 1. Predict Segmentasi Daun dengan YOLOv11
        results = model.predict(img, conf=0.60, verbose=False)[0]

        # Jika objek bukan daun jagung / tidak terdeteksi
        if results.masks is None or len(results.masks) == 0:
            return HTMLResponse(content="""
                <div class="p-5 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl text-center space-y-2 shadow-sm">
                    <div class="text-3xl">⚠️</div>
                    <p class="font-bold text-base text-amber-900">Gambar Bukan Daun Jagung</p>
                    <p class="text-xs text-amber-700 leading-relaxed">
                        Daun jagung tidak terdeteksi oleh sistem. Silakan pilih atau ambil foto sampel daun jagung secara jelas.
                    </p>
                </div>
            """)

        # 2. Buat Binary Mask Total Area Daun
        leaf_mask = np.zeros((h, w), dtype=np.uint8)
        for mask_data in results.masks.data:
            mask_np = mask_data.cpu().numpy()
            mask_resized = cv2.resize(mask_np, (w, h), interpolation=cv2.INTER_NEAREST)
            leaf_mask = np.bitwise_or(leaf_mask, (mask_resized > 0.5).astype(np.uint8))

        total_leaf_pixels = np.sum(leaf_mask)

        if total_leaf_pixels == 0:
            return HTMLResponse(content="""
                <div class="p-5 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl text-center space-y-2 shadow-sm">
                    <div class="text-3xl">⚠️</div>
                    <p class="font-bold text-base text-amber-900">Luas Area Daun 0 Piksel</p>
                </div>
            """)

        # 3. Deteksi Warna Kerusakan/Bercak Menggunakan HSV Thresholding
        disease_mask_full = cv2.inRange(hsv_img, HSV_LOWER_DISEASE, HSV_UPPER_DISEASE)
        disease_mask = cv2.bitwise_and(disease_mask_full, disease_mask_full, mask=leaf_mask)
        total_disease_pixels = np.count_nonzero(disease_mask)

        # 4. Hitung Persentase Kerusakan
        damage_percentage = (total_disease_pixels / total_leaf_pixels) * 100.0

        # 5. Pengkategorian Tingkat Kerusakan
        if damage_percentage < 1.0:
            kategori_text = "SEHAT"
            bg_badge = "bg-green-100 text-green-800"
            deskripsi = "Daun terdeteksi dalam kondisi sehat secara umum dengan tingkat kerusakan minimal (< 1%)."
            solusi_list = [
                "Pertahankan pola pengairan yang konsisten.",
                "Berikan pupuk nitrogen secara berkala.",
                "Lakukan pemantauan rutin seminggu sekali."
            ]
        elif damage_percentage <= 30.0:
            kategori_text = "ADA KERUSAKAN"
            bg_badge = "bg-amber-100 text-amber-800"
            deskripsi = f"Terdeteksi adanya bercak/gejala penyakit pada daun dengan tingkat kerusakan ringan-sedang ({damage_percentage:.2f}%)."
            solusi_list = [
                "Isolasi atau pangkas daun yang terinfeksi jika masih sedikit.",
                "Semprotkan fungisida organik atau berbahan aktif sesuai dosis anjuran.",
                "Jaga kebersihan area sekitar lahan tanaman."
            ]
        else:
            kategori_text = "RUSAK PARAH"
            bg_badge = "bg-red-100 text-red-800"
            deskripsi = f"Daun mengalami kerusakan parah akibat infeksi bercak/penyakit yang meluas ({damage_percentage:.2f}%)."
            solusi_list = [
                "Segera aplikasikan fungisida sistemik secara intensif.",
                "Pindahkan/karantina tanaman terinfeksi dari tanaman sehat.",
                "Lakukan rotasi tanaman untuk siklus tanam berikutnya."
            ]

        # 6. PEMBUATAN VISUALISASI GAMBAR (FITUR 1)
        # 6a. Visualisasi Overlay Kerusakan (Red Area)
        visualisasi_img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        green_overlay = np.zeros_like(visualisasi_img)
        green_overlay[leaf_mask == 1] = [0, 255, 0]
        visualisasi_img = cv2.addWeighted(visualisasi_img, 0.85, green_overlay, 0.15, 0)
        visualisasi_img[disease_mask > 0] = [0, 0, 255] # Merah solid untuk kerusakan

        # 6b. Mask Daun (Hitam Putih)
        leaf_mask_vis = (leaf_mask * 255).astype(np.uint8)

        # 6c. Mask Kerusakan (Hitam Putih)
        disease_mask_vis = (disease_mask > 0).astype(np.uint8) * 255

        # Konversi ketiga gambar ke Base64
        b64_visual = mat_to_base64(visualisasi_img)
        b64_leaf_mask = mat_to_base64(leaf_mask_vis)
        b64_disease_mask = mat_to_base64(disease_mask_vis)

        solusi_html = "".join([f"<li class='flex items-start'><span class='text-emerald-500 mr-2'>➤</span> {s}</li>" for s in solusi_list])

        # Tampilan HTML Hasil Diagnosis & Visualisasi
        return HTMLResponse(content=f"""
            <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
                <div class="flex justify-between items-center border-b border-slate-200 pb-3">
                    <h3 class="font-bold text-lg text-slate-800">📋 Hasil Diagnosis Tingkat Kerusakan</h3>
                    <span class="px-3 py-1 text-xs font-semibold rounded-full {bg_badge}">
                        {kategori_text} ({damage_percentage:.2f}%)
                    </span>
                </div>
                
                <div class="grid grid-cols-2 gap-2 text-xs bg-slate-50 p-3 rounded-lg border border-slate-200">
                    <div>
                        <span class="text-slate-500 block">Luas Total Daun:</span>
                        <strong class="text-slate-800 text-sm">{total_leaf_pixels:,} px</strong>
                    </div>
                    <div>
                        <span class="text-slate-500 block">Luas Kerusakan (HSV):</span>
                        <strong class="text-rose-600 text-sm">{total_disease_pixels:,} px</strong>
                    </div>
                </div>

                <!-- FITUR 1: PANEL TAMPILAN VISUALISASI MASKING -->
                <div class="space-y-2 pt-2 border-t border-slate-200">
                    <h4 class="font-semibold text-slate-700 text-sm uppercase tracking-wider">🎨 Visualisasi Segmentasi AI & HSV:</h4>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
                        <div class="bg-slate-900 rounded-lg overflow-hidden border border-slate-300 text-center">
                            <img src="data:image/jpeg;base64,{b64_visual}" class="w-full h-40 object-cover" alt="Visualisasi Overlay">
                            <div class="p-1.5 bg-slate-800 text-white font-semibold text-[11px]">
                                Visualisasi Output<br><span class="text-amber-400">({kategori_text.lower()}: {damage_percentage:.2f}%)</span>
                            </div>
                        </div>

                        <div class="bg-slate-900 rounded-lg overflow-hidden border border-slate-300 text-center">
                            <img src="data:image/jpeg;base64,{b64_leaf_mask}" class="w-full h-40 object-cover" alt="Mask Daun">
                            <div class="p-1.5 bg-slate-800 text-white font-semibold text-[11px]">
                                Mask Daun (YOLOv11)
                            </div>
                        </div>

                        <div class="bg-slate-900 rounded-lg overflow-hidden border border-slate-300 text-center">
                            <img src="data:image/jpeg;base64,{b64_disease_mask}" class="w-full h-40 object-cover" alt="Mask Kerusakan">
                            <div class="p-1.5 bg-slate-800 text-white font-semibold text-[11px]">
                                Mask Kerusakan (HSV)
                            </div>
                        </div>
                    </div>
                </div>

                <div class="space-y-1 pt-2 border-t border-dashed border-slate-200">
                    <h4 class="font-semibold text-slate-700 text-sm uppercase tracking-wider">Karakteristik & Kondisi:</h4>
                    <p class="text-slate-600 text-sm leading-relaxed">{deskripsi}</p>
                </div>

                <div class="space-y-2 pt-2 border-t border-dashed border-slate-200">
                    <h4 class="font-semibold text-emerald-700 text-sm uppercase tracking-wider">🛡️ Rekomendasi Tindakan:</h4>
                    <ul class="text-slate-600 text-sm space-y-1.5 font-medium">
                        {solusi_html}
                    </ul>
                </div>
            </div>
        """)
        
    except Exception as e:
        return HTMLResponse(content=f"""
            <div class="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">
                <p class="font-bold">❌ Gagal Menganalisis Gambar</p>
                <p class="text-xs mt-1 text-red-600">{str(e)}</p>
            </div>
        """)