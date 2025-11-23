from typing import Dict, List, Literal
from pydantic import BaseModel

class AddMemory(BaseModel):
    weight: float
    conversations: List[Dict[Literal["role", "content", "timestamp"], str]]
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

class UpdateMemoryBank(BaseModel):
    decay_rate: float = 0.01

class UpdateMemoryBankResponse(BaseModel):
    pass

class GetPersona(BaseModel):
    name: str

class GetPersonaResponse(BaseModel):
    result: Dict 

class UpadatePersonas(BaseModel):
    personas: Dict | List[Dict]

class UpadatePersonaResponse(BaseModel):
    pass

class GeneratePersonas(BaseModel):
    content : str

class GeneratePersonasResponse(BaseModel):
    pass


