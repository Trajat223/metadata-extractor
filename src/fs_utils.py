from pathlib import Path
import datetime

def file_system_metadata(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    st = p.stat()
    return {
        "name": p.name,
        "path": str(p.resolve()),
        "size_bytes": st.st_size,
        "created": datetime.datetime.fromtimestamp(st.st_ctime).isoformat(),
        "modified": datetime.datetime.fromtimestamp(st.st_mtime).isoformat(),
    }
