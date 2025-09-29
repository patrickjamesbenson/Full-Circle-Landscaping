import base64
from pathlib import Path
import streamlit as st
from .xldb import ensure_workbook

APP_ROOT = Path(__file__).resolve().parents[1]
ASSETS = APP_ROOT / "assets"
CSS_PATH = ASSETS / "theme.css"

def _img64(path:Path):
    try:
        b = path.read_bytes()
        return "data:image/png;base64," + base64.b64encode(b).decode("ascii")
    except Exception:
        return None

def bootstrap(home=False):
    ensure_workbook()
    if CSS_PATH.exists():
        st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    if not home:
        data = _img64(ASSETS / "brand" / "logo.png")
        if data:
            st.markdown(f"<div class='brand-row'><img src='{data}' alt='logo'><div style='font-weight:700'>Full Circle</div></div>", unsafe_allow_html=True)

def brand_hero_home():
    data = _img64(ASSETS / "brand" / "logo_full.png") or _img64(ASSETS / "brand" / "logo.png")
    title = "<div style='font-weight:700;font-size:28px;'>Home</div>"
    if data:
        st.markdown(f"<div class='brand-row'><img src='{data}' alt='logo'>{title}</div>", unsafe_allow_html=True)
    else:
        st.markdown("## Home")

def section(title, subtitle=None):
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)
