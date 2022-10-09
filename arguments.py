#!/usr/bin/env python3

import argparse
import sys

def add_common_args(parser: argparse.ArgumentParser):
    pass

def parse_args_compress():
    parser = argparse.ArgumentParser(description='Compress a file using ConvPress.')
    parser.add_argument('input_file',type=argparse.FileType('rb'))
    parser.add_argument('output_file',type=argparse.FileType('wb'))
    parser.add_argument('--ps', '--population_size', type=int,
                    default=50, help='max number of filters in each generation'
                    )
    parser.add_argument('--g', '--generations', type=int,
                    default=10, help='how many generations to run in search for better filters',
                    )
    parser.add_argument('--fsmin', '--filter_size_min', type=int,
                    default=2, help='minimum filter size to use',
                    )
    parser.add_argument('--fsmax', '--filter_size_max', type=int,
                    default=3, help='maximum filter size to use',
                    )
    parser.add_argument('--mmp', '--max_mutation_percentage', type=float,
                    default=0.05, help='maximum mutation percentage to use',
                    )
    return parser.parse_args()

def parse_args_decompress():
    parser = argparse.ArgumentParser(description='Decompress a file using ConvPress.')
    parser.add_argument('input_file',type=argparse.FileType('rb'))
    parser.add_argument('output_file',type=argparse.FileType('wb'))
    return parser.parse_args()

if __name__ == "__main__":
    pass