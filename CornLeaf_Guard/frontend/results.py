import base64
import cv2
import html


def _image_base64(image):
    if image.ndim == 2:
        success, buffer = cv2.imencode(".jpg", image)
    else:
        success, buffer = cv2.imencode(".jpg", image)
    if not success:
        raise ValueError("Gambar hasil analisis gagal dikodekan.")
    return base64.b64encode(buffer).decode("utf-8")


def build_result_html(result: dict):
    status = result.get("status")

    if status == "invalid_image":
        return (
            '<div style="padding:16px;background:#fef2f2;border:1px solid #fecaca;'
            'color:#b91c1c;border-radius:12px;text-align:center;">'
            '<strong>❌ Gagal Menganalisis Gambar</strong>'
            '<p style="font-size:12px;margin-top:4px;">'
            'Format gambar tidak valid atau korup.</p></div>'
        )

    if status == "not_corn_leaf":
        return (
            '<div style="padding:20px;background:#fffbeb;border:1px solid #fde68a;'
            'color:#92400e;border-radius:16px;text-align:center;">'
            '<div style="font-size:28px;">⚠️</div>'
            '<p style="font-weight:700;font-size:16px;color:#78350f;margin:6px 0 4px 0;">'
            'Gambar Bukan Daun Jagung</p>'
            '<p style="font-size:12px;color:#b45309;margin:0;">'
            'Daun jagung tidak terdeteksi oleh sistem. Silakan pilih atau ambil '
            'foto sampel daun jagung secara jelas.</p></div>'
        )

    if status == "empty_leaf_mask":
        return (
            '<div style="padding:20px;background:#fffbeb;border:1px solid #fde68a;'
            'color:#92400e;border-radius:16px;text-align:center;">'
            '<div style="font-size:28px;">⚠️</div>'
            '<p style="font-weight:700;font-size:16px;margin:6px 0 0 0;">'
            'Luas Area Daun 0 Piksel</p></div>'
        )

    category = result["category"]
    damage = result["damage_percentage"]
    badge_styles = {
        "SEHAT": "background-color:#dcfce7;color:#166534;",
        "ADA KERUSAKAN": "background-color:#fef3c7;color:#92400e;",
        "RUSAK PARAH": "background-color:#fee2e2;color:#991b1b;",
    }
    badge_style = badge_styles[category]

    visual_b64 = _image_base64(result["visualization"])
    leaf_b64 = _image_base64(result["leaf_mask"])
    disease_b64 = _image_base64(result["disease_mask"])

    recommendations = "".join(
        "<li style='display:flex;align-items:flex-start;margin-bottom:6px;'>"
        "<span style='color:#10b981;margin-right:8px;'>➤</span>"
        f"<span>{html.escape(item)}</span></li>"
        for item in result["recommendations"]
    )

    return (
        '<div class="custom-card">'
        '<div style="display:flex;justify-content:space-between;align-items:center;'
        'border-bottom:1px solid #e2e8f0;padding-bottom:12px;margin-bottom:14px;'
        'flex-wrap:wrap;gap:8px;">'
        '<h3 style="font-weight:700;font-size:18px;color:#1e293b;margin:0;">'
        '📋 Hasil Diagnosis Tingkat Kerusakan</h3>'
        f'<span style="padding:4px 12px;font-size:12px;font-weight:700;'
        f'border-radius:9999px;{badge_style}">{category} ({damage:.2f}%)</span>'
        '</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;'
        'font-size:12px;background:#f8fafc;padding:12px;border-radius:10px;'
        'border:1px solid #e2e8f0;margin-bottom:16px;">'
        '<div><span style="color:#64748b;display:block;">Luas Total Daun:</span>'
        f'<strong style="color:#1e293b;font-size:15px;">'
        f'{result["total_leaf_pixels"]:,} px</strong></div>'
        '<div><span style="color:#64748b;display:block;">Luas Kerusakan (HSV):</span>'
        f'<strong style="color:#e11d48;font-size:15px;">'
        f'{result["total_disease_pixels"]:,} px</strong></div></div>'
        '<div style="border-top:1px solid #e2e8f0;padding-top:14px;margin-bottom:16px;">'
        '<h4 style="font-weight:700;color:#334155;font-size:13px;'
        'text-transform:uppercase;letter-spacing:.04em;margin:0 0 8px 0;">'
        '🎨 Visualisasi Segmentasi AI & HSV:</h4>'
        '<div class="vis-grid">'
        f'<div class="vis-card"><img src="data:image/jpeg;base64,{visual_b64}" '
        'alt="Visualisasi Overlay"><div class="vis-caption">Visualisasi Output<br>'
        f'<span style="color:#fbbf24;">({category.lower()}: {damage:.2f}%)'
        '</span></div></div>'
        f'<div class="vis-card"><img src="data:image/jpeg;base64,{leaf_b64}" '
        'alt="Mask Daun"><div class="vis-caption">Mask Daun (YOLOv11)</div></div>'
        f'<div class="vis-card"><img src="data:image/jpeg;base64,{disease_b64}" '
        'alt="Mask Kerusakan"><div class="vis-caption">Mask Kerusakan (HSV)</div></div>'
        '</div></div>'
        '<div style="border-top:1px dashed #e2e8f0;padding-top:12px;margin-bottom:14px;">'
        '<h4 style="font-weight:700;color:#334155;font-size:13px;'
        'text-transform:uppercase;letter-spacing:.04em;margin:0 0 6px 0;">'
        'Karakteristik & Kondisi:</h4>'
        f'<p style="color:#475569;font-size:14px;line-height:1.6;margin:0;">'
        f'{html.escape(result["description"])}</p></div>'
        '<div style="border-top:1px dashed #e2e8f0;padding-top:12px;">'
        '<h4 style="font-weight:700;color:#047857;font-size:13px;'
        'text-transform:uppercase;letter-spacing:.04em;margin:0 0 8px 0;">'
        '🛡️ Rekomendasi Tindakan:</h4>'
        '<ul style="color:#475569;font-size:14px;list-style:none;padding:0;'
        f'margin:0;font-weight:500;">{recommendations}</ul></div></div>'
    )
