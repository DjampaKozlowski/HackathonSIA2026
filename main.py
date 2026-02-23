from pathlib import Path
from typing import List
from src.processing.referential import load_referential


def main() -> None:
    try:
        refs: List = load_referential()
    except Exception as e:
        print(f"Error during load/convert: {e}")
        return

    print(f"Loaded and converted {len(refs)} ReferenceConcept entries")


if __name__ == "__main__":
    main()
