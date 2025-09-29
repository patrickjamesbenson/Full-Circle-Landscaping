# ==========================================
# FILE: tools/patch_pages.py  (NEW, Windows OK)
# ==========================================
# Injects:
#  - from utils.ui import configure_page, footer
#  - configure_page("Title", home=...) after imports
#  - footer() at end
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "FullCircle-Home.py"
PAGES_DIR = ROOT / "pages"

def guess_title(text: str, path: Path) -> str:
    m = re.search(r'section\(\s*"([^"]+)"', text)
    if m:
        return m.group(1)
    if path.name == "FullCircle-Home.py":
        return "Home"
    stem = re.sub(r"^\d+[_-]?", "", path.stem).replace("_", " ").replace("-", " ").strip()
    return stem.title() or "Page"

def ensure_imports(txt: str) -> str:
    if "from utils.ui import" in txt:
        def repl(m):
            names = m.group(1)
            add = []
            if "configure_page" not in names: add.append("configure_page")
            if "footer" not in names: add.append("footer")
            if add: names = names.rstrip() + ", " + ", ".join(add)
            return f"from utils.ui import {names}\n"
        return re.sub(r"from utils\.ui import ([^\n]+)\n", repl, txt, count=1)
    return "from utils.ui import configure_page, footer\n" + txt

def ensure_configure_page(txt: str, title: str, home_flag: bool) -> str:
    if "configure_page(" in txt:
        return txt
    # Remove any direct st.set_page_config(...) to avoid duplicate call
    txt = re.sub(r"(?m)^ *st\.set_page_config\([^\n]*\)\s*\n", "", txt)
    lines = txt.splitlines(True)
    insert_at = 0
    for i, line in enumerate(lines[:60]):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1
        else:
            if insert_at: break
    cfg = f'configure_page("{title}", home={"True" if home_flag else "False"})\n'
    lines.insert(insert_at, cfg)
    return "".join(lines)

def ensure_footer(txt: str) -> str:
    if re.search(r'\bfooter\(\)\s*$', txt, flags=re.S):
        return txt
    return txt.rstrip() + "\n\nfooter()\n"

def patch_file(path: Path):
    txt = path.read_text(encoding="utf-8")
    title = guess_title(txt, path)
    txt = ensure_imports(txt)
    txt = ensure_configure_page(txt, title, home_flag=(path.name == "FullCircle-Home.py"))
    txt = ensure_footer(txt)
    path.write_text(txt, encoding="utf-8")
    print(f"Patched: {path.relative_to(ROOT)}  -> title='{title}'")

def main():
    targets = []
    if HOME.exists(): targets.append(HOME)
    if PAGES_DIR.exists(): targets += sorted(PAGES_DIR.glob("*.py"))
    if not targets:
        print("No targets found.")
        return 0
    for p in targets: patch_file(p)
    print("\nDone. Refresh Streamlit.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

