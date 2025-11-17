# streamlit_app.py
import streamlit as st
import os
import string
from pathlib import Path
from src.extractor import extract_metadata
import tempfile
import shutil

# --- Helpers -----------------------------------------------------
def secure_filename(name: str) -> str:
    """
    Very small sanitizer: keep only basename and remove path-traversal.
    Replace spaces with underscores. Remove problematic chars.
    """
    base = os.path.basename(name)
    # basic sanitization: allow alphanum, dot, underscore, hyphen
    allowed = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned = "".join(c if c in allowed else "_" for c in base)
    return cleaned

def save_uploaded_file(uploaded_file, dest_dir="uploads"):
    """
    Save Streamlit uploaded file to uploads/<original_name>
    Returns the saved absolute path.
    """
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    # use original filename
    original_name = uploaded_file.name or "uploaded_file"
    # sanitize filename
    import string
    safe_name = secure_filename(original_name)

    # ensure we preserve the original extension by using the original name
    saved_path = os.path.join(dest_dir, safe_name)

    # If the same filename already exists, add a counter suffix
    if os.path.exists(saved_path):
        stem = Path(safe_name).stem
        suf = Path(safe_name).suffix
        i = 1
        while True:
            candidate = os.path.join(dest_dir, f"{stem}_{i}{suf}")
            if not os.path.exists(candidate):
                saved_path = candidate
                break
            i += 1

    # write file
    with open(saved_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return os.path.abspath(saved_path)

# --- UI ----------------------------------------------------------
st.set_page_config(page_title="Metadata Extractor — Demo", layout="wide")
st.title("Metadata Extractor — Demo")

uploaded = st.file_uploader("Upload a file (image/docx/pdf)", type=['jpg','jpeg','png','tiff','docx','pdf'])
if uploaded:
    # Save to uploads/ with original filename (sanitized)
    saved_path = save_uploaded_file(uploaded, dest_dir="uploads")

    st.success(f"Saved uploaded file as: `{saved_path}`")
    st.write("File saved to uploads folder (preserves original filename & extension).")

    # Run extractor
    md = extract_metadata(saved_path)

    # Basic cleaning helper to avoid bytes in JSON
    def clean_for_display(obj):
        if isinstance(obj, dict):
            return {k: clean_for_display(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean_for_display(v) for v in obj]
        if isinstance(obj, bytes):
            try:
                return obj.decode(errors="ignore")
            except:
                return str(obj)
        return obj

    st.subheader("Extracted Metadata (JSON)")
    st.json(clean_for_display(md))

    # Show key summary
    st.subheader("Quick file info")
    fi = md.get("file_info", {})
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Path**")
        st.write(fi.get("path"))
        st.write("**Name**")
        st.write(fi.get("name"))
        st.write("**Extension**")
        st.write(fi.get("extension"))
    with col2:
        st.write("**MIME Type**")
        st.write(fi.get("mime_type"))
        st.write("**Size (bytes)**")
        st.write(fi.get("size_bytes"))
        st.write("**SHA256**")
        st.write(fi.get("hashes", {}).get("sha256"))
