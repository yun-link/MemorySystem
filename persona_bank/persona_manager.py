import json
from pathlib import Path
from typing  import Dict, List

from .persona_config import PERSONAS_PATH, GENERATE_PERSONA_PROMPT, GENERATE_PERSONA_MODEL_NAME
from .persona import Persona, Personality
from llm import call_model

class PersonaManager:
    def __init__(
        self,
        personas_path: str|Path = PERSONAS_PATH,
    ):
        self.personas_path = personas_path
        self.personas_data_dict = self._load_personas_data_dict()
        self.personas_data = self._load_personas_data()
        
    
    def _load_personas_data_dict(self):
        with open(self.personas_path, 'r', encoding = 'utf-8') as f:
            data = json.load(f)
        return data
    def _load_personas_data(self):
        
        personas_data = {}
        for persona in self.personas_data_dict.values():
            personas_data[persona['name']] = Persona.from_dict(persona)
        return personas_data
    def generate_persona(self, content):
        messages = [
            {
                "role": "system",
                "content": GENERATE_PERSONA_PROMPT.format(
                    content = content,
                    personas = self.personas_data_dict
                )
            },
            {
                "role": "user",
                "content": f"对话内容：{content}, 现有画像库：{self.personas_data_dict} "
            }
        ]
        result = call_model(
            GENERATE_PERSONA_MODEL_NAME,
            messages
        )
        data = json.loads(result)

        personas = []

        for persona in data.values():
            persona = Persona.from_dict(persona)
            personas.append(persona)

        self.update_personas(personas)

    def update_personas(self, personas: List[Persona]|Persona):
        if type(personas) == Persona:
            personas = [personas]
        for persona in personas:
            self.personas_data[persona.name] = persona
            self.personas_data_dict[persona.name] = persona.to_dict()
    
    def save_personas(self):
        with open(self.personas_path, 'w', encoding = 'utf-8') as f:
            json.dump(self.personas_data_dict, f, ensure_ascii = False, indent = 2) 


