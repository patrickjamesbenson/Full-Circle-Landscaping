import os, base64, streamlit as st
from .db import get_conn, init_db
from .seed import ensure_seed

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
BRAND_DIR  = os.path.join(ASSETS_DIR, "brand")
THEME_CSS  = os.path.join(ASSETS_DIR, "theme.css")

def _embed_img_base64(path):
    try:
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")
    except Exception:
        return None

def _inject_css():
    if os.path.exists(THEME_CSS):
        with open(THEME_CSS, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def _fixed_logo():
    # small logo shown on all pages (top-right)
    small = os.path.join(BRAND_DIR, "logo.png")
    data = _embed_img_base64(small)
    if data:
        st.markdown(f"""
            <div id="fcg-fixed-logo"><img src="{data}" alt="Full Circle Gardens"></div>
        """, unsafe_allow_html=True)

def bootstrap():
    """Initialise DB, seed first run, inject skin + fixed logo."""
    conn = get_conn()
    init_db(conn)
    ensure_seed(conn)
    _inject_css()
    _fixed_logo()
    return conn

def section(title, subtitle=None):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)

def brand_hero():
    """Big lockup on Home page."""
    full = os.path.join(BRAND_DIR, "logo_full.png")
    data = _embed_img_base64(full)
    if data:
        st.markdown(
            f'<div style="text-align:center;margin:-10px 0 10px 0;">'
            f'<img src="{data}" alt="Full Circle Gardens" style="max-width:320px;height:auto;">'
            f"</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;margin-top:-6px;'>Full Circle Control Centre</h2>", unsafe_allow_html=True)
