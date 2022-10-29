"""
Test to check if bytes are being replaced correctly by the filters.
Enconding: latin1
"""
import unittest
import sys
from classes.ByteGenerator import ByteGenerator
from classes.ConvFilter import ConvFilter
from classes.Convpress import Convpress
from utils.bytes_operations import bytelist_to_bytestring

sys.path.append("..")

class Testing(unittest.TestCase):
    """
    Tests the replacement of bytes
    with different filter lengths
    with and without the presence of wildcards
    """

    def setUp(self) -> None:
        byte_generator = ByteGenerator("latin1")
        self.convpress = Convpress(byte_generator)
        return super().setUp()

    def test_replace_byte_by_filter_length_2(self):
        """Test with length 2 filter"""

        filter_to_use = ConvFilter(2)
        filter_to_use.set_kernel_bytes_using_bytestring(b"\xfd\xe8")
        self.convpress.load_bytelist_from_bytestring(
            b"\xfd\xe8r\xc9\x1e?\xfda\xe8\xc9\xa4\xb9a\xfd\xe8\xfd7\xa4"
            )
        self.convpress.replace_byte_for_kernel(
            byte_index = 4,
            filter_for_decompression = filter_to_use
            )
        bytestring_should_be = b"\xfd\xe8r\xc9\xfd\xe8?\xfda\xe8\xc9\xa4\xb9a\xfd\xe8\xfd7\xa4"
        self.assertTrue(bytelist_to_bytestring(self.convpress.byte_list) == bytestring_should_be)

    def test_replace_filter_length_3(self):
        """Test with length 3 filter"""

        filter_to_use = ConvFilter(3)
        filter_to_use.set_kernel_bytes_using_bytestring(b"\xe8\xc9\xa4")
        self.convpress.load_bytelist_from_bytestring(
            b"\xfd\xe8r\xc9\x1e?\xfda\xe8\xc9\xa4dw\xb9a\xfd\xe8\xfd7\xa4"
            )
        self.convpress.replace_byte_for_kernel(
            byte_index = 2,
            filter_for_decompression = filter_to_use
            )
        bytestring_should_be = b"\xfd\xe8\xe8\xc9\xa4\xc9\x1e?\xfda\xe8\xc9\xa4dw\xb9a\xfd\xe8\xfd7\xa4"
        self.assertTrue(bytelist_to_bytestring(self.convpress.byte_list) == bytestring_should_be)

    def test_replace_filter_length_3_with_wildcard(self):
        """Test with length 3 filter with wildcard"""

        filter_to_use = ConvFilter(3)
        filter_to_use.set_kernel_bytes_using_bytestring(b"\xe8\x12\xa4")
        self.convpress.load_bytelist_from_bytestring(
            b"\xfd\xe8\x55\xa4\x1e?\xfda\xe8\xc9\xe8\x3a\xa4\xfd\xe8\xfd7\xa4"
            )
        self.convpress.wildcard_byte = b"\x12"
        self.convpress.replace_byte_for_kernel(
            byte_index = 11,
            filter_for_decompression = filter_to_use
            )
        bytestring_should_be = b"\xfd\xe8\x55\xa4\x1e?\xfda\xe8\xc9\xe8\xe8\xa4\xa4\xfd\xe8\xfd7\xa4"
        self.assertTrue(bytelist_to_bytestring(self.convpress.byte_list) == bytestring_should_be)

if __name__ == '__main__':

    # roda testes
    unittest.main()
