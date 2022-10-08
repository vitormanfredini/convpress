from __future__ import annotations
import random
from typing import List

class ConvFilter:

    def __init__(self,size: int):
        self.kernel: bytes = List[bytes]
        self.kernel = []
        for i in range(size):
            self.kernel.append(b"")
        self.size = size
        
    def randomize_from_list(self,unique_bytelist: list, wildcard_chance: float, wildcard_byte):
        self.kernel = []
        used_wildcard_once = False
        for c in range(self.size):
            rand_idx = random.randrange(len(unique_bytelist))
            byte_to_use = unique_bytelist[rand_idx]
            if c > 0 and c < (self.size - 1) and used_wildcard_once == False:
                if random.uniform(0.0,1.0) < wildcard_chance:
                    byte_to_use = wildcard_byte
                    used_wildcard_once = True
            self.kernel.append(byte_to_use)
    
    def get_kernel(self):
        return self.kernel
    
    def get_size(self):
        return self.size
    
    def __eq__(self, other: ConvFilter):
        if self.get_size() != other.get_size():
            return False
        for c in range(self.get_size()):
            if self.kernel[c] != other.kernel[c]:
                return False
        return True
