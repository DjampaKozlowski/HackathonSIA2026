import os

ROOT = os.path.dirname(os.path.dirname(__file__))

DATA_DIR = os.path.join(ROOT, "data")
RAW_EXCEL_DIR = os.path.join(DATA_DIR, "raw", "excel")
RAW_PDF_DIR = os.path.join(DATA_DIR, "raw", "pdf")
FORMATTED_EXCEL_DIR = os.path.join(DATA_DIR, "formatted", "excel")
PROCESSED_TRAITS_DIR = os.path.join(DATA_DIR, "processed", "traits")

PROMPTS_DIR = os.path.join(ROOT, "prompts")
PROMPT_V1 = os.path.join(PROMPTS_DIR, "v1")
PROMPT_V2 = os.path.join(PROMPTS_DIR, "v2")

EXTRACTED_TRAITS_JSON = os.path.join(PROCESSED_TRAITS_DIR, "extracted_traits.json")