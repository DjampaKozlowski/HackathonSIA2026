from typing import List
import json
import time
from pydantic import ValidationError
from src.classes import AlignmentLLMResponse, AlignmentLLMResponseList, CandidateAlignment, NormalizedVariable, ReferenceConcept
import lmstudio as lms  # SDK LM Studio

SYSTEM_PROMT = """ArithmeticErrorYou are a strict data-alignment system.

TASK
- For a given normalized variable and reference concepts, evaluate the semantic and contextual match.
- Score is a float between 0 and 1 (0=no match, 1=perfect match)
- Composite score combining:
  - Semantic match (concept similarity)
  - Contextual match (unit, method, description)
- Output rules: 
  - Maximum 3 items, highest score first
  - Each object MUST contain:
    - ref_id (string)
    - score (float 0–1)
    - why_match (string explaining semantic & contextual reasoning)"""


def buildPrompt(variable: NormalizedVariable, references: List[ReferenceConcept]) -> str:
    variable_json = variable.model_dump_json(indent=2)
    references_json = json.dumps([r.model_dump() for r in references], indent=2)
    return f"""Here is the variable to categorize:

{variable_json}

Reference concepts:

{references_json}
"""


# Initialisation modèle LM Studio
model = lms.llm("openai/gpt-oss-20b")


def align_variable(
    variable: NormalizedVariable,
    references: List[ReferenceConcept],
    max_retries: int = 3,
) -> AlignmentLLMResponseList:

    prompt = SYSTEM_PROMT + "\n\n" + buildPrompt(variable, references)
    last_error = None

    for _ in range(max_retries):
        try:
            # Utilisation de LM Studio
            response = model.respond(prompt,response_format=AlignmentLLMResponseList)
            parsed = response.parsed
            return parsed

        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            last_error = e
            time.sleep(0.5)

    raise RuntimeError("Invalid JSON from LLM") from last_error


if __name__ == "__main__":
    variable = NormalizedVariable(
        dataset_id="ds_001",
        variable_id="var_001",
        trait_id="trait_001",
        trait="Tartaric acid concentration",
        aliases="ttr acd ac",
        name="tartaric acd cc",
        unit="g/ml",
        method="Beer acid",
        description="acidity of grape juice measured by Beer acid method",
    )

    with open("data/reference/refs_clean.json", "r", encoding="utf-8") as f:
        all_refs = json.load(f)
        # take indices 28..33 inclusive
        sliced_refs = all_refs[28:34]
        references = [ReferenceConcept(**r) for r in sliced_refs]
        

    alignments = align_variable(variable, references)
    print(alignments)