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
    """Top-left floating logo (not on Home)."""
    small = os.path.join(BRAND_DIR, "logo.png")
    data = _embed_img_base64(small)
    if data:
        html = (
            "<div id=\"fcg-fixed-logo\"><img src=\""
            + data
            + "\" alt=\"Full Circle Gardens\"></div>"
        )
        st.markdown(html, unsafe_allow_html=True)

def bootstrap(show_logo=True, seed_now=True):
    conn = get_conn()
    init_db(conn)
    if seed_now: ensure_seed(conn)
    _inject_css()
    if show_logo: _fixed_logo()
    return conn

def section(title, subtitle=None):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)

def brand_hero():
    """Logo-with-name hero for Home page (no floating logo here)."""
    full = os.path.join(BRAND_DIR, "logo_full.png")
    data = _embed_img_base64(full)
    if data:
        html = (
            "<div style=\"display:flex;align-items:center;gap:16px;margin-top:-12px;\">"
            f"<img src='{data}' alt='Full Circle Gardens' style='max-height:64px;width:auto;'>"
            "<div style=\"font-family:'Cormorant Garamond',serif;font-size:28px;line-height:1.1;\"><strong>Full Circle Control Centre</strong></div>"
            "</div>"
        )
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown("### Full Circle Control Centre")
