from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from src.extracting.main import extract_pdf_to_dict, parse_file
from src.processing.referential import load_referential
from src.classes import NormalizedVariable

app = FastAPI(title="HackathonSIA2026 API")

# Allow all CORS for now (adjust in production)
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get("/core")
def get_refs():
	try:
		refs = load_referential()
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
	items = [r.model_dump() for r in refs]
	return {"count": len(refs), "items": items}


@app.post("/align")
def align(variable: NormalizedVariable):
	"""Align a `NormalizedVariable` against the referential.

	This endpoint lazy-imports the alignment function to avoid heavy
	initialization at import time.
	"""
	try:
		refs = load_referential()
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"load_referential error: {e}")

	try:
		# lazy import to avoid initializing LM Studio on import
		from src.matching.matching_llm import align_variable
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"failed to import alignment function: {e}")

	try:
		# TODO: add refs that are in the top n.
		alignments = align_variable(variable, refs[1:5])
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"alignment error: {e}")

	return [a.model_dump() for a in alignments]



@app.post("/uploadfile")
async def create_upload_file(file: UploadFile):
    return {
		"variables":[
        {
            "trait_id": "VIGOUR",
            "description": "VIGOUR",
            "trait": None,
            "method": None,
            "unit": None
        },
        {
            "trait_id": "Shoot_Lenght",
            "description": "Shoot Lenght",
            "trait": None,
            "method": None,
            "unit": None
        },
        {
            "trait_id": "Leaf_Area",
            "description": "Leaf Area",
            "trait": None,
            "method": None,
            "unit": None
        },
        {
            "trait_id": "SPAD",
            "description": "SPAD",
            "trait": None,
            "method": None,
            "unit": None
        },
        {
            "trait_id": "Fresh_Aerial_Weight",
            "description": "Fresh Aerial Weight",
            "trait": None,
            "method": None,
            "unit": None
        },
        {
            "trait_id": "Fresh_Root_Weight",
            "description": "Fresh Root Weight",
            "trait": None,
            "method": None,
            "unit": None
        },
        {
            "trait_id": "Bud_Break",
            "description": "Bud Break",
            "trait": None,
            "method": None,
            "unit": None
        }
    ]
	}
	# if file.content_type == "application/pdf":
	# 	bytes = await file.read()
	# 	result = parse_file(bytes)
	# 	return {"variables": result}
	# return {"variables": []}