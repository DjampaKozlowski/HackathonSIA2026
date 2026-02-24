import os
import io
import json
import sys
import glob
import fitz
from PIL import Image
from src.lm_studio_client import query_lm_studio_with_image
from src.Extraction_excel import extract_traits
from src import config


def load_prompt(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(prompt_template, traits_still_needed):
    """Build prompt with only the traits still missing."""
    trait_list_str = "\n".join([
        f"- **{t['trait_id']}**: {t['description']}"
        for t in traits_still_needed
    ])
    return prompt_template.replace("{trait_ids_placeholder}", trait_list_str)


def convert_pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        pix = doc[i].get_pixmap(alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        yield i + 1, buf.getvalue()


def is_trait_complete(trait_result: dict) -> bool:
    """A trait is considered found if at least trait+method OR trait+unit is non-null."""
    has_trait = trait_result.get("trait") not in (None, "null", "")
    has_method = trait_result.get("method") not in (None, "null", "")
    has_unit = trait_result.get("unit") not in (None, "null", "")
    return has_trait and (has_method or has_unit)


def merge_results(consolidated: dict, page_results: list) -> dict:
    """
    Merge page results into consolidated dict.
    Only updates fields that are still None/null/empty.
    """
    for item in page_results:
        tid = item.get("trait_id")
        if tid not in consolidated:
            continue
        for field in ["trait", "method", "unit"]:
            current = consolidated[tid].get(field)
            new_val = item.get(field)
            # Only update if current is empty and new value is meaningful
            if current in (None, "null", "") and new_val not in (None, "null", ""):
                consolidated[tid][field] = new_val
    return consolidated


if __name__ == "__main__":
    # ── CONFIG ──────────────────────────────────────────────
    PROMPT_PATH = os.path.join(config.PROMPT_V2, "prompt_targeted_extraction.txt")
    OUTPUT_PATH = os.path.join("outputs", "result.json")
    # ────────────────────────────────────────────────────────

    os.makedirs("outputs", exist_ok=True)

    # ── ÉTAPE 1 : Excel → traits ──
    print("=" * 60)
    print("Étape 1 — Extraction des traits depuis l'Excel")
    print("=" * 60)

    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
    else:
        candidates = sorted(glob.glob(os.path.join(config.RAW_EXCEL_DIR, "*.xlsx")))
        if not candidates:
            raise FileNotFoundError(f"Aucun .xlsx trouvé dans {config.RAW_EXCEL_DIR}")
        excel_path = candidates[0]
    print(f"Fichier Excel : {excel_path}")
    traits = extract_traits(excel_path)
    trait_ids = [t["trait_id"] for t in traits]

    # ── INIT : résultat consolidé ──
    consolidated = {
        t["trait_id"]: {
            "trait_id": t["trait_id"],
            "description": t["description"],
            "trait": None,
            "method": None,
            "unit": None,
        }
        for t in traits
    }

    # ── ÉTAPE 2 : Prompt template ──
    print("\n" + "=" * 60)
    print("Étape 2 — Chargement du prompt template")
    print("=" * 60)
    prompt_template = load_prompt(PROMPT_PATH)
    print(f"Prompt chargé depuis : {PROMPT_PATH}")
    print(f"Traits à extraire : {trait_ids}")

    # ── ÉTAPE 3 : PDF → extraction avec arrêt anticipé ──
    print("\n" + "=" * 60)
    print("Étape 3 — Extraction depuis le PDF")
    print("=" * 60)

    if len(sys.argv) > 2:
        pdf_path = sys.argv[2]
    else:
        candidates = sorted(glob.glob(os.path.join(config.RAW_PDF_DIR, "*.pdf")))
        if not candidates:
            raise FileNotFoundError(f"Aucun .pdf trouvé dans {config.RAW_PDF_DIR}")
        pdf_path = candidates[0]
    print(f"Fichier PDF : {pdf_path}")

    pages_processed = 0

    for page_num, image_bytes in convert_pdf_to_images(pdf_path):

        # Check which traits are still incomplete
        traits_still_needed = [
            t for t in traits
            if not is_trait_complete(consolidated[t["trait_id"]])
        ]

        if not traits_still_needed:
            print(f"\nTous les traits trouvés après page {page_num - 1}. Arrêt anticipé.")
            break

        still_needed_ids = [t["trait_id"] for t in traits_still_needed]
        print(f"\nPage {page_num} — Traits encore manquants : {still_needed_ids}")

        # Build prompt with only missing traits
        prompt = build_prompt(prompt_template, traits_still_needed)

        try:
            result = query_lm_studio_with_image(image_bytes, prompt)
            print(f"Réponse brute :\n{result[:300]}...")

            parsed = json.loads(result)
            if isinstance(parsed, dict):
                parsed = [parsed]

            # Merge into consolidated result
            consolidated = merge_results(consolidated, parsed)

            # Show what was found on this page
            newly_complete = [
                tid for tid in still_needed_ids
                if is_trait_complete(consolidated[tid])
            ]
            if newly_complete:
                print(f"Traits complétés sur cette page : {newly_complete}")
            else:
                print(f"ℹAucun nouveau trait complété sur cette page.")

        except json.JSONDecodeError:
            print(f"JSON invalide page {page_num}, page ignorée.")
        except Exception as e:
            print(f"Erreur page {page_num} : {e}")

        pages_processed += 1

    # ── ÉTAPE 4 : Sauvegarde du résultat consolidé ──
    print("\n" + "=" * 60)
    print("Étape 4 — Sauvegarde du résultat consolidé")
    print("=" * 60)

    final_results = list(consolidated.values())

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)

    found_traits = {
        tid for tid, data in consolidated.items()
        if is_trait_complete(data)
    }
    missing_traits = set(trait_ids) - found_traits

    print(f"\nRésumé :")
    print(f"   Pages traitées     : {pages_processed}")
    print(f"   Traits recherchés  : {len(trait_ids)} → {trait_ids}")
    print(f"   Traits trouvés     : {len(found_traits)} → {found_traits}")
    print(f"   Traits manquants   : {len(missing_traits)} → {missing_traits}")
    print(f"   Résultat sauvegardé: {OUTPUT_PATH}")

    # Print final consolidated result
    print("\nRésultat final consolidé :")
    for trait_data in final_results:
        status = "Working !" if is_trait_complete(trait_data) else "Error"
        print(f"  {status} {trait_data['trait_id']}: "
              f"trait={trait_data['trait']}, "
              f"method={trait_data['method']}, "
              f"unit={trait_data['unit']}")