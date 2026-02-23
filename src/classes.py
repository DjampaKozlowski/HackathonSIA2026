from pydantic import BaseModel, Field


class ResultLLM(BaseModel):
    score: float = Field(..., description="Score")
    core_id: str = Field(..., description="Variable core id")
    dataset_id: str = Field(..., description="Dataset ID")
    trait_id: str = Field(..., description="Trait ID")
    
    
class NormalizedVariable(BaseModel):
    dataset_id: str = Field(..., description="ID du dataset")
    trait_id: str = Field(..., description="ID du trait")
    trait: str = Field(..., description="Nom du trait")
    methode: str = Field(..., description="Méthode utilisée")
    unite: str = Field(..., description="Unité de mesure")
    description: str = Field(..., description="Description")
    alias: str = Field(..., description="Alias")


class CoreVariable(BaseModel):
    core_id: str = Field(..., description="Core variable id")
    unit: list[str] = Field(..., description="Unit(s) of measurement")
    description: str = Field(..., description="Description")
    alias: list[str] = Field(default_factory=list, description="Alias list")
    methods: list[str] = Field(default_factory=list, description="Methods")
