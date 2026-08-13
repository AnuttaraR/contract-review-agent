import base64
import io
import os
import pandas as pd
import pdfplumber
from PIL import Image


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pdfplumber."""
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
    return "\n\n".join(text_parts)


def parse_csv(file_bytes: bytes, filename: str = "") -> str:
    """Convert CSV/Excel to a readable text representation."""
    try:
        if filename.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            df = pd.read_csv(io.BytesIO(file_bytes))
        summary_lines = [
            f"Document: {filename}",
            f"Rows: {len(df)}, Columns: {len(df.columns)}",
            f"Column headers: {', '.join(str(c) for c in df.columns)}",
            "",
            "Data:",
            df.to_string(index=False, max_rows=200),
        ]
        return "\n".join(summary_lines)
    except Exception as e:
        raise ValueError(f"CSV/Excel parse error: {e}")


def image_to_base64(file_bytes: bytes) -> tuple[str, str]:
    """Return (base64_data, media_type) for an image."""
    img = Image.open(io.BytesIO(file_bytes))
    fmt = img.format or "PNG"
    media_type_map = {
        "JPEG": "image/jpeg",
        "JPG": "image/jpeg",
        "PNG": "image/png",
        "GIF": "image/gif",
        "WEBP": "image/webp",
    }
    media_type = media_type_map.get(fmt.upper(), "image/png")

    buf = io.BytesIO()
    img.save(buf, format=fmt if fmt != "JPG" else "JPEG")
    b64 = base64.standard_b64encode(buf.getvalue()).decode("utf-8")
    return b64, media_type


def detect_file_type(filename: str, content_type: str = "") -> str:
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext == "pdf":
        return "pdf"
    if ext in ("csv",):
        return "csv"
    if ext in ("xlsx", "xls"):
        return "excel"
    if ext in ("png", "jpg", "jpeg", "gif", "webp", "tiff", "bmp"):
        return "image"
    if "pdf" in content_type:
        return "pdf"
    if "image" in content_type:
        return "image"
    if "csv" in content_type or "spreadsheet" in content_type:
        return "csv"
    return "unknown"


def parse_document(file_bytes: bytes, filename: str, content_type: str = "") -> dict:
    """
    Returns {
        'file_type': str,
        'raw_text': str | None,
        'image_b64': str | None,
        'image_media_type': str | None
    }
    """
    file_type = detect_file_type(filename, content_type)

    if file_type == "pdf":
        text = parse_pdf(file_bytes)
        return {"file_type": "pdf", "raw_text": text, "image_b64": None, "image_media_type": None}

    if file_type in ("csv", "excel"):
        text = parse_csv(file_bytes, filename)
        return {"file_type": file_type, "raw_text": text, "image_b64": None, "image_media_type": None}

    if file_type == "image":
        b64, media_type = image_to_base64(file_bytes)
        return {"file_type": "image", "raw_text": None, "image_b64": b64, "image_media_type": media_type}

    raise ValueError(f"Unsupported file type for: {filename}")
