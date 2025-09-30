# ===============================
# FILE: utils/ui.py  (REPLACE)
# ===============================
import os
import base64
from pathlib import Path
import streamlit as st
from .xldb import ensure_workbook, get_setting, set_setting

# ---- App meta (env-overridable) ----
VERSION = os.getenv("FULLCIRCLE_VERSION", "v5.5")
OWNER = os.getenv("FULLCIRCLE_OWNER", "LB Lighting")
PRODUCT = os.getenv("FULLCIRCLE_PRODUCT", "Small Business E2E Workflow")
YEAR = os.getenv("FULLCIRCLE_YEAR", "2025")

APP_ROOT = Path(__file__).resolve().parents[1]
ASSETS = APP_ROOT / "assets"
CSS_PATH = ASSETS / "theme.css"

def _img64(path: Path):
    try:
        return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")
    except Exception:
        return None

def _client_doc_url() -> str | None:
    ensure_workbook()
    url = os.getenv("FULLCIRCLE_CLIENT_DOC_URL") or get_setting("client_doc_url", "")
    url = (url or "").strip()
    return url or None

def _client_doc_badge_html(url: str) -> str:
    return (
        "<a href='{url}' target='_blank' rel='noopener noreferrer' style='text-decoration:none;'>"
        "<span style='display:inline-block;padding:4px 8px;border-radius:999px;"
        "background:#E8F0FE;color:#174EA6;font-size:12px;font-weight:600;'>"
        "📄 Client Brief (Google Doc)</span></a>"
    ).format(url=url)

def _icon_source() -> str:
    env = os.getenv("FULLCIRCLE_FAVICON")
    if env and Path(env).exists():
        return env
    fav = ASSETS / "brand" / "favicon.png"
    if fav.exists():
        return str(fav)
    logo = ASSETS / "brand" / "logo.png"
    if logo.exists():
        return str(logo)
    return "🌿"  # fallback emoji

def configure_page(title: str, *, home: bool = False) -> None:
    """
    Why: Use the page name only in the browser tab (no owner suffix).
    """
    st.set_page_config(page_title=title, page_icon=_icon_source(), layout="wide")

def bootstrap(home: bool = False):
    """Load CSS + brand row + client doc badge + sidebar link."""
    ensure_workbook()
    if CSS_PATH.exists():
        st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

    data = _img64(ASSETS / "brand" / "logo.png")
    title_html = "Home" if home else PRODUCT
    left = []
    if data:
        left.append(
            f"<img src='{data}' alt='logo' style='width:42px;height:42px;border-radius:8px;vertical-align:middle;margin-right:10px'>"
        )
    left.append(f"<span style='font-weight:700;vertical-align:middle'>{title_html}</span>")
    header_html = "<div class='brand-row'>" + "".join(left) + "</div>"

    url = _client_doc_url()
    badge = f" &nbsp; {_client_doc_badge_html(url)}" if url else ""
    st.markdown(header_html + badge, unsafe_allow_html=True)
    if url:
        st.sidebar.markdown(f"**Client Brief**  \n[{url}]({url})")

def section(title: str, subtitle: str | None = None):
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)

def footer(extra: str | None = None):
    note = f" • {extra}" if extra else ""
    st.markdown(
        f"<hr style='opacity:.3;margin-top:24px;margin-bottom:8px'>"
        f"<div style='font-size:12px;opacity:.8'>© {YEAR} {OWNER} • {PRODUCT} {VERSION}{note}</div>",
        unsafe_allow_html=True,
    )

def save_client_doc_url(url: str) -> None:
    set_setting("client_doc_url", (url or "").strip())

# Optional wrapper if you want one-liner page scaffolding.
from contextlib import contextmanager
@contextmanager
def page(title: str, subtitle: str | None = None, *, home: bool = False, show_footer: bool = True):
    configure_page(title, home=home)
    bootstrap(home=home)
    section(title, subtitle)
    try:
        yield
    finally:
        if show_footer:
            footer()
