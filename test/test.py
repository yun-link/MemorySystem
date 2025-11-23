import requests
import json

BASE_URL = "http://localhost:8000"

def test_add_memories():
    memory_data = [
        {
            "weight": 0.8,
            "conversations": [
                {"role": "user", "content": "Hello", "timestamp": "2023-01-01"},
                {"role": "assistant", "content": "Hi there!", "timestamp": "2023-01-01"}
            ],
            "related_memories": []
        }
    ]
    response = requests.post(f"{BASE_URL}/memory_bank/add_memories", json=memory_data)
    print(f"Add Memories: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")

def test_search_memories():
    search_data = {
        "queries": ["hello", "greeting"],
        "top_k": 5,
        "top_p": 0.5,
        "search_deep": 10,
        "association_deep": 2
    }
    response = requests.post(f"{BASE_URL}/memory_bank/search_memories", json=search_data)
    print(f"Search Memories: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")

def test_update_memory_bank():
    update_data = {
        "decay_rate": 0.01
    }
    response = requests.post(f"{BASE_URL}/memory_bank/update_memory_bank", json=update_data)
    print(f"Update Memory Bank: {response.status_code}")

def test_get_persona():
    persona_data = {
        "name": "test_persona"
    }
    response = requests.post(f"{BASE_URL}/persona_bank/get_persona", json=persona_data)
    print(f"Get Persona: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")

def test_update_persona():
    persona_data = {
        "name": "test_persona",
        "gender": "unkonwn",
        "age": "unkonwn",
        "profile": "unkonwn",
        "personality": {
                "mbti": "unkonwn",
                "openness": "unkonwn",
                "conscientiousness": "unkonwn",
                "extraversion": "unkonwn",
                "agreeableness": "unkonwn",
                'neuroticism': "unkonwn"
            },
        "likeability": "unkonwn"
    }
    response = requests.post(f"{BASE_URL}/persona_bank/update_persona", json=persona_data)
    print(f"Update Persona: {response.status_code}")

def test_generate_persona():
    generate_data = {
        "content": "Create a friendly assistant persona"
    }
    response = requests.post(f"{BASE_URL}/persona_bank/generate_persona", json=generate_data)
    print(f"Generate Persona: {response.status_code}")

def test_get_all_personas():
    response = requests.post(f"{BASE_URL}/persona_bank/get_all_personas")
    print(f"Get All Personas: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_add_memories()
    test_search_memories()
    test_update_memory_bank()
    test_get_persona()
    test_update_persona()
    test_generate_persona()
    test_get_all_personas()
