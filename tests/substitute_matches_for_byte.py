"""
Test to check if bytes are being replaced by the filters correctly
"""
import unittest
import sys
from classes.ConvFilter import ConvFilter
from classes.Convpress import Convpress
from utils.bytes_operations import bytelist_to_bytestring

sys.path.append("..")

class Testing(unittest.TestCase):
    """Tests the replacement of bytes with different filter lengths and the presence of wildcards"""

    def test_substitute_filter_length_2(self):
        """Test with length 2 filter"""

        filter_to_test = ConvFilter(2)
        filter_to_test.set_kernel_bytes_using_bytestring(b"\xfd\xe8")
        cp.load_bytelist_from_bytestring(
            b"\xfd\xe8r\xc9\x1e?\xfda\xe8\xc9\xa4\xb9a\xfd\xe8\xfd7\xa4"
            )
        cp.substitute_matches_for_newbyte(
                matches = [0,13],
                newbyte = b"\x02",
                filter_used = filter_to_test
                )
        bytestring_should_be = b"\x02r\xc9\x1e?\xfda\xe8\xc9\xa4\xb9a\x02\xfd7\xa4"
        self.assertTrue(bytelist_to_bytestring(cp.bytelist) == bytestring_should_be)

    def test_substitute_filter_length_3(self):
        """Test with length 3 filter"""

        filter_to_test = ConvFilter(3)
        filter_to_test.set_kernel_bytes_using_bytestring(b"\xe8\xc9\xa4")
        cp.load_bytelist_from_bytestring(
            b"\xfd\xe8r\xc9\x1e?\xfda\xe8\xc9\xa4\xb9a\xfd\xe8\xfd7\xa4"
            )
        cp.substitute_matches_for_newbyte(
                matches = [8],
                newbyte = b"\x07",
                filter_used = filter_to_test
                )
        bytestring_should_be = b"\xfd\xe8r\xc9\x1e?\xfda\x07\xb9a\xfd\xe8\xfd7\xa4"
        self.assertTrue(bytelist_to_bytestring(cp.bytelist) == bytestring_should_be)

    def test_substitute_filter_length_3_with_wildcard(self):
        """Test with length 3 filter with wildcard"""

        filter_to_test = ConvFilter(3)
        filter_to_test.set_kernel_bytes_using_bytestring(b"\xe8\x12\xa4")
        cp.load_bytelist_from_bytestring(
            b"\xfd\xe8\x55\xa4\x1e?\xfda\xe8\xc9\xe8\x3a\xa4\xfd\xe8\xfd7\xa4"
            )
        cp.wildcard_byte = b"\x12"
        cp.substitute_matches_for_newbyte(
                matches = [1,10],
                newbyte = b"\x07",
                filter_used = filter_to_test
                )
        bytestring_should_be = b"\xfd\x07\x55\x1e?\xfda\xe8\xc9\x07\x3a\xfd\xe8\xfd7\xa4"
        self.assertTrue(bytelist_to_bytestring(cp.bytelist) == bytestring_should_be)

if __name__ == '__main__':

    cp = Convpress()

    # roda testes
    unittest.main()
