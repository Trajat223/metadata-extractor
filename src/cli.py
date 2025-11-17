import argparse
import sys
from rich import print_json
from .extractor import extract_metadata, to_pretty_json

def main():
    parser = argparse.ArgumentParser(description="Metadata Extractor CLI")
    parser.add_argument("file", help="Path to file to extract metadata from")
    parser.add_argument("--out", help="Write JSON output to file (optional)")
    args = parser.parse_args()

    path = args.file
    try:
        res = extract_metadata(path)
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    pretty = to_pretty_json(res)
    print(pretty)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(pretty)
        print(f"Saved output to {args.out}")

if __name__ == "__main__":
    main()

