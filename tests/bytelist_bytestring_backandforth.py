import sys
sys.path.append("..")

import unittest

from utils.bytes_operations import bytestring_to_bytelist, bytelist_to_bytestring

class Testing(unittest.TestCase):

    def test_backandforth(self):
        bytestring = b"\xfd\xe8r\xc9\x1e?\xfda\xe8\xc9\xa4\xb9a\xfd\xe8\xfd7\xa4"
        bytelist = bytestring_to_bytelist(bytestring)
        bytestringagain = bytelist_to_bytestring(bytelist)
        self.assertTrue(bytestring == bytestringagain)
    
if __name__ == '__main__':

    # roda testes
    unittest.main()
