from typing import List
import os
from volcenginesdkarkruntime import Ark

client = Ark(
    api_key=os.getenv("VOLCE_API_KEY"),
)
def call_model(
    model_name,
    messages,
    on_thinking = True
) -> str:
    response = client.chat.completions.create(
        messages = messages,
        model = model_name,
        thinking = {"type":"enabled"} if on_thinking  else {"type":"disabled"}
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    print(call_model(
        'doubao-seed-1-6-flash-250828',
        [{'role':"user","content":"你好"}],
        False
    ))