import random

from typing import List
from classes.ConvFilter import ConvFilter

class RanOutofPossibleBytes(Exception):
    pass

class Convpress:

    def __init__(self, filename):
        self.bytelist = []
        self.uniquebytelist = []
        self.adittionalbytelist = []
        self.filename = filename
        self.currentScores = []
        self.mutationPercentage = 0
        self.__loadFile(self.filename)
        self.generation_scores = []
    
    def getByteList(self) -> list:
        return self.bytelist

    def getUniqueByteList(self) -> list:
        return self.uniquebytelist

    def setMutationChance(self, chance):
        self.mutationPercentage = chance
    
    def __loadFile(self, filename):
        with open(filename, "rb") as file:
            byte = file.read(1)
            while byte:
                self.bytelist.append(byte)
                if byte not in self.uniquebytelist:
                    self.uniquebytelist.append(byte)
                byte = file.read(1)
    
    def __convolve(self, filter: ConvFilter):
        matches = []
        c = 0
        while c < len(self.bytelist):
            if c >= len(self.bytelist) - filter.getSize():
                break
            match = True
            for f in range(filter.getSize()):
                arrFilterBytes = filter.getFilter()
                if self.bytelist[c+f] != arrFilterBytes[f]:
                    match = False
                    break
            if match == True:
                matches.append(c)
                c += filter.getSize()
            else:
                c += 1
        return matches

    def convolveAll(self, filtersToConvolve: List[ConvFilter]):
        """Calculate score of each genration based on how much of the string it covered with all its filters"""
        unique_matches = []
        self.currentScores = []
        for filter in filtersToConvolve:
            matches = self.__convolve(filter)
            for index in matches:
                if index not in unique_matches:
                    unique_matches.append(index)
            score = len(matches) * filter.getSize()
            self.currentScores.append(score)
        self.addGenerationScore(len(unique_matches) / len(self.bytelist))
    
    def addGenerationScore(self, score: float):
        self.generation_scores.append(score)
    
    def getMaxScore(self):
        max = 0
        for score in self.currentScores:
            if score > max:
                max = score
        return max

    def getScores(self) -> list:
        return self.currentScores
    
    def get_generation_with_best_score(self):
        indexMax = 0
        maxScore = 0
        for idx, score in enumerate(self.generation_scores):
            if score > maxScore:
                maxScore = score
                indexMax = idx
        return indexMax

    def get_generation_scores(self):
        return self.generation_scores
    
    def debugScores(self):
        print(self.currentScores)

    def get_available_byte(self):
        for i in range(1114112):
            byte = chr(i)
            if byte not in self.uniquebytelist and byte not in self.adittionalbytelist:
                self.adittionalbytelist.append(byte)
                return byte
        raise RanOutofPossibleBytes("All possible bytes are in use. Can't proceed.")
    
    def compress(self, filters: List[ConvFilter], output: str) -> None:
        """process string replacing filter matches with new bytes representing the filter used in that particular place"""
        
        used_filters: List[ConvFilter] = []
        for filter in filters:
            matches = self.__convolve(filter)
            if len(matches) == 0:
                continue
            newbyte = self.get_available_byte()
            for pos in matches:
                self.bytelist[pos] = newbyte
            for idx, byte in enumerate(self.bytelist):
                if byte == newbyte:
                    for f in range(filter.getSize()):
                        if f == 0:
                            self.bytelist[idx+f] = self.bytelist[idx+f].encode('utf-8')
                            continue
                        self.bytelist.pop(idx+f)
            used_filters.append(filter)

        header = f"convpress{len(used_filters):04}"
        for filter in used_filters:
            filterString = b""
            for byte in filter.getFilter():
                filterString += byte
            header += filterString.decode('utf-8')
            
        with open(output, 'bw') as file:
            file.write(header.encode('utf-8'))
            for b in self.bytelist:
                file.write(bytes(b))
