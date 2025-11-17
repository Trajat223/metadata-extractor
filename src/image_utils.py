from PIL import Image, ExifTags

def exif_from_image(path):
    try:
        img = Image.open(path)
    except Exception as e:
        return {"error": f"cannot open image: {e}"}

    exif_raw = img._getexif() or {}
    decoded = {}

    for k, v in exif_raw.items():
        tag = ExifTags.TAGS.get(k, k)
        decoded[tag] = v

    # Extract GPS info
    gps = {}
    if "GPSInfo" in decoded:
        gps_info = decoded["GPSInfo"]
        gps_decoded = {}

        for t, val in gps_info.items():
            subtag = ExifTags.GPSTAGS.get(t, t)
            gps_decoded[subtag] = val

        gps = gps_decoded

    if gps:
        decoded["GPS"] = gps

    return decoded


def gps_to_decimal(gps):
    """Convert GPS EXIF format to decimal coordinates."""
    def _to_deg(values):
        d = values[0][0] / values[0][1]
        m = values[1][0] / values[1][1]
        s = values[2][0] / values[2][1]
        return d + m / 60 + s / 3600

    if not gps:
        return None

    try:
        lat = _to_deg(gps["GPSLatitude"])
        if gps.get("GPSLatitudeRef", "N") in ["S", "s"]:
            lat = -lat

        lon = _to_deg(gps["GPSLongitude"])
        if gps.get("GPSLongitudeRef", "E") in ["W", "w"]:
            lon = -lon

        return {"latitude": lat, "longitude": lon}

    except Exception:
        return None


def extract_image_metadata(file_path):
    """
    Wrapper required by the extractor.
    Returns structured EXIF + GPS metadata.
    """
    metadata = exif_from_image(file_path)
    gps = metadata.get("GPS", {})
    decimal = gps_to_decimal(gps) if gps else None

    return {
        "type": "image",
        "raw_exif": metadata,
        "gps_decimal": decimal
    }
