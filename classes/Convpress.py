import random

from typing import List
from classes.ConvFilter import ConvFilter

class RanOutofPossibleBytes(Exception):
    pass

class Convpress:

    def __init__(self):
        self.bytelist = []
        self.uniquebytelist = []
        self.adittionalbytelist = []
        self.inputFile = None
        self.current_filter_scores = []
        self.mutationPercentage = 0
    
    def getByteList(self) -> list:
        return self.bytelist

    def getUniqueByteList(self) -> list:
        return self.uniquebytelist

    def setMutationChance(self, chance):
        self.mutationPercentage = chance
    
    def loadFile(self, filename):
        self.inputFile = filename
        self.bytelist = []
        self.uniquebytelist = []
        with open(self.inputFile, "rb") as file:
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
            if c >= len(self.bytelist) - filter.get_size():
                break
            match = True
            for f in range(filter.get_size()):
                kernel = filter.get_kernel()
                if self.bytelist[c+f] != kernel[f]:
                    match = False
                    break
            if match == True:
                matches.append(c)
                c += filter.get_size()
            else:
                c += 1
        return matches

    def convolve_all_and_get_generation_score(self, filtersToConvolve: List[ConvFilter]):
        """Calculate score of each generation based on how much of the string it covered with all its filters"""
        unique_matches = []
        self.current_filter_scores = []
        for filter in filtersToConvolve:
            matches = self.__convolve(filter)
            for match_index in matches:
                if match_index not in unique_matches:
                    unique_matches.append(match_index)
            filter_score = len(matches) * filter.get_size()
            self.current_filter_scores.append(filter_score)
        return len(unique_matches) / len(self.bytelist)
    
    def getMaxScore(self):
        max = 0
        for score in self.current_filter_scores:
            if score > max:
                max = score
        return max

    def get_current_filters_scores(self) -> list:
        return self.current_filter_scores
    
    def debugScores(self):
        print(self.current_filter_scores)

    def get_available_byte(self):
        for i in range(1114112):
            byte = chr(i)
            if byte not in self.uniquebytelist and byte not in self.adittionalbytelist:
                self.adittionalbytelist.append(byte)
                return byte
        raise RanOutofPossibleBytes("All possible bytes are in use. Can't proceed.")
    
    def get_min_matches_necessary(self):
        """number of filter matches necessary to reduce the string more than it adds to the header"""
        return 5
    
    @staticmethod
    def generate_header(filters: list, bytes:list):
        """
        Generate the header to hold the filter data.
        Returns a string like this: "cp002003ima02pa02os"
        "cp"
        + 4 byte to represent the number of filters (from 0000 to 9999)
        then for each filter
            + 1 byte to represent the byte used to replace the filter ocurrences
            + 2 filter size (00 to 99)
            + the filter itself (number of bytes is the same as the filter size)
        """
        header = f"cp{len(filters):04}".encode()
        for filter in filters:
            header += f"{filter.get_size():02}".encode()
            for byte in filter.get_kernel():
                header += byte
        return header

    def compress(self, filters: List[ConvFilter], output: str) -> None:
        """process string replacing filter matches with new bytes representing the filter"""
        
        used_filters: List[ConvFilter] = []
        user_newbytes: List[byte] = []
        for filter in filters:
            matches = self.__convolve(filter)
            if len(matches) < self.get_min_matches_necessary():
                continue
            newbyte = self.get_available_byte()
            for pos in matches:
                self.bytelist[pos] = newbyte
            for idx, byte in enumerate(self.bytelist):
                if byte == newbyte:
                    for f in range(filter.get_size()):
                        if f == 0:
                            self.bytelist[idx+f] = self.bytelist[idx+f].encode('utf-8')
                            continue
                        self.bytelist.pop(idx+f)
            used_filters.append(filter)
            user_newbytes.append(newbyte)

        header = self.generate_header(used_filters,user_newbytes)
            
        with open(output, 'bw') as file:
            file.write(header)
            for b in self.bytelist:
                file.write(bytes(b))
