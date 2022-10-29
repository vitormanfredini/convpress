"""
Convpress module
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from io import TextIOWrapper

from typing import List
from classes.ByteGenerator import ByteGenerator
from classes.ConvFilter import ConvFilter

from utils.bytes_operations import bytestring_to_bytelist
from utils.custom_map import map_easein


class RanOutOfPossibleBytes(Exception):
    """
    Error for when there are no more chars in the encoding
    that can be represented by only one byte
    """


class UnexpectedHeaderFormat(Exception):
    """Error for when the header isn't valid"""


class RepetitionPenaltyType(Enum):
    """
    Types of penalty that can be applied
    to scores of filters with overlapping coverage
    """
    DIVIDE_BY_NUMBER_OF_REPETITIONS = auto()  # rigorous
    LINEARLY_PROPORTIONAL = auto()  # linear
    PERMISSIVE = auto()  # permissive


@dataclass()
class Convpress:
    """
    Class for matching filters against the input data,
    calculating the score for each filter,
    calculating string coverage of all filters processed,
    compressing/decompressing the data
    and generating the output file
    """

    byte_list: List[bytes] = field(default_factory=list)
    unique_byte_list: List[bytes] = field(default_factory=list)
    input_file: TextIOWrapper = None
    output_file: TextIOWrapper = None
    wildcard_byte: bytes = None
    current_filters_scores: List[float] = field(default_factory=list)
    current_filters_matches: List[List[int]] = field(default_factory=list)
    bytes_to_decompress: List[bytes] = field(default_factory=list)
    decompress_filters: List[ConvFilter] = field(default_factory=list)
    indexes_affected_by_filters: List[List[bool]] = field(default_factory=list)
    filters_in_use: List[ConvFilter] = field(default_factory=list)
    penalty_type: RepetitionPenaltyType = RepetitionPenaltyType.DIVIDE_BY_NUMBER_OF_REPETITIONS

    def __init__(self, byte_generator: ByteGenerator):
        """resets everything"""

        self.byte_generator = byte_generator
        self.reset()

    def reset(self):
        """ reset the things the need to be reseted """

        self.byte_list = []
        self.unique_byte_list = []
        self.input_file = None
        self.wildcard_byte = None
        self.current_filters_scores = []
        self.current_filters_matches = []
        self.indexes_affected_by_filters = []
        self.decompress_filters = []
        self.bytes_to_decompress = []
        self.filters_in_use = []

    def set_output_file(self, output_file: TextIOWrapper):
        """set the output file"""
        self.output_file = output_file

    def get_bytelist(self) -> list:
        """get the bytelist"""
        return self.byte_list

    def get_unique_bytelist(self) -> list:
        """get a list of unique bytes in the input file"""
        return self.unique_byte_list

    def get_wildcard_byte(self):
        """get wildcard byte that is currently being used"""
        return self.wildcard_byte

    def load_bytelist_from_bytestring(self, bytestring: bytes):
        """loads bytelist using a bytestring"""
        self.byte_list = bytestring_to_bytelist(bytestring)

    def load_file_for_decompression(self, filename: TextIOWrapper):
        """loads file for decompressing it"""
        self.reset()
        self.input_file = filename

        print(f"Loading file: {self.input_file.name}")

        # parse header
        try:
            cp_marker = self.input_file.read(2)
            if cp_marker != b'cp':
                raise UnexpectedHeaderFormat(
                    "First two bytes aren't the correct marker.")

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
            self.byte_list.append(byte)
            byte = self.input_file.read(1)
        self.input_file.close()

    def load_file(self, filename: TextIOWrapper):
        """loads a file for compressing it"""

        self.reset()
        self.input_file = filename

        byte = self.input_file.read(1)
        while byte:
            self.byte_list.append(byte)
            if byte not in self.unique_byte_list:
                self.unique_byte_list.append(byte)
            byte = self.input_file.read(1)
        self.input_file.close()

        self.wildcard_byte = self.byte_generator.get_next_available_byte(
            except_those=self.unique_byte_list
            )

    def convolve_all(self, filters_to_convolve: List[ConvFilter]):
        """convolve all filters and save their matches"""
        self.filters_in_use = filters_to_convolve
        self.current_filters_matches = []
        for filter_to_convolve in self.filters_in_use:
            matches = self.convolve(filter_to_convolve)
            self.current_filters_matches.append(matches)

    def convolve(self, filter_to_convolve: ConvFilter):
        """Convolve filter and return perfect matches"""
        kernel = filter_to_convolve.get_kernel()
        matches = []
        bytelist_idx = 0

        while bytelist_idx < len(self.byte_list) - filter_to_convolve.get_size():
            match = True
            for kernel_idx in range(filter_to_convolve.get_size()):
                if kernel[kernel_idx] == self.wildcard_byte:
                    continue
                if kernel[kernel_idx] == self.byte_list[bytelist_idx+kernel_idx]:
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
        by calculating the percentage of the input file it covers
        """
        self.__generate_boolean_lists_of_filters_matches()

        indexes_repetition_count: List[int] = [
            0 for i in range(len(self.byte_list))]
        for boolean_list in self.indexes_affected_by_filters:
            for idx, item in enumerate(boolean_list):
                if item:
                    indexes_repetition_count[idx] += 1

        self.current_filters_scores = []
        for boolean_list in self.indexes_affected_by_filters:
            score = self.calculate_one_score(
                affected_by_filter=boolean_list,
                bytes_repetition=indexes_repetition_count
            )
            self.current_filters_scores.append(score)

        return self.__calculate_string_coverage()

    def __generate_boolean_lists_of_filters_matches(self):
        """
        This functions generate booleans lists
        that have the same length as the input file and
        they hold true where that byte matched with the filter
        or false where it didn't
        """

        self.indexes_affected_by_filters = []
        for idx_matches, filter_matches in enumerate(self.current_filters_matches):

            filter_to_read = self.filters_in_use[idx_matches]
            boolean_indexes_it_affects = [
                False for i in range(len(self.byte_list))]

            for match_index in filter_matches:
                for k in range(filter_to_read.get_size()):
                    if filter_to_read.get_kernel()[k] != self.wildcard_byte:
                        boolean_indexes_it_affects[match_index+k] = True

            self.indexes_affected_by_filters.append(
                boolean_indexes_it_affects)

    def __calculate_string_coverage(self) -> float:

        boolean_unique_matches = [False for i in range(len(self.byte_list))]
        count = 0

        if len(self.indexes_affected_by_filters) == 0:
            self.__generate_boolean_lists_of_filters_matches()

        for bool_match_list in self.indexes_affected_by_filters:
            for idx, bool_affected in enumerate(bool_match_list):
                if bool_affected:
                    if not boolean_unique_matches[idx]:
                        boolean_unique_matches[idx] = True
                        count += 1

        return count / len(self.byte_list)

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
                score += self.apply_repetition_penalty(
                    1.0,
                    bytes_repetition[idx_affected]
                )
        return score

    def apply_repetition_penalty(self, score: float, repetitions: int):
        """apply penalty for repetition"""
        if repetitions > 1:

            possible_types = [item.value for item in RepetitionPenaltyType]
            if self.penalty_type.value not in possible_types:
                raise ValueError("Invalid penalty_type.")

            if self.penalty_type is RepetitionPenaltyType.DIVIDE_BY_NUMBER_OF_REPETITIONS:
                return score / repetitions

            if self.penalty_type is RepetitionPenaltyType.LINEARLY_PROPORTIONAL:
                ratio = (repetitions - 1) / (len(self.filters_in_use) - 1)
                return score - (score * ratio)

            if self.penalty_type is RepetitionPenaltyType.PERMISSIVE:
                return score - (score * map_easein(ratio))

        return score

    def set_repetition_penalty_type(self, penalty_type: RepetitionPenaltyType):
        """set the repetition penalty type"""
        self.penalty_type = penalty_type

    def get_current_filters_scores(self) -> list:
        """get list of convolved filters scores"""
        return self.current_filters_scores

    def debug_scores(self):
        """prints all scores"""
        print('debug_scores')
        print(self.current_filters_scores)

    def get_min_matches_necessary(self):
        """Number of matches necessary to reduce the string more than it adds to it"""
        return 20

    def generate_header(self, used_filters: List[ConvFilter]) -> bytes:
        """
        Generate the header with necessary data for later decompression.
        Returns a byte string like this: "cp$002003ima02pa02os"
        2 bytes to represent the convpress marker: "cp"
        + 1 byte to represent the wildcard
        + 4 bytes to represent the number of filters (from 0000 to 9999)
        then for each filter
            + 1 byte to represent the byte used to replace the filter ocurrences
            + 2 bytes to represent the filter size (00 to 99)
            + the filter itself (number of bytes will be the same as the filter size)
        """

        encoding = self.byte_generator.get_encoding()
        header = "cp".encode(encoding)
        header += self.wildcard_byte
        header += f"{len(used_filters):04}".encode(encoding)
        for filter_to_write in used_filters:
            header += filter_to_write.get_byte_it_represents()
            header += f"{filter_to_write.get_size():02}".encode(encoding)
            for byte in filter_to_write.get_kernel():
                header += byte
        return header

    def compress(self, filters_to_use: List[ConvFilter]) -> None:
        """
        Convolve filters and replace matches with new bytes representing the filter.
        Returns the filters that were actually used.
        """

        actually_used: List[ConvFilter] = []

        for filter_to_convolve in filters_to_use:

            matches = self.convolve(filter_to_convolve)

            if len(matches) < self.get_min_matches_necessary():
                continue

            newbyte = self.byte_generator.get_next_available_byte(
                except_those=self.unique_byte_list
                )
            filter_to_convolve.set_byte_it_represents(newbyte)

            self.replace_matches_for_newbyte(
                matches=matches,
                filter_used=filter_to_convolve
            )

            actually_used.append(filter_to_convolve)

        return actually_used

    def replace_matches_for_newbyte(self, matches: List[int], filter_used: ConvFilter):
        """
        For every match, replace the first byte
        for the byte that represents the filter
        and remove the rest from the array
        """

        filter_wildcard_indexes = filter_used.get_wildcards_indexes(
            wildcard_byte=self.get_wildcard_byte())

        for matched_idx in matches:
            self.byte_list[matched_idx] = filter_used.get_byte_it_represents()

        indexes_to_pop = []
        for byte_idx, byte in enumerate(self.byte_list):
            if byte == filter_used.get_byte_it_represents():
                for filter_idx in range(filter_used.get_size()):
                    if filter_idx > 0 and filter_idx not in filter_wildcard_indexes:
                        indexes_to_pop.append(byte_idx+filter_idx)

        for index in reversed(indexes_to_pop):
            self.byte_list.pop(index)

    def decompress(self) -> None:
        """
        Decompress the bytelist by replacing the bytes
        for its corresponding filter's kernel
        """
        for idx, byte in enumerate(self.byte_list):
            for byte_decompress_idx, byte_to_decompress in enumerate(self.bytes_to_decompress):
                if byte != byte_to_decompress:
                    continue

                self.replace_byte_for_kernel(
                    idx, self.decompress_filters[byte_decompress_idx])

    def output_file_from_bytelist(self, header: bytes = None) -> None:
        """Saves the current bytelist to a file."""

        if header is not None:
            self.output_file.write(header)

        for byte in self.byte_list:
            self.output_file.write(byte)
        self.output_file.close()

    def replace_byte_for_kernel(self, byte_index: int, filter_for_decompression: ConvFilter):
        """
        Decompress one byte at specific index for a filter's kernel.
        This process accounts for wildcards too.
        """

        for kernel_idx, kernel_byte in enumerate(filter_for_decompression.get_kernel()):
            if kernel_byte == self.wildcard_byte:
                continue
            if kernel_idx == 0:
                self.byte_list[byte_index] = kernel_byte
            else:
                self.byte_list.insert(byte_index + kernel_idx, kernel_byte)
