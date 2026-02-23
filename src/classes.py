from typing import List

from pydantic import BaseModel, Field


    
class CandidateAlignment(BaseModel):
    score: float = Field(...,
                         ge=0.0,
                         le=1.0,
                         description="Score normalisé entre 0 et 1"
                         )
    ref_id: str = Field(..., description="Variable core id")
    dataset_id: str = Field(..., description="Dataset ID")
    trait_id: str = Field(..., description="Trait ID")
    
class AlignmentLLMResponse(BaseModel):
    score: float = Field(...,
                         ge=0.0,
                         le=1.0,
                         description="Score normalisé entre 0 et 1"
                         )
    ref_id: str = Field(..., description="Variable core id")
    why_description: str = Field(..., description="Description of why the alignment was made")
class AlignmentLLMResponseList(BaseModel):
    items: List[AlignmentLLMResponse]
class NormalizedVariable(BaseModel):
    dataset_id: str = Field(..., description="ID du dataset")
    trait_id: str = Field(..., description="ID du trait")
    trait: str = Field(..., description="Nom du trait")
    method: str = Field(..., description="Méthode utilisée")
    unit: str = Field(..., description="Unité de mesure")
    description: str = Field(..., description="Description")
    aliases: str = Field(..., description="Alias")


class ReferenceConcept(BaseModel):
    ref_id: str = Field(..., description="Core variable id")
    name: str = Field(..., description="Core variable name in plain english")
    units: list[str] = Field(..., description="Unit(s) of measurement")
    methods: list[str] = Field(default_factory=list, description="Methods")
    description: str = Field(..., description="Description")
    aliases: list[str] = Field(default_factory=list, description="Alias list")