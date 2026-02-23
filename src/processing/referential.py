import json
from pathlib import Path
from typing import Any, Dict, List
from pydantic import ValidationError

from src.classes import ReferenceConcept


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

def convert_entries_to_reference_concepts(entries: List[dict]) -> List[ReferenceConcept]:
    """Convert raw referential entries into `ReferenceConcept` instances.

    Mapping:
      - ref_id: 'ref_<index>'
      - name: item['name']
      - units: [ item['unit']['name'] ] if present
      - methods: [ item['method']['name'] ] if present
      - description: item['alternative_name']
      - aliases: []
    """
    dct = {}
    for entry in entries:
        characteristic = entry.get("characteristic")
        if isinstance(characteristic, dict):
            name = characteristic.get("name")

        unit = entry.get('unit').get('name')
        method = entry.get('method').get('name')
        description = entry.get("alternative_name")
        short_name = entry.get("name")
        if name not in dct:
            dct[name] = {
                'name': name,
                'units': [unit],
                'methods':[method],
                'description': description,
                'aliases': [short_name]
            }
        else:
            item = dct[name]
            if unit not in item['units']:
                item['units'].append(unit)
            if method not in item['methods']:
                item['methods'].append(method)
            if description not in item['description']:
                item['description'] += '|'+description
            if short_name not in item['aliases']:
                item['aliases'].append(short_name)
        
    results = []
    for i, item in enumerate(dct.values(), start=1):
        item['ref_id'] = f"ref_{i}"
        try:
            rc = ReferenceConcept(**item)
            results.append(rc)
        except ValidationError:
            # Skip invalid items but continue processing
            continue
    return results





# def convert_entries_to_reference_concepts(entries: List[dict]) -> List[ReferenceConcept]:
#     """Convert raw referential entries into `ReferenceConcept` instances.

#     Mapping:
#       - ref_id: 'ref_<index>'
#       - name: item['name']
#       - units: [ item['unit']['name'] ] if present
#       - methods: [ item['method']['name'] ] if present
#       - description: item['alternative_name']
#       - aliases: []
#     """
#     concepts: List[ReferenceConcept] = []
#     for idx, item in enumerate(entries, start=1):
#         ref_id = f"ref_{idx}"
#         # name = item.get("name") or ""

#         # Name should be the plain english name, not, the shortname
#         characteristic = item.get("characteristic")
#         if isinstance(characteristic, dict):
#             name = characteristic.get("name")


#         units: List[str] = []
#         unit = item.get("unit")
#         if isinstance(unit, dict):
#             u = unit.get("name")
#             if u:
#                 units.append(u)

#         methods: List[str] = []
#         method = item.get("method")
#         if isinstance(method, dict):
#             m = method.get("name")
#             if m:
#                 methods.append(m)

#         description = item.get("alternative_name") or item.get("description") or ""
#         aliases: List[str] = []

#         try:
#             rc = ReferenceConcept(
#                 ref_id=ref_id,
#                 name=name,
#                 units=units,
#                 methods=methods,
#                 description=description,
#                 aliases=aliases,
#             )
#             concepts.append(rc)
#         except ValidationError:
#             # Skip invalid items but continue processing
#             continue

#     return concepts


def load_and_convert_referential(fpath: str | Path) -> List[ReferenceConcept]:
    """Convenience function: read a referential JSON file, parse it and convert to ReferenceConcepts.

    Returns the list of successfully converted `ReferenceConcept` instances.
    """
    raw = read_referential_json(fpath=fpath)
    parsed = parse_raw_referential(raw)
    items = parsed.get("items", [])
    return convert_entries_to_reference_concepts(items)


def load_referential() -> List[ReferenceConcept]:
    module_dir = Path(__file__).resolve().parent
    fpath = module_dir.parent.parent / "data" / "reference" / "raw_vitis_crop_ontology.json"
    return load_and_convert_referential(fpath)

