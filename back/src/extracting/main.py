import json
import sys
import re
from pathlib import Path
from src.extracting.Extraction_excel import extract_traits
from src.extracting.lm_studio_client import query_lm_studio_with_text
import pymupdf
import pymupdf4llm


def extract_pdf_to_dict(pdf_source):
    """Extrait le PDF en dict {page_num: content}. Accepte chemin ou bytes."""
    if isinstance(pdf_source, (str, Path)):
        doc = pymupdf.open(str(pdf_source))
    else:
        doc = pymupdf.open(stream=pdf_source, filetype="pdf")

    pages = {}
    for page_num in range(len(doc)):
        page_md = pymupdf4llm.to_markdown(doc, pages=[page_num])
        pages[page_num + 1] = page_md

    doc.close()
    return pages


def build_prompt(traits, page_content, template):
    trait_list = "\n".join(f"- {t['trait_id']}: {t['description']}" for t in traits)
    return template.replace("{trait_list}", trait_list).replace("{page_content}", page_content)


def parse_json(raw):
    text = re.sub(r'^```(?:json)?\s*', '', raw.strip())
    text = re.sub(r'\s*```$', '', text).strip()

    if text.startswith('[') and not text.endswith(']'):
        last = text.rfind('}')
        if last > 0:
            text = text[:last + 1] + ']'

    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, list) else [parsed]
    except:
        return []


def merge(results, new_items):
    for item in new_items:
        tid = item.get("trait_id")
        if not tid or tid not in results:
            continue

        for field in ("trait", "method", "unit"):
            if results[tid].get(field) in (None, "", "null") and item.get(field) not in (None, "", "null"):
                results[tid][field] = item.get(field)


def run_pipeline(excel_source, pdf_source, output_path="outputs/result.json"):
    """
    Lance la pipeline complète d'extraction.

    Args:
        excel_source : str | Path | bytes
        pdf_source   : str | Path | bytes
        output_path  : str

    Returns:
        list[dict]
    """
    # 1. Charger traits
    traits = extract_traits(excel_source)
    print(f"Traits: {len(traits)}")

    # 2. Extraire PDF
    print(f"Extracting PDF...")
    pages = extract_pdf_to_dict(pdf_source)
    print(f"Pages: {len(pages)}\n")

    # 3. Charger prompt
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "v2" / "prompt_targeted_extraction.txt"
    with open(prompt_path, "r") as f:
        template = f.read()

    # 4. Initialiser résultats
    results = {t["trait_id"]: {**t, "trait": None, "method": None, "unit": None} for t in traits}

    # 5. Traiter chaque page
    for page_num, content in pages.items():
        print(f"Page {page_num}...", end=" ")
        try:
            prompt = build_prompt(traits, content, template)
            response = query_lm_studio_with_text(prompt)
            parsed = parse_json(response)
            merge(results, parsed)

            found = [item["trait_id"] for item in parsed]
            print(f"{found if found else 'nothing'}")
        except Exception as e:
            print(f"error: {e}")

    # 6. Sauvegarder
    final = list(results.values())
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    complete = sum(1 for r in final if r["trait"])
    print(f"\nDone: {complete}/{len(traits)} traits found")
    print(f"Saved: {output_path}")

    return final


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m src.extracting.main <excel_path> <pdf_path> [output_path]")
        sys.exit(1)

    output = sys.argv[3] if len(sys.argv) > 3 else "outputs/result.json"
    run_pipeline(sys.argv[1], sys.argv[2], output)
    