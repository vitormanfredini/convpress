#!/usr/bin/env python3

import argparse
import sys

def parse_args_compress():
    parser = argparse.ArgumentParser(description='Compress a file using ConvPress.')
    parser.add_argument('input_file',type=argparse.FileType('rb'))
    parser.add_argument('output_file',type=argparse.FileType('wb'))
    return parser.parse_args()

def parse_args_decompress():
    parser = argparse.ArgumentParser(description='Decompress a file using ConvPress.')
    parser.add_argument('input_file',type=argparse.FileType('rb'))
    parser.add_argument('output_file',type=argparse.FileType('wb'))
    return parser.parse_args()

if __name__ == "__main__":
    pass