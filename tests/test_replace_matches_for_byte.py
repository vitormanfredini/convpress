"""
Test to check if matches are being replaced by the compression byte correctly
"""
import unittest
import sys
from classes.ConvFilter import ConvFilter
from classes.Convpress import Convpress
from utils.bytes_operations import bytelist_to_bytestring

sys.path.append("..")

class Testing(unittest.TestCase):
    """Tests the replacement of bytes with different filter lengths and the presence of wildcards"""

    convpress: Convpress = None

    def setUp(self) -> None:
        self.convpress = Convpress()
        return super().setUp()

    def test_replace_filter_length_2(self):
        """Test with length 2 filter"""

        filter_to_test = ConvFilter(2)
        filter_to_test.set_kernel_bytes_using_bytestring(b"\xfd\xe8")
        filter_to_test.set_byte_it_represents(b"\x02")
        self.convpress.load_bytelist_from_bytestring(
            b"\xfd\xe8r\xc9\x1e?\xfda\xe8\xc9\xa4\xb9a\xfd\xe8\xfd7\xa4"
            )
        self.convpress.replace_matches_for_newbyte(
                matches = [0,13],
                filter_used = filter_to_test
                )
        bytestring_should_be = b"\x02r\xc9\x1e?\xfda\xe8\xc9\xa4\xb9a\x02\xfd7\xa4"
        self.assertTrue(bytelist_to_bytestring(self.convpress.bytelist) == bytestring_should_be)

    def test_replace_filter_length_3(self):
        """Test with length 3 filter"""

        filter_to_test = ConvFilter(3)
        filter_to_test.set_kernel_bytes_using_bytestring(b"\xe8\xc9\xa4")
        filter_to_test.set_byte_it_represents(b"\x07")
        self.convpress.load_bytelist_from_bytestring(
            b"\xfd\xe8r\xc9\x1e?\xfda\xe8\xc9\xa4\xb9a\xfd\xe8\xfd7\xa4"
            )
        self.convpress.replace_matches_for_newbyte(
                matches = [8],
                filter_used = filter_to_test
                )
        bytestring_should_be = b"\xfd\xe8r\xc9\x1e?\xfda\x07\xb9a\xfd\xe8\xfd7\xa4"
        self.assertTrue(bytelist_to_bytestring(self.convpress.bytelist) == bytestring_should_be)

    def test_replace_filter_length_3_with_wildcard(self):
        """Test with length 3 filter with wildcard"""

        filter_to_test = ConvFilter(3)
        filter_to_test.set_kernel_bytes_using_bytestring(b"\xe8\x12\xa4")
        filter_to_test.set_byte_it_represents(b"\x07")
        self.convpress.load_bytelist_from_bytestring(
            b"\xfd\xe8\x55\xa4\x1e?\xfda\xe8\xc9\xe8\x3a\xa4\xfd\xe8\xfd7\xa4"
            )
        self.convpress.wildcard_byte = b"\x12"
        self.convpress.replace_matches_for_newbyte(
                matches = [1,10],
                filter_used = filter_to_test
                )
        bytestring_should_be = b"\xfd\x07\x55\x1e?\xfda\xe8\xc9\x07\x3a\xfd\xe8\xfd7\xa4"
        self.assertTrue(bytelist_to_bytestring(self.convpress.bytelist) == bytestring_should_be)

    def test_length_after_replacing_with_filter_length_3(self):
        """Test if length is the correct one after replacing the matches for the byte"""

        filter_to_test = ConvFilter(3)
        filter_to_test.set_kernel_bytes_using_bytestring(b"\x2f\xaa\xab")
        self.convpress.wildcard_byte = b"\xaa"
        filter_to_test.set_byte_it_represents(b"\x07")
        input_byte_string = b"\xe8\x12\xa4\x2f\xa1\xab\x3e\x61\x2f\xa2\xab\xe8\x12\xa4\x2f\xa3\xab\x3e\x61\xff"
        self.convpress.load_bytelist_from_bytestring(input_byte_string)
        matches = self.convpress.convolve(filter_to_test)
        self.convpress.replace_matches_for_newbyte(
                matches = matches,
                filter_used = filter_to_test
                )
        kernel_size_without_wildcards = filter_to_test.get_size() - len(filter_to_test.get_wildcards_indexes(self.convpress.wildcard_byte))
        should_be_this_length = len(input_byte_string) - (len(matches) * (kernel_size_without_wildcards - 1))
        self.assertTrue(len(self.convpress.bytelist) == should_be_this_length)

    def test_length_after_replacing_with_filter_length_2(self):
        """Test if length is the correct one after replacing the matches for the byte"""

        filter_to_test = ConvFilter(2)
        filter_to_test.set_kernel_bytes_using_bytestring(b"\x11\xff")
        self.convpress.wildcard_byte = b"\x00"
        filter_to_test.set_byte_it_represents(b"\xdc")
        input_byte_string = b"\x11\xff\x11\xff\x11\xff\xbb\xe7\x11\xff\xdd\xda\x11\xff\xbd\x11\xff\x11\xff\xaa"
        self.convpress.load_bytelist_from_bytestring(input_byte_string)
        matches = self.convpress.convolve(filter_to_test)
        self.convpress.replace_matches_for_newbyte(
                matches = matches,
                filter_used = filter_to_test
                )
        kernel_size_without_wildcards = filter_to_test.get_size() - len(filter_to_test.get_wildcards_indexes(self.convpress.wildcard_byte))
        should_be_this_length = len(input_byte_string) - (len(matches) * (kernel_size_without_wildcards - 1))
        self.assertTrue(len(self.convpress.bytelist) == should_be_this_length)

if __name__ == '__main__':

    unittest.main()
