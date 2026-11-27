import base64
import html
import streamlit as st


def render_header():
    st.markdown(
        """
        <div class="custom-header">
          <div class="logo-flex">
            <div class="logo-icon">🌽</div>
            <div>
              <div style="font-weight:700;font-size:20px;line-height:1.2;">
                CornLeaf Guard
              </div>
              <div style="font-size:11px;color:#a7f3d0;margin-top:2px;">
                Sistem Pemantauan Kesehatan Komoditas Jagung
              </div>
            </div>
          </div>
          <div><span class="badge-active">YOLOv11 + HSV ACTIVE</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_input_tabs():
    active_file = None
    active_source = None

    tab_upload, tab_camera = st.tabs(
        ["📁 Upload Foto File", "📸 Kamera Direct"]
    )

    with tab_upload:
        file_input = st.file_uploader(
            "Pilih Gambar dari Perangkat",
            type=["jpg", "jpeg", "png"],
            key="upload_widget",
        )
        if file_input is not None:
            render_preview(file_input, "upload")
            st.markdown(
                """
                <div class="status-bar-row">
                  <span>File telah dipilih</span>
                  <span style="color:#059669;font-weight:600;">
                    ● File Siap Dianalisis
                  </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "🔍 Analisis File Gambar",
                type="primary",
                use_container_width=True,
                key="btn_scan_upload",
            ):
                active_file = file_input
                active_source = "upload"
        else:
            st.markdown(
                """
                <div class="status-bar-row">
                  <span>Belum ada gambar dipilih</span>
                  <span style="color:#64748b;">● Mode Upload File</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab_camera:
        camera_input = st.camera_input(
            "Potret Gambar Daun", key="camera_widget"
        )
        if camera_input is not None:
            if st.button(
                "🔍 Analisis Hasil Potret",
                type="primary",
                use_container_width=True,
                key="btn_scan_cam",
            ):
                active_file = camera_input
                active_source = "camera"

    return active_file, active_source, file_input, camera_input


def render_preview(uploaded_file, source):
    raw = uploaded_file.getvalue()
    encoded = base64.b64encode(raw).decode("utf-8")
    mime = getattr(uploaded_file, "type", None) or "image/jpeg"

    if source == "upload":
        safe_name = html.escape(getattr(uploaded_file, "name", "gambar"))
        label = f"Nama File: <strong>{safe_name}</strong>"
    else:
        label = "Sumber Gambar: <strong>Kamera Direct</strong>"

    st.markdown(
        f"""
        <div class="status-bar-row">
          <span>{label}</span>
          <span style="color:#059669;font-weight:600;">● File Siap Dianalisis</span>
        </div>
        <div class="preview-box">
          <img src="data:{mime};base64,{encoded}"
               alt="Preview Gambar Daun Jagung">
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis_section(analysis_html):
    st.markdown(
        '<div class="section-label">🔬 HASIL ANALISIS SEGMENTASI INSTAN</div>',
        unsafe_allow_html=True,
    )
    if analysis_html is None:
        st.markdown(
            """
            <div class="placeholder-box">
              Silakan aktifkan kamera di atas atau upload file gambar daun
              untuk memicu proses analisis.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(analysis_html, unsafe_allow_html=True)


def render_sidebar():
    st.markdown(
        """
        <div class="custom-card">
          <div style="border-bottom:1px solid #f1f5f9;padding-bottom:10px;margin-bottom:16px;">
            <h2 style="font-weight:700;color:#1e293b;font-size:16px;margin:0;">
              📚 Kriteria Tingkat Kerusakan
            </h2>
          </div>
          <div class="kriteria-item">
            <div style="font-weight:700;font-size:14px;color:#047857;">
              🟢 DAUN SEHAT
            </div>
            <p style="font-size:12px;color:#475569;margin:4px 0 0 0;">
              Luas area bercak/kerusakan pada daun kurang dari 1.0%.
            </p>
          </div>
          <div class="kriteria-item">
            <div style="font-weight:700;font-size:14px;color:#b45309;">
              🟡 ADA KERUSAKAN
            </div>
            <p style="font-size:12px;color:#475569;margin:4px 0 0 0;">
              Luas area bercak/kerusakan pada daun berkisar antara 1.0% - 30.0%.
            </p>
          </div>
          <div class="kriteria-item" style="margin-bottom:0;">
            <div style="font-weight:700;font-size:14px;color:#be123c;">
              🔴 RUSAK PARAH
            </div>
            <p style="font-size:12px;color:#475569;margin:4px 0 0 0;">
              Luas area bercak/kerusakan pada daun lebih dari 30.0%.
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        """
        <div class="custom-footer">
          &copy; 2026 CornLeaf Guard - Universitas Pertanian Cerdas AI.
          All Rights Reserved.
        </div>
        """,
        unsafe_allow_html=True,
    )
