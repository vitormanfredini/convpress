"""
Convpress module
"""
from dataclasses import dataclass, field
from io import TextIOWrapper
import sys

from typing import List
from classes.ConvFilter import ConvFilter

from utils.bytes_operations import bytestring_to_bytelist

class RanOutOfPossibleBytes(Exception):
    """
    Error for when there are no more chars in the encoding
    that can be represented by only one byte
    """

class UnexpectedHeaderFormat(Exception):
    """Error for when the header isn't valid"""

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
    current_filters_scores: List[float] = field(default_factory=list)
    current_filters_matches: List[List[int]] = field(default_factory=list)
    bytes_to_decompress: List[bytes] = field(default_factory=list)
    decompress_filters: List[ConvFilter] = field(default_factory=list)
    current_filters_indexes_it_affects: List[List[bool]] = field(default_factory=list)
    filters_in_use: List[ConvFilter] = field(default_factory=list)
    encoding: str = "latin1"

    def reset(self):
        """resets everything"""

        self.bytelist = []
        self.uniquebytelist = []
        self.adittionalbytelist = []
        self.input_file = None
        self.wildcard_byte = None
        self.current_filters_scores = []
        self.current_filters_matches = []
        self.current_filters_indexes_it_affects = []
        self.decompress_filters = []
        self.bytes_to_decompress = []
        self.filters_in_use = []

    def set_output_file(self, output_file: TextIOWrapper):
        """set the output file"""
        self.output_file = output_file

    def get_bytelist(self) -> list:
        """get the bytelist"""
        return self.bytelist

    def get_unique_bytelist(self) -> list:
        """get a list of unique bytes in the input file"""
        return self.uniquebytelist

    def get_wildcard_byte(self):
        """get wildcard byte that is currently being used"""
        return self.wildcard_byte

    def load_bytelist_from_bytestring(self, bytestring: bytes):
        """loads bytelist using a bytestring"""
        self.bytelist = bytestring_to_bytelist(bytestring)

    def load_file_for_decompression(self, filename: TextIOWrapper):
        """loads file for decompressing it"""
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

            for _ in range(number_of_filters):
                byte_to_decompress = self.input_file.read(1)
                self.bytes_to_decompress.append(byte_to_decompress)

                filter_size = int(self.input_file.read(2).decode())
                new_filter = ConvFilter(filter_size)
                for k in range(filter_size):
                    new_filter.kernel[k] = self.input_file.read(1)
                self.decompress_filters.append(new_filter)

        except Exception as exception:
            raise UnexpectedHeaderFormat(str(exception)) from exception

        print("Loading data")
        byte = self.input_file.read(1)
        while byte:
            self.bytelist.append(byte)
            byte = self.input_file.read(1)
        self.input_file.close()


    def load_file(self, filename: TextIOWrapper):
        """loads a file for compressing it"""

        self.reset()
        self.input_file = filename

        byte = self.input_file.read(1)
        while byte:
            self.bytelist.append(byte)
            if byte not in self.uniquebytelist:
                self.uniquebytelist.append(byte)
            byte = self.input_file.read(1)
        self.input_file.close()

        self.wildcard_byte = self.get_available_byte()

    def get_wildcards_indexes(self, from_filter: ConvFilter):
        """get a list of indexes of all the wildcards in the kernel"""
        kernel = from_filter.get_kernel()
        indexes = []
        for idx, byte in enumerate(kernel):
            if byte == self.wildcard_byte:
                indexes.append(idx)
        return indexes

    def convolve_all(self, filters_to_convolve: List[ConvFilter]):
        """convolve all filters and save their matches"""
        self.filters_in_use = filters_to_convolve
        self.current_filters_matches = []
        for filter_to_convolve in self.filters_in_use:
            matches = self.__convolve(filter_to_convolve)
            self.current_filters_matches.append(matches)

    def __convolve(self, filter_to_convolve: ConvFilter):
        kernel = filter_to_convolve.get_kernel()
        matches = []
        bytelist_idx = 0

        while bytelist_idx < len(self.bytelist) - filter_to_convolve.get_size():
            match = True
            for kernel_idx in range(filter_to_convolve.get_size()):
                if kernel[kernel_idx] == self.wildcard_byte:
                    continue
                if kernel[kernel_idx] == self.bytelist[bytelist_idx+kernel_idx]:
                    continue
                match = False
            if match:
                matches.append(bytelist_idx)
                bytelist_idx += filter_to_convolve.get_size()
            else:
                bytelist_idx += 1

        return matches

    def calculate_generation_score(self):
        """
        Calculate the generation score
        by calculating the
        1- scores of individual filters (number of matches)
           and applying a penalty for overlapping with other filters,
        2- calculate average
        3- multiply by string coverage
        """
        self.__generate_boolean_lists_of_filters_matches()

        indexes_repetition_count: List[int] = [0 for i in range(len(self.bytelist))]
        for boolean_list in self.current_filters_indexes_it_affects:
            for idx, item in enumerate(boolean_list):
                if item:
                    indexes_repetition_count[idx] += 1

        self.current_filters_scores = []
        score_sum = 0
        for boolean_list in self.current_filters_indexes_it_affects:
            score = self.calculate_one_score(
                affected_by_filter = boolean_list,
                bytes_repetition = indexes_repetition_count
                )
            score_sum =+ score
            self.current_filters_scores.append(score)

        scores_average = score_sum / len(self.current_filters_indexes_it_affects)
        final_score = scores_average * self.__calculate_string_coverage()
        return final_score

    def __generate_boolean_lists_of_filters_matches(self):
        """
        This functions generate booleans lists
        that have the same length as the input file and
        they hold true where that byte matched with the filter
        or false where it didn't
        """

        self.current_filters_indexes_it_affects = []
        for idx_matches, filter_matches in enumerate(self.current_filters_matches):

            filter_to_read = self.filters_in_use[idx_matches]
            boolean_indexes_it_affects = [False for i in range(len(self.bytelist))]

            for match_index in filter_matches:
                for k in range(filter_to_read.get_size()):
                    if filter_to_read.get_kernel()[k] != self.wildcard_byte:
                        boolean_indexes_it_affects[match_index+k] = True

            self.current_filters_indexes_it_affects.append(boolean_indexes_it_affects)

    def __calculate_string_coverage(self) -> float:

        boolean_unique_matches = [False for i in range(len(self.bytelist))]
        count = 0

        if len(self.current_filters_indexes_it_affects) == 0:
            self.__generate_boolean_lists_of_filters_matches()

        for bool_match_list in self.current_filters_indexes_it_affects:
            for idx, bool_affected in enumerate(bool_match_list):
                if bool_affected:
                    if not boolean_unique_matches[idx]:
                        boolean_unique_matches[idx] = True
                        count += 1

        return count / len(self.bytelist)


    def calculate_one_score(self, affected_by_filter: List[bool], bytes_repetition: List[int]):
        """
        Calculate score for one filter
        by using how many matches it had
        and applying a penalty when that particular match
        affects the same places as other filters
        """

        score = 0
        for idx_affected, affected in enumerate(affected_by_filter):
            if affected:
                repetition_penalty_division = 1.0 + bytes_repetition[idx_affected]
                score += 1 / repetition_penalty_division
        return score

    def get_current_filters_scores(self) -> list:
        """get list of convolved filters scores"""
        return self.current_filters_scores

    def debug_scores(self):
        """prints scores"""
        print('debug_scores')
        print(self.current_filters_scores)

    def get_available_byte(self):
        """
        Get a byte value that haven't been used yet
        """

        if self.encoding == 'utf-8':
            max_chars = sys.maxunicode
        elif self.encoding == 'latin1':
            max_chars = 256
        else:
            raise ValueError(f"Encoding {self.encoding} is not supported")

        for i in range(max_chars):
            byte = chr(i).encode(self.encoding)
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
        """Number of matches necessary to reduce the string more than it adds to it"""
        return 5

    def generate_header(self, used_filters: List[ConvFilter], used_newbytes: list) -> bytes:
        """
        Generate the header to necessary data for later decompression.
        Returns a byte string like this: "cp$002003ima02pa02os"
        2 bytes to represent the convpress marker: "cp"
        + 1 byte to represent the wildcard
        + 4 byte to represent the number of filters (from 0000 to 9999)
        then for each filter
            + 1 byte to represent the byte used to replace the filter ocurrences
            + 2 bytes to represent the filter size (00 to 99)
            + the filter itself (number of bytes will be the same as the filter size)
        """

        header = "cp".encode(self.encoding)
        header += self.wildcard_byte
        header += f"{len(used_filters):04}".encode(self.encoding)
        for idx, filter_to_write in enumerate(used_filters):
            header += used_newbytes[idx]
            header += f"{filter_to_write.get_size():02}".encode(self.encoding)
            for byte in filter_to_write.get_kernel():
                header += byte
        return header

    def compress(self, filters: List[ConvFilter]) -> None:
        """process bytelist replacing filter matches with new bytes representing the filter"""

        used_filters: List[ConvFilter] = []
        used_newbytes: List[bytes] = []

        for filter_to_convolve in filters:
            matches = self.__convolve(filter_to_convolve)
            if len(matches) < self.get_min_matches_necessary():
                continue
            newbyte = self.get_available_byte()
            self.substitute_matches_for_newbyte(
                matches = matches,
                newbyte = newbyte,
                filter_used = filter_to_convolve
                )
            used_filters.append(filter_to_convolve)
            used_newbytes.append(newbyte)

        header = self.generate_header(used_filters, used_newbytes)

        self.output_file.write(header)
        for byte in self.bytelist:
            self.output_file.write(byte)
        self.output_file.close()

    def substitute_matches_for_newbyte(self, matches, newbyte, filter_used):
        """
        Replaces the bytes where the matches happened
        for the byte that represents the filter
        """

        filter_wildcard_indexes = self.get_wildcards_indexes(from_filter = filter_used)

        for pos in matches:
            self.bytelist[pos] = newbyte

        indexes_to_pop = []
        for byte_idx, byte in enumerate(self.bytelist):
            if byte == newbyte:
                for filter_idx in range(filter_used.get_size()):
                    if filter_idx > 0 and filter_idx not in filter_wildcard_indexes:
                        indexes_to_pop.append(byte_idx+filter_idx)

        for index in reversed(indexes_to_pop):
            self.bytelist.pop(index)

    def decompress(self) -> None:
        """process bytelist replacing the bytes for its corresponding filter"""

        for idx, byte in enumerate(self.bytelist):
            for byte_decompress_idx, byte_to_decompress in enumerate(self.bytes_to_decompress):
                if byte != byte_to_decompress:
                    continue

                filter_for_decompression: ConvFilter = self.decompress_filters[byte_decompress_idx]
                kernel = filter_for_decompression.get_kernel()
                for k in range(filter_for_decompression.get_size()):
                    if kernel[k] == self.wildcard_byte:
                        continue
                    if k == 0:
                        self.bytelist[idx] = kernel[k]
                    else:
                        self.bytelist.insert(idx+k,kernel[k])

        for byte_to_decompress in self.bytelist:
            self.output_file.write(byte_to_decompress)
        self.output_file.close()
