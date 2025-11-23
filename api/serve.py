from pydantic import BaseModel
from typing import Optional, List
import uuid

from fastapi import FastAPI, HTTPException, Depends

from memory_bank import Memory, MemoryBankManager, MemoryContent
from persona_bank import Persona, Personality, PersonaManager
from . import bodys

app = FastAPI(
    title = "MemorySystem",
    version="1.0.0"
)

memory_bank_manager = MemoryBankManager()
persona_bank_manager = PersonaManager()

@app.post("/memory_bank/add_memories", response_model=List[bodys.AddMemoryResponse])
def add_memories(memories: List[bodys.AddMemory]):
    try:
        _memories = []
        results = []
        for memory in memories:
            _memory = Memory(
                    memory.weight,
                    MemoryContent(
                        memory.conversations
                    ),
                    related_memories = memory.related_memories
                )
            _memories.append(
                _memory
            )
            results.append(bodys.AddMemoryResponse(uuid = _memory.memory_id))
        memory_bank_manager.add_memories(_memories)
        return results

    except Exception as e:
        return HTTPException(status_code=500, detail=f"添加记忆时发生错误：{str(e)}")
    
@app.post("/memory_bank/search_memories", response_model=bodys.SearchMemoryResponse)
def search_memories(resquest_body: bodys.SearchMemory):
    try:
        results = memory_bank_manager.search_memories(
                resquest_body.queries,
                top_k=resquest_body.top_k,
                top_p=resquest_body.top_p,
                search_deep=resquest_body.search_deep,
                association_deep=resquest_body.association_deep
        )
        return bodys.SearchMemoryResponse(results)
    except Exception as e:
        return HTTPException(500, f"搜索时发生错误：{e}")
    
@app.post("/memory_bank/update_memory_bank", response_model=bodys.UpdateMemoryBankResponse)
def update_memory_bank(resquest_body: bodys.UpdateMemoryBank):
    try:
        memory_bank_manager.update_memory_bank(resquest_body.decay_rate)
        return bodys.UpdateMemoryBankResponse()
    except Exception as e:
        return HTTPException(500, f"更新时发生错误：{e}")

@app.post("/persona_bank/get_persona", response_model=bodys.GetPersonaResponse)
def get_persona(request_body: bodys.GetPersona):
    try:
        result = persona_bank_manager.personas_data_dict.get(request_body.name, {"result":"没有结果"})
        return bodys.GetPersonaResponse(result=result)
    except Exception as e:
        return HTTPException(status_code=500, detail=f"获取人设时发生错误：{str(e)}")

@app.post("/persona_bank/update_persona", response_model=bodys.UpadatePersonaResponse)
def update_persona(request_body: bodys.UpadatePersonas):
    try:
        personas = None
        if type(request_body.personas) == list:
            personas = [Persona.from_dict(persona) for persona in request_body.personas ]
        else:
            personas = Persona.from_dict(request_body.personas)
        
        persona_bank_manager.update_personas(personas)
        persona_bank_manager.save_personas()
        return bodys.UpadatePersonaResponse()
    except Exception as e:
        return HTTPException(status_code=500, detail=f"更新人设时发生错误：{str(e)}")

@app.post("/persona_bank/generate_persona", response_model=bodys.GeneratePersonasResponse)
def update_persona(request_body: bodys.GeneratePersonas):
    try:
        persona_bank_manager.generate_persona(request_body.content)
        persona_bank_manager.save_personas()
        return bodys.UpadatePersonaResponse()
    except Exception as e:
        return HTTPException(status_code=500, detail=f"更新人设时发生错误：{str(e)}")
    
@app.post("/persona_bank/get_all_personas")
def update_persona():
    try:
        return persona_bank_manager.personas_data_dict
    except Exception as e:
        return HTTPException(status_code=500, detail=f"获取人设时发生错误：{str(e)}")
    

    
