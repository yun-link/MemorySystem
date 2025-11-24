from datetime import datetime
from pathlib import Path
from typing import List
import sys
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import bisect
import torch
import torch.nn.functional as F
from difflib import SequenceMatcher

from .memory import Memory, MemoryContent
from .memory_bank_config import MEMORY_BANK_PATH
from llm import encode

class MemoryBankManager:
    def __init__(
        self,
        memory_bank_path: str = MEMORY_BANK_PATH,
        weight_intervals: List[float | int] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1,],
        spical_weight: int|float = -1
    ):
        self.memory_bank_path = memory_bank_path
        self.weight_intervals = [
            [weight_intervals[i], weight_intervals[i+1]]
            for i in range(len(weight_intervals)-1)
        ]
        self.spical_weight = spical_weight
        self.dir_paths = self._creat_memory_bank_dir()

        self.memorie_ids_index = self._load_all_memories_ids()

    def _find_interval(self, num):
        left_ends = [interval[0] for interval in self.weight_intervals]
        
        pos = bisect.bisect_right(left_ends, num) - 1
        
        if pos >= 0 and pos < len(self.weight_intervals) and self.weight_intervals[pos][0] <= num <= self.weight_intervals[pos][1]:
            return pos
        return None
    
    def _creat_memory_bank_dir(self):
        dir_paths = {}
        for path_name in self.weight_intervals:
            path = self.memory_bank_path / '~'.join([str(value) for value in path_name])
            path.mkdir(parents=True, exist_ok=True)
            dir_paths[str(path_name)] = path
        
        path = self.memory_bank_path / str(self.spical_weight)
        path.mkdir(exist_ok=True)
        dir_paths[str(self.spical_weight)] = path

        return dir_paths
    
    def _load_all_memories_ids(self):
        memorie_index={}
        
        for weight_interval in self.dir_paths:
            path = self.dir_paths[weight_interval]
            memorie_files = list(path.iterdir())

            memorie_index[weight_interval] = {}

            for memorie_file in memorie_files:
                memory_id = memorie_file.stem
                memorie_path = path / memorie_file

                memorie_index[weight_interval][memory_id] = memorie_path

        return memorie_index
    
    def from_ids_load_memory(self, memory_ids: List[str]) -> List[Memory]:
        memories = []
        lookup = {mid: path for w in self.memorie_ids_index for mid, path in self.memorie_ids_index[w].items()}
        for memory_id in memory_ids:
            if memory_id not in lookup:
                raise ValueError(f"记忆不存在：{memory_id}")
            memories.append(Memory.load_memory(lookup[memory_id]))
        return memories
    def add_memories(self,memories: List[Memory]):
        for memory in memories:
            if memory.weight == self.spical_weight:
                path = self.dir_paths[str(self.spical_weight)]
                self.memorie_ids_index[self.spical_weight][memory.memory_id] = path / f"{memory.memory_id}.mem"
            else:    
                index = self._find_interval(memory.weight)
                if index is None:
                    raise ValueError(f"记忆权重值超出范围：{memory.weight}")
                path = self.dir_paths[str(self.weight_intervals[index])]
                self.memorie_ids_index[str(self.weight_intervals[index])][memory.memory_id] = path / f"{memory.memory_id}.mem"
            memory.save_memory(path / f"{memory.memory_id}.mem")
            
    def get_related_memories(
        self,
        memories: List[Memory],
        deep: int = 3
    ) -> List[Memory]:
        if deep <= 0:  
            return []
        related_memories = []

        for memory in memories:
            _related_memories = memory.related_memories
            related_memories.append(self.from_ids_load_memory(_related_memories))
            related_memories.append(self.get_related_memories(_related_memories, deep-1))

        return related_memories
    def _delete_memories(self, memories: List[Memory]):
        for memory in memories:
            for interval in self.memorie_ids_index:
                if memory.memory_id in self.memorie_ids_index[interval]:
                    path = self.memorie_ids_index[interval][memory.memory_id]
                    if path.exists():
                        path.unlink()
                    del self.memorie_ids_index[interval][memory.memory_id]
                    break

    def set_memory_weights(self, targets: List[tuple]):
        memories_to_delete = [target[0] for target in targets]
        self._delete_memories(memories_to_delete)
        updated_memories = []
        for memory, new_weight in targets:
            memory.weight = new_weight
            updated_memories.append(memory)
        self.add_memories(updated_memories)

    def search_memories(
        self,
        queries: List[str],
        top_k: int = 5,
        top_p: float = 0.5,
        search_deep: int = 10,
        association_deep: int = 2,
    ):
        result = {}
        for query in queries:
            query_vector = encode([query])
            results = []
            for i, weight in enumerate(sorted(self.memorie_ids_index, reverse=True, 
                    key=lambda x: (float('inf') if x == -1 else x))):
                memory_ids = list(self.memorie_ids_index[weight])
                memories = self.from_ids_load_memory(memory_ids)
                
                for memory in memories:
                    memory_content = str(memory.content)
                    related_memories = self.get_related_memories([memory], association_deep)
                    semantic_similarity = F.cosine_similarity(query_vector, memory.vector_content).item()
                    
                    query_lower = query.lower()
                    content_lower = memory_content.lower()
                    char_match_score = content_lower.count(query_lower) * 0.1
                  
                    combined_score = (semantic_similarity + char_match_score) 
                    
                    if combined_score >= top_p:
                        self.set_memory_weights([(memory, memory.weight + 0.03)])
                        results.append(
                            {
                                "memory": memory, 
                                "source": combined_score,
                                "related_memories": related_memories if any(related_memories) else None
                            }
                        )
                
                if i >= search_deep:
                        break
            results = sorted(results, reverse = True, key = lambda x: x["source"])
            if results:
                result[query] = results[:top_k]
        return result


    def update_memory_bank(self, decay_rate: float = 0.01):
        update_targets = []
        delete_targets = []
        for interval in self.memorie_ids_index:
            if interval == str(self.spical_weight):
                continue
            memory_ids = list(self.memorie_ids_index[interval].keys())
            memories = self.from_ids_load_memory(memory_ids)
            for memory in memories:
                new_weight = memory.weight * (1 - decay_rate)
                if new_weight >= 0.1:
                    update_targets.append((memory, new_weight))
                else:
                    delete_targets.append(memory)
        if update_targets:
            self.set_memory_weights(update_targets)
        if delete_targets:
            self._delete_memories(delete_targets)


if __name__ == "__main__":
    memory_manager = MemoryBankManager()

    memory1 = Memory(
        memory_id="mem_001",
        content=MemoryContent(text="Python是一种编程语言", timestamp=datetime.now()),
        weight=0.7
    )

    memory2 = Memory(
        memory_id="mem_002",
        content=MemoryContent(conversations=['机器学习需要计算机基础'], timestamp=datetime.now()),
        weight=0.9
    )

    memory_manager.add_memories([memory1, memory2])

    queries = ["编程语言", "数学"]
    search_results = memory_manager.search_memories(queries, top_k=3)

    for query, results in search_results.items():
        print(f"查询: {query}")
        for result in results:
            memory = result["memory"]
    print(f"记忆ID: {memory.memory_id}, 内容: {memory.content.text}, 得分: {result['source']:.4f}")

