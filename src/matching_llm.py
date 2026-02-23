from typing import List
import json
import time
from openai import OpenAI
from pydantic import ValidationError
from classes import (
    CandidateAlignment,
    NormalizedVariable,
    ReferenceConcept,
)

SYSTEM_PROMT = """ArithmeticErrorYou are a strict data-alignment system.

TASK
- For a given normalized variable and reference concepts, evaluate the semantic and contextual match.
- Score is a float between 0 and 1 (0=no match, 1=perfect match)
- Composite score combining:
  - Semantic match (concept similarity)
  - Contextual match (unit, method, description)
- Output rules:
  - ONLY valid JSON
  - JSON array only
  - Maximum 3 items, highest score first
  - Each object MUST contain:
    - ref_id (string)
    - score (float 0–1)
    - why_match (string explaining semantic & contextual reasoning)
- Do NOT add markdown, text, or explanation outside JSON"""


def buildPrompt(variable: NormalizedVariable, references: List[ReferenceConcept]) -> str:
    variable_json = variable.model_dump_json(indent=2)
    references_json = json.dumps([r.model_dump() for r in references], indent=2)

    return f"""Here is the variable to categorize:

{variable_json}

Reference concepts:

{references_json}
"""




client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
)


def align_variable(
    variable: NormalizedVariable,
    references: List[ReferenceConcept],
    model: str = "google/gemma-3-12b",
    max_retries: int = 3,
) -> List[CandidateAlignment]:

    prompt = buildPrompt(variable, references)
    last_error = None

    for _ in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMT},
                    {"role": "user", "content": prompt},
                ],
            )

            raw = response.choices[0].message.content.strip()
            parsed = json.loads(raw)

            return [CandidateAlignment(**item) for item in parsed]

        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            last_error = e
            time.sleep(0.5)

    raise RuntimeError("Invalid JSON from LLM") from last_error