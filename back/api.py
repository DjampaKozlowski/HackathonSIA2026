from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from src.extracting.main import extract_pdf_to_dict, parse_file
from src.processing.referential import load_referential
from src.classes import NormalizedVariable
from src.embedding import SemanticEmbedding

# Load Referentials
refs = load_referential()
# Init the semantic embedding class and init the referential embedding
semantic_embedding = SemanticEmbedding(referential_json=refs, model_name="nomic-embed-text-v1.5")


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
	items = [r.model_dump() for r in refs]
	return {"count": len(refs), "items": items}


@app.post("/align")
def align(variable: NormalizedVariable):
	"""Align a `NormalizedVariable` against the referential.

	This endpoint lazy-imports the alignment function to avoid heavy
	initialization at import time.
	"""
	try:
		# lazy import to avoid initializing LM Studio on import
		from src.matching.matching_llm import align_variable
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"failed to import alignment function: {e}")

	try:
		# TODO: add refs that are in the top n.
		best_matches, idx = semantic_embedding.get_best_matches(variable, top_k=5) # best_matches not usefull so far (scores)
		best_refs = [refs[i] for i in idx]
		alignments = align_variable(variable, best_refs)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"alignment error: {e}")

	return alignments



@app.post("/uploadfile")
async def create_upload_file(file: UploadFile):
    return {
		"variables": [
			{
			"trait_id": "VIGOUR",
			"description": "Overall plant vigor assessed as a composite indicator of vegetative growth and plant health (e.g., canopy development, leafiness, stem robustness, color/greenness, and general uniformity). Typically used to compare treatments or genotypes at a given date or growth stage.",
			"trait": "VIGOUR",
			"method": "Visual vigor rating (field scoring on a predefined scale, e.g., 1–9)",
			"unit": "score (1–9)"
			},
			{
			"trait_id": "Shoot_Lenght",
			"description": "Length of the main shoot (or the dominant shoot) measured from the shoot base (insertion point) to the apical tip. Used as an indicator of vegetative growth rate and treatment/genotype effects on elongation.",
			"trait": "Shoot Lenght",
			"method": "Manual measurement with ruler/tape on the main shoot (base-to-tip)",
			"unit": "cm"
			},
			{
			"trait_id": "Leaf_Area",
			"description": "Total leaf area per plant (or per sampled shoot), reflecting the photosynthetically active surface. Often derived from direct leaf area measurement or image-based estimation, and used to assess canopy development and potential light interception.",
			"trait": "Leaf Area",
			"method": "Leaf area meter measurement (planimeter) on sampled leaves (sum per plant)",
			"unit": "cm2"
			},
			{
			"trait_id": "SPAD",
			"description": "Relative leaf chlorophyll content index measured non-destructively on leaves. Frequently used as a proxy for leaf nitrogen status and photosynthetic capacity, and to monitor nutritional or stress effects over time.",
			"trait": "SPAD",
			"method": "SPAD meter reading (e.g., Minolta/Konica SPAD) on the mid-section of fully expanded leaves",
			"unit": "SPAD units"
			},
			{
			"trait_id": "Fresh_Aerial_Weight",
			"description": "Fresh biomass of above-ground plant parts (shoots/stems/leaves; optionally excluding fruits depending on protocol) measured immediately after harvest to avoid dehydration. Indicator of vegetative biomass accumulation.",
			"trait": "Fresh Aerial Weight",
			"method": "Destructive sampling: harvest above-ground biomass and weigh immediately on a calibrated balance",
			"unit": "g/plant"
			},
			{
			"trait_id": "Fresh_Root_Weight",
			"description": "Fresh biomass of the root system measured after uprooting and cleaning (removal of adhering soil) and weighing promptly. Indicator of below-ground biomass allocation and root development.",
			"trait": "Fresh Root Weight",
			"method": "Destructive sampling: uproot plant, wash roots, blot dry, then weigh on a calibrated balance",
			"unit": "g/plant"
			},
			{
			"trait_id": "Bud_Break",
			"description": "Bud break progression quantified as the proportion of buds that have opened (visible green tissue) on a plant/shoot at a given observation date. Common phenological indicator to compare earliness and treatment/genotype effects.",
			"trait": "Bud Break",
			"method": "Field phenology scoring by counting opened buds vs total buds on tagged shoots/plants",
			"unit": "%"
			}
		]
		}
	# if file.content_type == "application/pdf":
	# 	bytes = await file.read()
	# 	result = parse_file(bytes)
	# 	return {"variables": result}
	# return {"variables": []}