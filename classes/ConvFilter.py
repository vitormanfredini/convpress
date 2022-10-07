import random

class ConvFilter:

    def __init__(self,size):
        self.kernel = []
        self.size = size
        
    def randomize_from_list(self,uniquebytelist: list):
        self.kernel = []
        for c in range(self.size):
            rand_idx = random.randrange(len(uniquebytelist))
            self.kernel.append(uniquebytelist[rand_idx])
    
    def get_kernel(self):
        return self.kernel
    
    def get_size(self):
        return self.size
    
    def __eq__(self, other):
        if self.get_size() != other.get_size():
            return False
        for c in range(self.get_size()):
            if self.kernel[c] != other.kernel[c]:
                return False
        return True
