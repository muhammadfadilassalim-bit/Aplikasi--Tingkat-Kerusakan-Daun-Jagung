import streamlit as st


def apply_styles():
    st.markdown(
        """
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
                font-family: system-ui, -apple-system, BlinkMacSystemFont,
                'Segoe UI', Roboto, sans-serif;
                background-color: #f8fafc;
                color: #0f172a;
            }
            .custom-header {
                background: linear-gradient(to right, #065f46, #0f766e);
                color: white; padding: 16px 24px;
                border-radius: 0 0 16px 16px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,.1);
                margin-bottom: 24px; display: flex;
                justify-content: space-between; align-items: center;
                flex-wrap: wrap; gap: 12px;
            }
            .logo-flex { display: flex; align-items: center; gap: 12px; }
            .logo-icon {
                background: rgba(255,255,255,.2); padding: 8px 12px;
                border-radius: 12px; font-size: 24px;
            }
            .badge-active {
                font-size: 12px; background: #064e3b;
                padding: 5px 14px; border-radius: 9999px;
                color: #d1fae5; font-weight: 600;
                border: 1px solid rgba(167,243,208,.25);
            }
            .custom-card {
                background: white; border-radius: 16px;
                border: 1px solid #e2e8f0; padding: 20px;
                box-shadow: 0 1px 3px 0 rgba(0,0,0,.08);
                margin-bottom: 20px;
            }
            .section-label {
                margin-top: 8px; margin-bottom: 12px;
                font-weight: 700; color: #64748b;
                font-size: 13px; letter-spacing: .05em;
            }
            .placeholder-box {
                padding: 36px 24px; text-align: center;
                font-size: 14px; color: #94a3b8;
                border: 1px dashed #cbd5e1; border-radius: 16px;
                background: white;
            }
            .preview-box {
                width: 100%; background: #0f172a;
                border-radius: 12px; overflow: hidden;
                border: 1px solid #cbd5e1;
                margin-top: 12px; margin-bottom: 14px;
                text-align: center;
            }
            .preview-box img {
                width: 100%; max-height: 360px;
                object-fit: cover; display: block;
            }
            .status-bar-row {
                display: flex; justify-content: space-between;
                align-items: center; margin-bottom: 8px;
                font-size: 12px; color: #64748b;
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px; border-bottom: 1px solid #f1f5f9;
                padding-bottom: 8px;
            }
            .stTabs [data-baseweb="tab"] {
                background: #e2e8f0; color: #475569;
                border-radius: 8px; padding: 6px 16px;
                font-weight: 600; font-size: 13px;
            }
            .stTabs [aria-selected="true"] {
                background: #059669 !important; color: white !important;
            }
            div.stButton > button[kind="primary"] {
                background: #d97706 !important;
                border-color: #d97706 !important; color: white !important;
                font-weight: 700 !important; border-radius: 12px !important;
                padding: .6rem 1rem !important; width: 100%;
            }
            div.stButton > button[kind="primary"]:hover {
                background: #b45309 !important;
                border-color: #b45309 !important;
            }
            .kriteria-item {
                padding: 12px 14px; background: #f8fafc;
                border: 1px solid #e2e8f0; border-radius: 12px;
                margin-bottom: 12px;
            }
            .vis-grid {
                display: grid; grid-template-columns: repeat(3, 1fr);
                gap: 12px; margin-top: 10px;
            }
            @media (max-width: 768px) {
                .vis-grid { grid-template-columns: 1fr; }
            }
            .vis-card {
                background: #0f172a; border-radius: 10px;
                overflow: hidden; border: 1px solid #cbd5e1;
                text-align: center;
            }
            .vis-card img {
                width: 100%; height: 175px;
                object-fit: cover; display: block;
            }
            .vis-caption {
                padding: 8px; background: #1e293b; color: white;
                font-weight: 600; font-size: 11px;
            }
            .custom-footer {
                width: 100%; background: white;
                border-top: 1px solid #e2e8f0; text-align: center;
                padding: 14px 0; font-size: 12px; color: #94a3b8;
                font-weight: 500; margin-top: 32px; border-radius: 12px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
