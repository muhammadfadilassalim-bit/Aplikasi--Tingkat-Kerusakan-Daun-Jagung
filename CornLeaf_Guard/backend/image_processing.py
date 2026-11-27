import cv2
import numpy as np

# Rentang HSV untuk mendeteksi warna bercak/penyakit (mengikuti kode awal).
HSV_LOWER_DISEASE = np.array([10, 40, 40])
HSV_UPPER_DISEASE = np.array([35, 255, 255])


def analyze_image(raw_bytes: bytes, model) -> dict:
    """
    Menjalankan deteksi segmentasi YOLOv11 dan HSV Thresholding.
    Mengembalikan status, gambar visualisasi, metrik, serta rekomendasi.
    """
    nparr = np.frombuffer(raw_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return {"status": "invalid_image"}

    height, width = img.shape[:2]
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 1. Prediksi segmentasi daun dengan YOLOv11.
    results = model.predict(img, conf=0.60, verbose=False)[0]

    if results.masks is None or len(results.masks) == 0:
        return {"status": "not_corn_leaf"}

    # 2. Gabungkan seluruh mask menjadi binary mask area daun.
    leaf_mask = np.zeros((height, width), dtype=np.uint8)
    for mask_data in results.masks.data:
        mask_np = mask_data.cpu().numpy()
        mask_resized = cv2.resize(
            mask_np, (width, height), interpolation=cv2.INTER_NEAREST
        )
        leaf_mask = np.bitwise_or(
            leaf_mask, (mask_resized > 0.5).astype(np.uint8)
        )

    total_leaf_pixels = int(np.sum(leaf_mask))
    if total_leaf_pixels == 0:
        return {"status": "empty_leaf_mask"}

    # 3. Deteksi warna bercak/kerusakan menggunakan HSV.
    disease_mask_full = cv2.inRange(
        hsv_img, HSV_LOWER_DISEASE, HSV_UPPER_DISEASE
    )
    disease_mask = cv2.bitwise_and(
        disease_mask_full, disease_mask_full, mask=leaf_mask
    )
    total_disease_pixels = int(np.count_nonzero(disease_mask))

    # 4. Persentase kerusakan.
    damage_percentage = (
        total_disease_pixels / total_leaf_pixels
    ) * 100.0

    # 5. Kategori dan rekomendasi (mengikuti batas pada kode awal).
    if damage_percentage < 1.0:
        category = "SEHAT"
        description = (
            "Daun terdeteksi dalam kondisi sehat secara umum dengan "
            "tingkat kerusakan minimal (< 1%)."
        )
        recommendations = [
            "Pertahankan pola pengairan yang konsisten.",
            "Berikan pupuk nitrogen secara berkala.",
            "Lakukan pemantauan rutin seminggu sekali.",
        ]
    elif 1.0 <= damage_percentage <= 30.0:
        category = "ADA KERUSAKAN"
        description = (
            "Terdeteksi adanya bercak/gejala penyakit pada daun dengan "
            f"tingkat kerusakan ringan-sedang ({damage_percentage:.2f}%)."
        )
        recommendations = [
            "Isolasi atau pangkas daun yang terinfeksi jika masih sedikit.",
            "Semprotkan fungisida organik atau berbahan aktif sesuai dosis anjuran.",
            "Jaga kebersihan area sekitar lahan tanaman.",
        ]
    else:
        category = "RUSAK PARAH"
        description = (
            "Daun mengalami kerusakan parah akibat infeksi bercak/penyakit "
            f"yang meluas ({damage_percentage:.2f}%)."
        )
        recommendations = [
            "Segera aplikasikan fungisida sistemik secara intensif.",
            "Pindahkan/karantina tanaman terinfeksi dari tanaman sehat.",
            "Lakukan rotasi tanaman untuk siklus tanam berikutnya.",
        ]

    # 6. Buat overlay dan mask visualisasi.
    visualisasi_img = img.copy()
    green_overlay = np.zeros_like(visualisasi_img)
    green_overlay[leaf_mask == 1] = [0, 255, 0]
    visualisasi_img = cv2.addWeighted(
        visualisasi_img, 0.85, green_overlay, 0.15, 0
    )
    visualisasi_img[disease_mask > 0] = [0, 0, 255]

    leaf_mask_vis = (leaf_mask * 255).astype(np.uint8)
    disease_mask_vis = (disease_mask > 0).astype(np.uint8) * 255

    return {
        "status": "success",
        "category": category,
        "damage_percentage": damage_percentage,
        "total_leaf_pixels": total_leaf_pixels,
        "total_disease_pixels": total_disease_pixels,
        "description": description,
        "recommendations": recommendations,
        "visualization": visualisasi_img,
        "leaf_mask": leaf_mask_vis,
        "disease_mask": disease_mask_vis,
    }
