from typing import List

def bytestring_to_bytelist(bytestring: bytes):
    bytelist = []
    for idx in range(len(bytestring)):
        bytelist.append(bytestring[idx:idx+1])
    return bytelist

def bytelist_to_bytestring(bytelist: List[bytes]):
    bytestring = b""
    for idx in range(len(bytelist)):
        bytestring += bytelist[idx]
    return bytestring