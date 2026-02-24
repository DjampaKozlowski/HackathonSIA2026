import os, io, json, sys, glob, re, fitz
from PIL import Image
from src.lm_studio_client import query_lm_studio_with_image
from src.Extraction_excel import extract_traits
from src import config


def pdf_to_images(pdf_path):
    """Convertit chaque page PDF en bytes PNG."""
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        pix = doc[i].get_pixmap(alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        yield i + 1, buf.getvalue()


def clean_json_response(raw: str) -> str:
    """Nettoie la réponse LLM : retire markdown, ferme les brackets tronqués."""
    text = raw.strip()
    # Retirer les blocs markdown
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()
    # Tenter de fermer un JSON tronqué
    if text.startswith('[') and not text.endswith(']'):
        # Couper au dernier objet complet
        last_brace = text.rfind('}')
        if last_brace > 0:
            text = text[:last_brace + 1] + ']'
    return text


def build_prompt(template: str, traits: list) -> str:
    """Injecte les traits manquants dans le template."""
    listing = "\n".join(f"- {t['trait_id']}: {t['description']}" for t in traits)
    return template.replace("{trait_ids_placeholder}", listing)


def is_complete(t: dict) -> bool:
    """Un trait est complet si trait + (method OU unit) sont renseignés."""
    ok = lambda v: v not in (None, "null", "")
    return ok(t.get("trait")) and (ok(t.get("method")) or ok(t.get("unit")))


def merge(consolidated: dict, page_results: list) -> dict:
    """Fusionne les résultats d'une page dans le dictionnaire consolidé."""
    for item in page_results:
        tid = item.get("trait_id")
        if tid not in consolidated:
            continue
        for f in ("trait", "method", "unit"):
            if consolidated[tid].get(f) in (None, "null", "") \
               and item.get(f) not in (None, "null", ""):
                consolidated[tid][f] = item[f]
    return consolidated


if __name__ == "__main__":
    PROMPT_PATH = os.path.join(config.PROMPT_V2, "prompt_targeted_extraction.txt")
    OUTPUT_PATH = os.path.join("outputs", "result.json")
    os.makedirs("outputs", exist_ok=True)

    # ── 1. Excel → traits ──
    excel = sys.argv[1] if len(sys.argv) > 1 else sorted(
        glob.glob(os.path.join(config.RAW_EXCEL_DIR, "*.xlsx")))[0]
    print(f"Excel : {excel}")
    traits = extract_traits(excel)

    consolidated = {
        t["trait_id"]: {**t, "trait": None, "method": None, "unit": None}
        for t in traits
    }

    # ── 2. Prompt ──
    with open(PROMPT_PATH, "r") as f:
        template = f.read()
    print(f"📝 Prompt : {PROMPT_PATH}")

    # ── 3. PDF → extraction page par page ──
    pdf = sys.argv[2] if len(sys.argv) > 2 else sorted(
        glob.glob(os.path.join(config.RAW_PDF_DIR, "*.pdf")))[0]
    print(f"📄 PDF : {pdf}")

    for page_num, img_bytes in pdf_to_images(pdf):
        needed = [t for t in traits if not is_complete(consolidated[t["trait_id"]])]
        if not needed:
            print(f"\nTous les traits trouvés ! Arrêt page {page_num - 1}.")
            break

        print(f"\n── Page {page_num} | Manquants : {[t['trait_id'] for t in needed]}")

        try:
            raw = query_lm_studio_with_image(img_bytes, build_prompt(template, needed))
            cleaned = clean_json_response(raw)
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                parsed = [parsed]

            consolidated = merge(consolidated, parsed)

            found = [t["trait_id"] for t in needed if is_complete(consolidated[t["trait_id"]])]
            if found:
                print(f"Complétés : {found}")

        except json.JSONDecodeError:
            print(f"JSON invalide, page ignorée")
            print(f"   Aperçu : {raw[:200]}")
        except Exception as e:
            print(f"Erreur : {e}")

    # ── 4. Sauvegarde ──
    results = list(consolidated.values())
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    found = {tid for tid, d in consolidated.items() if is_complete(d)}
    missing = set(t["trait_id"] for t in traits) - found
    print(f"\n{'='*60}")
    print(f"Trouvés : {len(found)}/{len(traits)} → {found}")
    print(f"Manquants : {missing}")
    print(f"Sauvegardé : {OUTPUT_PATH}")