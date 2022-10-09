from dataclasses import dataclass, field
from io import TextIOWrapper
import random
import sys

from typing import List
from classes.ConvFilter import ConvFilter

class RanOutOfPossibleBytes(Exception):
    pass

class UnexpectedHeaderFormat(Exception):
    pass

@dataclass()
class Convpress:
    """
    Class for matching filters against the input data, 
    calculating the score for each filter,
    calculating string coverage of all filters processed, 
    compressing/decompressing the data
    and generating the output file
    """

    bytelist: List[bytes] = field(default_factory=list)
    uniquebytelist: List[bytes] = field(default_factory=list)
    adittionalbytelist: List[bytes] = field(default_factory=list)
    input_file: TextIOWrapper = None
    output_file: TextIOWrapper = None
    wildcard_byte: bytes = None
    current_filter_scores: List[float] = field(default_factory=list)

    bytes_to_decompress: List[bytes] = field(default_factory=list)
    decompress_filters: List[ConvFilter] = field(default_factory=list)
    

    def reset(self):
        self.bytelist = []
        self.uniquebytelist = []
        self.adittionalbytelist = []
        self.input_file = None
        self.wildcard_byte = None
        self.current_filter_scores = []

        self.decompress_filters: List[ConvFilter] = []
        self.bytes_to_decompress: List[ConvFilter] = []
    
    def set_output_file(self, output_file: TextIOWrapper):
        self.output_file = output_file
    
    def get_bytelist(self) -> list:
        return self.bytelist

    def get_unique_bytelist(self) -> list:
        return self.uniquebytelist

    def get_wildcard_byte(self):
        return self.wildcard_byte
    
    def load_file_for_decompression(self, filename: TextIOWrapper):
        self.reset()
        self.input_file = filename

        print(f"Loading file: {self.input_file.name}")

        # parse header
        try:
            cp_marker = self.input_file.read(2)
            if cp_marker != b'cp':
                raise UnexpectedHeaderFormat("First two bytes aren't the correct marker.")

            self.wildcard_byte = self.input_file.read(1)
            
            number_of_filters = int(self.input_file.read(4).decode())
            print(f"Found {number_of_filters} filters")

            for f in range(number_of_filters):
                byte_to_decompress = self.input_file.read(1)
                self.bytes_to_decompress.append(byte_to_decompress)

                filter_size = int(self.input_file.read(2).decode())
                new_filter = ConvFilter(filter_size)
                for k in range(filter_size):
                    new_filter.kernel[k] = self.input_file.read(1)
                self.decompress_filters.append(new_filter)

        except Exception as e:
            raise UnexpectedHeaderFormat(str(e))

        print(f"Loading data")
        byte = self.input_file.read(1)
        while byte:
            self.bytelist.append(byte)
            byte = self.input_file.read(1)
        self.input_file.close()


    def load_file(self, filename: TextIOWrapper):
        self.reset()

        self.input_file = filename
        print(f"Loading: {self.input_file.name}")
        byte = self.input_file.read(1)
        while byte:
            self.bytelist.append(byte)
            if byte not in self.uniquebytelist:
                self.uniquebytelist.append(byte)
            byte = self.input_file.read(1)
        self.input_file.close()
        
        self.wildcard_byte = self.get_available_byte()
        
    def __convolve(self, filter: ConvFilter):
        kernel = filter.get_kernel()
        matches = []
        c = 0
        while c < len(self.bytelist) - filter.get_size():
            match = True
            for f in range(filter.get_size()):
                if kernel[f] == self.wildcard_byte:
                    continue
                if kernel[f] == self.bytelist[c+f]:
                    continue
                match = False
            if match == True:
                matches.append(c)
                c += filter.get_size()
            else:
                c += 1
        return matches

    def get_wildcards_indexes(self, filter: ConvFilter):
        kernel = filter.get_kernel()
        indexes = []
        for i in range(len(kernel)):
            if kernel[i] == self.wildcard_byte:
                indexes.append(i)
        return indexes

    def convolve_all_and_get_generation_score(self, filtersToConvolve: List[ConvFilter]):
        """
        Calculate and return the generation score
        which is the percentage of the string
        that was covered by all filters.
        Individual filter scores are also calculated
        based on how many matches it found.
        """
        unique_matches = []
        self.current_filter_scores = []
        for filter in filtersToConvolve:
            matches = self.__convolve(filter)
            for match_index in matches:
                if match_index not in unique_matches:
                    unique_matches.append(match_index)
            filter_score = len(matches) * (filter.get_size() - len(self.get_wildcards_indexes(filter)))
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
    
    def debug_scores(self):
        print('debug_scores')
        print(self.current_filter_scores)

    def get_available_byte(self):
        for i in range(sys.maxunicode):
            try:
                byte = chr(i).encode('utf-8')
            except UnicodeEncodeError as e:
                continue
            if len(byte) > 1:
                continue
            if byte in self.uniquebytelist:
                continue
            if byte in self.adittionalbytelist:
                continue
            self.adittionalbytelist.append(byte)
            return byte
        raise RanOutOfPossibleBytes("All possible bytes are in use. Can't proceed.")
    
    def get_min_matches_necessary(self):
        """number of filter matches necessary to reduce the string more than it adds to the header"""
        return 5
    
    def generate_header(self, filters: List[ConvFilter], bytes:list) -> bytes:
        """
        Generate the header to hold the filter data.
        Returns a byte string like this: "cp$002003ima02pa02os"
        2 bytes to represent the "cp" marker
        + 1 byte to represent the wildcard
        + 4 byte to represent the number of filters (from 0000 to 9999)
        then for each filter
            + 1 byte to represent the byte used to replace the filter ocurrences
            + 2 bytes to represent the filter size (00 to 99)
            + the filter itself (number of bytes will be the same as the filter size)
        """
        
        header = f"cp".encode()
        header += self.wildcard_byte
        header += f"{len(filters):04}".encode()
        for idx, filter in enumerate(filters):
            header += bytes[idx]
            header += f"{filter.get_size():02}".encode()
            for byte in filter.get_kernel():
                header += byte
        return header

    def compress(self, filters: List[ConvFilter]) -> None:
        """process bytelist replacing filter matches with new bytes representing the filter"""
        print("Compressing")
        used_filters: List[ConvFilter] = []
        used_newbytes: List[byte] = []
        for filter in filters:
            matches = self.__convolve(filter)
            if len(matches) < self.get_min_matches_necessary():
                continue
            newbyte = self.get_available_byte()
            for pos in matches:
                self.bytelist[pos] = newbyte
            indexes_to_pop = []
            for idx, byte in enumerate(self.bytelist):
                if byte == newbyte:
                    wildcard_indexes = self.get_wildcards_indexes(filter=filter)
                    for f in range(filter.get_size()):
                        if f == 0:
                            # self.bytelist[idx+f] = self.bytelist[idx+f].encode('utf-8')
                            continue
                        if f not in wildcard_indexes:
                            indexes_to_pop.append(idx+f)
            for index in reversed(indexes_to_pop):
                self.bytelist.pop(index)
            used_filters.append(filter)
            used_newbytes.append(newbyte)

        header = self.generate_header(used_filters,used_newbytes)
        self.output_file.write(header)
        for b in self.bytelist:
            self.output_file.write(b)
        self.output_file.close()

    def decompress(self) -> None:
        """process bytelist replacing the bytes for its corresponding filter"""
        print("Decompressing")
        for idx, byte in enumerate(self.bytelist):
            for byte_decompress_idx, b in enumerate(self.bytes_to_decompress):
                if byte != b:
                    continue
                filter: ConvFilter = self.decompress_filters[byte_decompress_idx]
                kernel = filter.get_kernel()
                for k in range(filter.get_size()):
                    if kernel[k] == self.wildcard_byte:
                        continue
                    if k == 0:
                        self.bytelist[idx] = kernel[k]
                    else:
                        self.bytelist.insert(idx+k,kernel[k])
        
        for b in self.bytelist:
            self.output_file.write(b)
        self.output_file.close()