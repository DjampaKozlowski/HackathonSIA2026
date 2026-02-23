import pandas as pd
import json
import os

KNOWN_METADATA_COLS = {
    "Trial name", "Observation unit", "Plot code", "Plot label",
    "Replication number", "Treatment number", "Treatment label", "Round"
}

def extract_traits(excel_path, sheet_name="Plots notations"):
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
    # header=None : pandas ne traite AUCUNE ligne comme header
    # on gère manuellement les deux premières lignes

    # Ligne 0 = trait_ids techniques  (VIGOUR, Shoot_Lenght, ...)
    # Ligne 1 = descriptions lisibles (VIGOUR, Shoot Lenght, ...)
    # Ligne 2+ = données

    row_ids   = df.iloc[0].tolist()   # ex: [nan, nan, ..., 'VIGOUR', 'Shoot_Lenght', ...]
    row_desc  = df.iloc[1].tolist()   # ex: ['Trial name', ..., 'VIGOUR', 'Shoot Lenght', ...]

    traits = []
    for trait_id, description in zip(row_ids, row_desc):
        # Ignorer les colonnes metadata (détectées via la ligne de description)
        if str(description).strip() in KNOWN_METADATA_COLS:
            continue
        # Ignorer les colonnes vides / NaN
        if pd.isna(trait_id) or str(trait_id).strip() == "":
            continue

        traits.append({
            "trait_id": str(trait_id).strip(),
            "description": str(description).strip()
        })

    print(f"Fichier : {os.path.basename(excel_path)}")
    print(f"   Traits extraits ({len(traits)}) :")
    for t in traits:
        print(f"     - {t['trait_id']:30s} → {t['description']}")

    return traits



def save_traits_to_json(traits, output_path="data/extracted_traits.json"):
    """Sauvegarde la liste des traits en JSON pour le pipeline"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"traits": traits}, f, indent=2, ensure_ascii=False)
    print(f"\nTraits sauvegardés dans : {output_path}")


if __name__ == "__main__":
    import sys
    
    excel_path = sys.argv[1] if len(sys.argv) > 1 else "data/input_excel/SI24BT004IGS_Grapevine-20260223134943.xlsx"
    
    traits = extract_traits(excel_path)
    save_traits_to_json(traits)


