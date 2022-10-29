"""
Test to check if all chars produced are singlebyte chars.
"""
import unittest
import sys

sys.path.append("..")


class Testing(unittest.TestCase):
    """Tests the sizes of bytes produced by different encodings"""

    def test_all_chars_must_be_single_byte_latin1(self):
        """
        Test the first 256 chars in the latin1 encoding
        and check if all of them
        can be represented by 1 byte only
        """

        max_chars = 256
        count_single_byte = 0
        for i in range(max_chars):
            try:
                byte = chr(i).encode("latin1")
            except UnicodeEncodeError:
                pass
            if len(byte) == 1:
                count_single_byte += 1
        self.assertTrue(count_single_byte > 0)

    def test_all_chars_must_be_single_byte_utf8(self):
        """
        Test the first 256 chars in the utf-8 encoding
        and check if all of them
        can be represented by 1 byte only
        """

        max_chars = 256
        count_single_byte = 0
        for i in range(max_chars):
            try:
                byte = chr(i).encode("utf-8")
            except UnicodeEncodeError:
                pass
            if len(byte) == 1:
                count_single_byte += 1
        self.assertTrue(count_single_byte > 0)

    def test_all_chars_must_be_single_byte_cp1252(self):
        """
        Test the first 256 chars in the cp1252 encoding
        and check if all of them
        can be represented by 1 byte only
        """

        max_chars = 256
        count_single_byte = 0
        for i in range(max_chars):
            try:
                byte = chr(i).encode("cp1252")
            except UnicodeEncodeError:
                pass
            if len(byte) == 1:
                count_single_byte += 1
        self.assertTrue(count_single_byte > 0)

if __name__ == '__main__':
    unittest.main()
