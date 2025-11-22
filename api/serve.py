from pydantic import BaseModel
from typing import Optional, List
import uuid

from fastapi import FastAPI, HTTPException, Depends

from memory_bank import Memory, MemoryBankManager, MemoryContent
from persona_bank import Persona, Personality, PersonaManager
import bodys

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
            results.append(bodys.AddMemoryResponse(_memory.memory_id))
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
        return HTTPException(500, f"搜索时发送错误：{e}")
    

    
