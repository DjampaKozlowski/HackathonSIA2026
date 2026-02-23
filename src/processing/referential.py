import json
from pathlib import Path
from typing import Any, Dict


def read_referential_json(fpath: str | Path) -> Dict[str, Any]:
    """Read a JSON file and return a dictionary.

    Args:
        fpath: Path or string to the JSON file.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the JSON is invalid.
    """
    p = Path(fpath)
    if not p.exists():
        raise FileNotFoundError(f"JSON file not found: {p} (resolved: {p.resolve()})")

    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {p}: {e}") from e


def parse_raw_referential(raw_dict: dict) -> dict:
    """Example parser for the raw referential structure.

    This is a minimal implementation that demonstrates safe access
    to the structure; adapt to your actual JSON schema.
    """
    results = []
    for page in raw_dict:
        entries = page.get("result") if isinstance(page, dict) else None
        if not entries:
            continue
        for entry in entries:
            # placeholder: extract something useful
            results.append(entry)
    return {"count": len(results), "items": results}


if __name__ == "__main__":
    # Resolve the path relative to this file so the script can be
    # run from any current working directory.
    script_dir = Path(__file__).resolve().parent
    data_path = script_dir.parent.parent / "data" / "reference" / "raw_vitis_crop_ontology.json"
    print(f"Looking for referential file at: {data_path.resolve()}")
    try:
        res = read_referential_json(fpath=data_path)
    except Exception as e:
        print(f"Error reading referential JSON: {e}")
    else:
        parsed = parse_raw_referential(res)
        print(f"Parsed {parsed.get('count', 0)} entries")