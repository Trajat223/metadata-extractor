# src/pdf_utils.py

from PyPDF2 import PdfReader


def extract_pdf_metadata(file_path):
    """Extract metadata from PDF using PyPDF2."""

    metadata = {
        "info": {},
        "pages": 0
    }

    try:
        reader = PdfReader(file_path)

        # Basic info
        if reader.metadata:
            for key, value in reader.metadata.items():
                cleaned_key = key.replace("/", "")
                metadata["info"][cleaned_key] = str(value)

        # Page count
        metadata["pages"] = len(reader.pages)

    except Exception as e:
        metadata["error"] = str(e)

    return metadata

