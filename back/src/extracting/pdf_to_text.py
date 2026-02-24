import sys
import json
import pymupdf
import pymupdf4llm


def extract_pdf_to_json(pdf_path):
    """Extrait le PDF en JSON : {page_num: content}."""
    doc = pymupdf.open(pdf_path)
    pages = {}
    
    for page_num in range(len(doc)):
        page_md = pymupdf4llm.to_markdown(doc, pages=[page_num])
        pages[page_num + 1] = page_md
    
    doc.close()
    return pages


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_text.py <pdf_path> [output.json]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "pdf_content.json"
    
    # Extraction
    pages = extract_pdf_to_json(pdf_path)
    
    # Sauvegarde
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)
    
    print(f"{len(pages)} pages → {output_path}")