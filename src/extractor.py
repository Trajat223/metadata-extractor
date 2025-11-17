# src/extractor.py
import os
import mimetypes
from pathlib import Path
import hashlib

# Import the wrapper functions that are present in your project
from .image_utils import extract_image_metadata
from .docx_utils import extract_docx_metadata
from .pdf_utils import extract_pdf_metadata
from .fs_utils import file_system_metadata


# ---------------------------
# HASHING (Forensic objective)
# ---------------------------
def compute_hashes(file_path):
    """Compute MD5, SHA1, SHA256 for the given file_path."""
    hashes = {"md5": None, "sha1": None, "sha256": None}
    try:
        with open(file_path, "rb") as f:
            # read in chunks to handle large files
            md5 = hashlib.md5()
            sha1 = hashlib.sha1()
            sha256 = hashlib.sha256()
            for chunk in iter(lambda: f.read(8192), b""):
                md5.update(chunk)
                sha1.update(chunk)
                sha256.update(chunk)
            hashes["md5"] = md5.hexdigest()
            hashes["sha1"] = sha1.hexdigest()
            hashes["sha256"] = sha256.hexdigest()
    except Exception as e:
        hashes["error"] = str(e)
    return hashes


# ---------------------------
# FILE TYPE DETECTION
# ---------------------------
def detect_file_type(path):
    """Detect file type from extension (simple and reliable for uploads)."""
    ext = Path(path).suffix.lower()
    if ext in [".jpg", ".jpeg", ".png", ".tif", ".tiff"]:
        return "image"
    if ext == ".pdf":
        return "pdf"
    if ext == ".docx":
        return "docx"
    return "unknown"


# ---------------------------
# MASTER EXTRACTOR
# ---------------------------
def extract_metadata(file_path):
    """
    Return a dictionary with:
      - file_info: forensic file-level fields (path, name, size, created/modified, hashes, mime)
      - type: detected type (image/pdf/docx/unknown)
      - extracted_metadata: type-specific metadata returned by each module
    """
    file_path = str(file_path)
    file_name = os.path.basename(file_path)
    extension = Path(file_path).suffix.lower().lstrip(".")
    mime_type = mimetypes.guess_type(file_path)[0]

    # file size
    try:
        file_size = os.path.getsize(file_path)
    except Exception:
        file_size = None

    # file system metadata (created/modified)
    try:
        fs_meta = file_system_metadata(file_path)
    except Exception:
        fs_meta = {}

    # compute hashes
    hashes = compute_hashes(file_path)

    # detect file type
    file_type = detect_file_type(file_path)

    # extract type-specific metadata using the wrappers you already have
    extracted = {}
    try:
        if file_type == "image":
            extracted = extract_image_metadata(file_path)
        elif file_type == "pdf":
            extracted = extract_pdf_metadata(file_path)
        elif file_type == "docx":
            extracted = extract_docx_metadata(file_path)
        else:
            extracted = {}
    except Exception as e:
        extracted = {"error": f"extraction failed: {e}"}

    # final structured response
    return {
        "file_info": {
            "path": file_path,
            "name": file_name,
            "extension": extension,
            "mime_type": mime_type,
            "size_bytes": file_size,
            "fs": fs_meta,       # created/modified from fs_utils if available
            "hashes": hashes
        },
        "type": file_type,
        "extracted_metadata": extracted
    }


# Small helper for pretty JSON printing if you need it
def to_pretty_json(obj):
    import json
    return json.dumps(obj, indent=2, ensure_ascii=False)
