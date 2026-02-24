from fastapi import FastAPI, HTTPException, UploadFile
from typing import List

from src.processing.referential import load_referential
from src.classes import NormalizedVariable

app = FastAPI(title="HackathonSIA2026 API")

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
		alignments = align_variable(variable, refs[1:5])
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"alignment error: {e}")

	return [a.model_dump() for a in alignments]



@app.post("/uploadfile")
async def create_upload_file(file: UploadFile):
    
    return {"filename": file.filename}