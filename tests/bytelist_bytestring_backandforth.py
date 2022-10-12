"""
Tests for the bytes operations functions
"""
import unittest
import sys
from utils.bytes_operations import bytestring_to_bytelist, bytelist_to_bytestring

sys.path.append("..")

class Testing(unittest.TestCase):
    """Tests the process of converting bytestrings to bytelists and vice versa"""

    def test_backandforth(self):
        """convert it to bytelist, than back to bytestring"""
        bytestring = b"\xfd\xe8r\xc9\x1e?\xfda\xe8\xc9\xa4\xb9a\xfd\xe8\xfd7\xa4"
        bytelist = bytestring_to_bytelist(bytestring)
        bytestringagain = bytelist_to_bytestring(bytelist)
        self.assertTrue(bytestring == bytestringagain)

if __name__ == '__main__':

    # roda testes
    unittest.main()
