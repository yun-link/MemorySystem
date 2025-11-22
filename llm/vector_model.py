import os
import torch
import torch.nn.functional as F
import struct
from volcenginesdkarkruntime import Ark
from typing import Optional, List
client = Ark(
    api_key="d9b1c355-199e-4f04-b38a-1ad4af162ff7",
)
def encode(inputs: List[str],):
    resp = client.embeddings.create(
        model="doubao-embedding-large-text-250515",
        input=inputs,
        encoding_format="float",
    )
    embedding = [d.embedding for d in resp.data]
    embedding = F.normalize(torch.tensor(embedding))
    return embedding