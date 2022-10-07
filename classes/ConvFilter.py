import random

class ConvFilter:

    def __init__(self,size):
        self.filter = []
        self.size = size
        
    def randomizeFromList(self,uniquebytelist: list):
        self.filter = []
        for c in range(self.size):
            rand_idx = random.randrange(len(uniquebytelist))
            self.filter.append(uniquebytelist[rand_idx])
    
    def getFilter(self):
        return self.filter
    
    def getSize(self):
        return self.size
    
    def __eq__(self, other):
        if self.getSize() != other.getSize():
            return False
        for c in range(self.getSize()):
            if self.filter[c] != other.filter[c]:
                return False
        return True
