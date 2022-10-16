#!/usr/bin/env python3
"""
Program to decompress a file that was compressed by convpress.
"""

from arguments import parse_args_decompress
from classes.Convpress import Convpress

def main():
    """Decompresses a file that was compressed by convpress."""

    args = parse_args_decompress()

    convpress = Convpress()
    convpress.load_file_for_decompression(args.input_file)
    convpress.set_output_file(args.output_file)
    print("Decompressing...")
    convpress.decompress()
    convpress.output_file_from_bytelist()

if __name__ == '__main__':
    main()
