from pathlib import Path
from typing import List
from src.processing.referential import load_referential
import json

# def main() -> None:
#     refs: List = load_referential()

def main() -> None:
    try:
        refs: List = load_referential()
        refs_json = [ref.model_dump() for ref in refs]
        with open("data/reference/refs.json", "w", encoding="utf-8") as f:
            json.dump(refs_json, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error during load/convert: {e}")
        return

    print(f"Loaded and converted {len(refs)} ReferenceConcept entries")


if __name__ == "__main__":
    main()
