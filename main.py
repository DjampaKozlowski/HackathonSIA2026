from pathlib import Path
from typing import List
from src.processing.referential import load_referential


def main() -> None:
    """Run the referential load+convert flow using the package logic.

    This file is a convenient entrypoint so you can run the project with
        python main.py
    It will look for `data/reference/raw_vitis_crop_ontology.json` under the
    project root and call the conversion function from `src.processing.referential`.
    """
    try:
        # call loader without args; module will resolve default path
        refs: List = load_referential()
    except Exception as e:
        print(f"Error during load/convert: {e}")
        return

    print(f"Loaded and converted {len(refs)} ReferenceConcept entries")


if __name__ == "__main__":
    main()
