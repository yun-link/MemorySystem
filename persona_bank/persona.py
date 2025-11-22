import json
from dataclasses import dataclass

from llm import call_model

@dataclass
class Personality:
    mbti: str
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    def to_dict(self):
        return {
            "mbti": self.mbti,
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            'neuroticism': self.neuroticism
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            mbti = data['mbti'],
            openness = data['openness'],
            conscientiousness = data['conscientiousness'],
            extraversion = data['extraversion'],
            agreeableness = data['agreeableness'],
            neuroticism = data['neuroticism'],
        )


@dataclass
class Persona:
    name: str
    gender: str
    age: str
    profile: str
    personality: Personality
    likeability: float
    def to_dict(self):
        return {
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "profile": self.profile,
            "personality": self.personality.to_dict(),
            "likeability": self.likeability
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name = data['name'],
            gender = data['gender'],
            age = data['age'],
            profile = data['profile'],
            personality = Personality.from_dict(data['personality']),
            likeability = data['likeability']
        )

