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
    """Tests the replacement filter kernel with all possible single bytes in the encoding"""

    convpress: Convpress = None
    all_possible_bytes: bytes = []

    def setUp(self) -> None:
        self.convpress = Convpress()
        max_chars = 256
        for i in range(max_chars):
            self.all_possible_bytes.append(chr(i).encode(self.convpress.encoding))
        return super().setUp()

    def test_replace_filter_length_2(self):
        """Test replacing filter for all possible bytes"""

        for byte_idx, test_byte in enumerate(self.all_possible_bytes):
            with self.subTest(str(byte_idx)+ " " + str(test_byte)):
                kernel_bytestring = b"\xfd\xe8"
                bytestring_before = b"\xfd\xe8r\xc9\x1e?\xfda\xe8\xc9\xa4\xb9a\xfd\xe8\xfd7\xa4"
                bytestring_should_be = test_byte + b"r\xc9\x1e?\xfda\xe8\xc9\xa4\xb9a" + test_byte + b"\xfd7\xa4"
                matches_indexes = [0,13]

                filter_to_test = ConvFilter(len(kernel_bytestring))
                filter_to_test.set_kernel_bytes_using_bytestring(kernel_bytestring)
                filter_to_test.set_byte_it_represents(test_byte)
                self.convpress.load_bytelist_from_bytestring(bytestring_before)
                self.convpress.replace_matches_for_newbyte(
                        matches = matches_indexes,
                        filter_used = filter_to_test
                        )

                # print(f"idx: {byte_idx}")
                # print("test_byte:")
                # print(test_byte)
                # print("filter kernel:")
                # print(kernel_bytestring)
                # print("before:")
                # print(bytestring_before)
                # print("after:")
                # print(bytelist_to_bytestring(self.convpress.bytelist))
                # print("should be:")
                # print(bytestring_should_be)
                # print(bytelist_to_bytestring(self.convpress.bytelist) == bytestring_should_be)
                # print('------------')
                self.assertTrue(bytelist_to_bytestring(self.convpress.bytelist) == bytestring_should_be)

if __name__ == '__main__':

    unittest.main()
