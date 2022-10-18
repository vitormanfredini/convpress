"""
Class for holding the filter data
and some operations
"""

from __future__ import annotations
import random
from typing import List

from utils.bytes_operations import bytestring_to_bytelist


class ConvFilter:
    """
    Kernel/filter for sequences of bytes
    """

    def __init__(self, size: int):
        self.kernel: bytes = List[bytes]
        self.kernel = []
        for _ in range(size):
            self.kernel.append(b"")
        self.byte_it_represents = b"\x00"

    def set_byte_it_represents(self, byte_it_represents: bytes):
        """Sets the byte that this filter represents"""
        self.byte_it_represents = byte_it_represents

    def get_byte_it_represents(self) -> bytes:
        """Gets the byte that this filter represents"""
        return self.byte_it_represents

    def randomize_from_list(self, unique_bytelist: list, wildcard_chance: float, wildcard_byte):
        """
        Randomize kernel bytes using a list of bytes,
        all indexes (except both ends) have a wildcard_chance
        of receiving a wildcard_byte
        """
        new_kernel = []
        used_wildcard_once = False
        for kernel_idx in range(self.get_size()):
            rand_idx = random.randrange(len(unique_bytelist))
            byte_to_use = unique_bytelist[rand_idx]

            if used_wildcard_once is False:
                if kernel_idx > 0 and kernel_idx < (self.get_size() - 1):
                    if random.uniform(0.0, 1.0) < wildcard_chance:
                        byte_to_use = wildcard_byte
                        used_wildcard_once = True

            new_kernel.append(byte_to_use)

        self.kernel = new_kernel

    def set_kernel_bytes_using_bytestring(self, bytestring: bytes):
        """set kernel bytes using a bytestring"""
        self.kernel = bytestring_to_bytelist(bytestring)

    def crossover(self, other: ConvFilter):
        """
        Crossover the information
        between 2 filters
        to create a new one
        """

        new_filter = ConvFilter(self.get_size())
        new_filter.kernel = self.get_kernel().copy()

        random_skip = 0
        size_diff = abs(self.get_size() - other.get_size())
        if size_diff > 0:
            random_skip = random.randrange(size_diff)

        smaller_size = self.get_size()
        if other.get_size() < smaller_size:
            smaller_size = other.get_size()

        for idx in range(smaller_size):
            if random.choice([0, 1]) == 1:
                if self.get_size() > other.get_size():
                    new_filter.kernel[random_skip + idx] = other.kernel[idx]
                else:
                    new_filter.kernel[idx] = other.kernel[random_skip + idx]

        return new_filter

    def get_wildcards_indexes(self, wildcard_byte: bytes) -> List:
        """get a list of indexes of all the wildcards in the kernel"""
        indexes = []
        for kernel_idx, kernel_byte in enumerate(self.get_kernel()):
            if kernel_byte == wildcard_byte:
                indexes.append(kernel_idx)
        return indexes

    def get_kernel(self):
        """get kernel's list of bytes"""
        return self.kernel

    def get_size(self):
        """get kernel's size"""
        return len(self.kernel)

    def calculate_footprint_in_bytes(self):
        """calculate how many bytes this filter will use in the file header"""
        extrabytes = 3  # see Convpress.generate_header()
        return self.get_size() + extrabytes

    def __eq__(self, other: ConvFilter):
        if self.get_size() != other.get_size():
            return False
        for kernel_idx in range(self.get_size()):
            if self.kernel[kernel_idx] != other.kernel[kernel_idx]:
                return False
        return True

    def __str__(self):
        output = f"size {self.get_size()}"
        output += f" _\\x{self.get_byte_it_represents().hex()}_"
        output += " _"
        for kernel_byte in self.kernel:
            output += f"\\x{kernel_byte.hex()}"
        output += '_'
        return output
