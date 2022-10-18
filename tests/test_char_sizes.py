"""
Test to check if all chars produced are singlebyte chars.
"""
import unittest
import sys

sys.path.append("..")


class Testing(unittest.TestCase):
    """Tests the sizes of bytes produced by different encodings"""

    def test_all_latin1_chars_must_be_single_byte(self):
        """
        Test the first 256 chars in the latin1 encoding
        and check if all of them
        can be represented by 1 byte only
        """

        max_chars = 256
        for i in range(max_chars):
            with self.subTest():
                byte = chr(i).encode("latin1")
                self.assertTrue(len(byte) == 1)


if __name__ == '__main__':

    unittest.main()
