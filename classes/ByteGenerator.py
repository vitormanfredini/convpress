"""
Convpress module
"""
from dataclasses import dataclass, field

from typing import List

class RanOutOfPossibleBytes(Exception):
    """
    Error for when there are no more chars in the encoding
    that can be represented by only one byte
    """

@dataclass()
class ByteGenerator:
    """
    Class for matching filters against the input data,
    calculating the score for each filter,
    calculating string coverage of all filters processed,
    compressing/decompressing the data
    and generating the output file
    """

    bytes_taken: List[bytes] = field(default_factory=list)
    encoding: str = ""

    def __init__(self, encoding: str):
        """ Initializes everything """

        if encoding not in ByteGenerator.get_supported_encodings():
            raise ValueError(f"Encoding {self.encoding} is not supported")

        self.encoding = encoding
        self.bytes_taken = []

    def get_next_available_byte(self, except_those: List[bytes]) -> bytes:
        """
        Get a byte value that haven't been used yet
        """

        max_chars = 256
        for i in range(max_chars):
            byte = chr(i).encode(self.encoding)
            if len(byte) > 1:
                continue
            if byte in except_those:
                continue
            if byte in self.bytes_taken:
                continue
            self.bytes_taken.append(byte)
            return byte

        raise RanOutOfPossibleBytes("All possible bytes are in use. Can't proceed.")

    def get_encoding(self) -> str:
        """ get encoding """
        return self.encoding

    @staticmethod
    def get_supported_encodings():
        """ get list of supported encodings """
        return ['utf-8', 'latin1', 'cp1252']
