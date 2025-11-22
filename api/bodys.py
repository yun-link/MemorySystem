from typing import Dict, List
from pydantic import BaseModel

class AddMemory(BaseModel):
    weight: float
    conversations: List
    related_memories: List

class AddMemoryResponse(BaseModel):
    uuid: str

class SearchMemory(BaseModel):
    queries: List[str]
    top_k: int = 5
    top_p: float = 0.5
    search_deep: int = 10
    association_deep: int = 2

class SearchMemoryResponse(BaseModel):
    results: Dict

class GetPersona(BaseModel):
    name: str

class GetPersonaResponse(BaseModel):
    result: Dict

class UpadatePersona(BaseModel):
    persona: Dict

class UpadatePersonaResponse(BaseModel):
    pass

