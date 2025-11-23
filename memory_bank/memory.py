import datetime
import json
import os
import struct
import time
from typing import Dict, List
from uuid import uuid4
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import torch

from .memory_bank_config import MEMORY_BANK_PATH, SUMMARY_MODEL, SUMMARY_PROMPT
from llm import encode
from llm import call_model

class MemoryContent:
    def __init__(
        self,
        conversations: List[Dict],
        summary: str = None,
    ):
        self.conversations = conversations
        self.summary = summary if not summary  is None else self.generate_summary()

    def generate_summary(self):
        messages_body = self.format_messages()

        messages = [
            {"role" : "system", "content": SUMMARY_PROMPT},
            {"role" : "user","content" : messages_body}
        ]
        
        response = call_model(SUMMARY_MODEL, messages)

        return response

    def format_messages(self,  indentation_spaces: int = 0):
        messages_body=""
        for message in self.conversations:
            messages_body+=f"{" "*indentation_spaces}{message.get('timestamp')}-{message.get('role')}：{message.get('content')}\n"
        return messages_body
    
    def to_dict(self):
        return {
            "conversations" : self.conversations,
            "summary" : self.summary
        }
    
    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return  cls(
            data['conversations'],
            data['summary']
        )

    def __str__(self):
        messages_body = self.format_messages()
        return f"""- conversations: 
```text
{messages_body}
```
- summary: {self.summary}
"""
    def __repr__(self):
        return f"""MemoryContent(
        conversations={self.conversations}, 
        summary={self.summary}
    )"""
    


class Memory:
    def __init__( 
       self,
       weight: float,
       content: MemoryContent,
       vector_content: torch.Tensor = None,
       related_memories: List[str] = [], 
       memory_id: str = None
    ):  
       self.weight = weight
       self.content = content
       self.vector_content = self.memory_encode() if vector_content is None else vector_content
       self.related_memories = related_memories
       self.memory_id = str(uuid4()) if not memory_id else memory_id

    def memory_encode(self):
       return encode(str(self.content))
    
    def save_memory(self, filepath = None):

        MEMORY_BANK_PATH.mkdir(parents=True, exist_ok=True)

        filepath = os.path.join(MEMORY_BANK_PATH, f"{self.memory_id}.mem") if filepath is None else filepath
       
        with open(filepath, 'wb') as f:
            f.write(struct.pack('d', self.weight))
           
            content = json.dumps(self.content.to_dict(), ensure_ascii=False).encode('utf-8')
            f.write(struct.pack('I', len(content)))
            f.write(content)
           
            vector_bytes = self.vector_content.cpu().numpy().tobytes()
            vector_shape = self.vector_content.shape
            f.write(struct.pack('I', len(vector_shape)))
            for dim in vector_shape:
                f.write(struct.pack('I', dim))
            f.write(struct.pack('I', len(vector_bytes)))
            f.write(vector_bytes)
           
            f.write(struct.pack('I', len(self.related_memories)))
            for mem_id in self.related_memories:
                mem_id_bytes = mem_id.encode('utf-8')
                f.write(struct.pack('I', len(mem_id_bytes)))
                f.write(mem_id_bytes)
           
            memory_id_bytes = self.memory_id.encode('utf-8')
            f.write(struct.pack('I', len(memory_id_bytes)))
            f.write(memory_id_bytes)

    @staticmethod
    def load_memory(filepath: str):
       
        with open(filepath, 'rb') as f:
            weight = struct.unpack('d', f.read(8))[0]
        
            content_len = struct.unpack('I', f.read(4))[0]
            content = MemoryContent.from_json(f.read(content_len).decode('utf-8'))
           
            shape_len = struct.unpack('I', f.read(4))[0]
            shape = []
            for _ in range(shape_len):
                shape.append(struct.unpack('I', f.read(4))[0])
            vector_len = struct.unpack('I', f.read(4))[0]
            vector_bytes = f.read(vector_len)
            vector_content = torch.from_numpy(
                np.frombuffer(vector_bytes, dtype=np.float32).reshape(shape).copy()
            )
           
            related_count = struct.unpack('I', f.read(4))[0]
            related_memories = []
            for _ in range(related_count):
                mem_id_len = struct.unpack('I', f.read(4))[0]
                related_memories.append(f.read(mem_id_len).decode('utf-8'))
           
            memory_id_len = struct.unpack('I', f.read(4))[0]
            loaded_memory_id = f.read(memory_id_len).decode('utf-8')
       
        return Memory(
            weight=weight,
            content=content,
            vector_content=vector_content,
            related_memories=related_memories,
            memory_id=loaded_memory_id
        )
    
    def __str__(self):
        return f"""Memory(
    weight = {self.weight},
    content = {repr(self.content)},
    related_memories = {self.related_memories},
    vector_content = {self.vector_content},
    memory_id = {self.memory_id},
)"""
    
    def to_dict(self):
        return {
            "weight": self.weight,
            "content": self.content.to_dict(),
            "related_memories": self.related_memories,
            "memory_id": self.memory_id
        }

    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    memory=Memory(
        0.2,
        MemoryContent(
            [{"role":"云水", "content":"你好"}]
        )
    )
    print(memory)
    memory.save_memory()

    memory=Memory.load_memory(memory.memory_id)

