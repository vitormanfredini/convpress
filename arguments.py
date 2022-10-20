"""
command line arguments for compression and decompression
"""

import argparse


def parse_args_compress():
    """command line arguments for compression"""
    parser = argparse.ArgumentParser(
        description='Compress a file using ConvPress.')
    parser.add_argument('input_file', type=argparse.FileType('rb'))
    parser.add_argument('output_file', type=argparse.FileType('wb'))
    parser.add_argument('--ps', '--population_size', type=int,
                        default=75, help='max number of filters in each generation'
                        )
    parser.add_argument('--g', '--generations', type=int,
                        default=25, help='how many generations to run',
                        )
    parser.add_argument('--fsmin', '--filter_size_min', type=int,
                        default=2, help='minimum filter',
                        )
    parser.add_argument('--fsmax', '--filter_size_max', type=int,
                        default=3, help='maximum filter',
                        )
    parser.add_argument('--mcp', '--mutation_chance_percentage', type=float,
                        default=0.15, help='percentage of filters that will suffer mutation',
                        )
    parser.add_argument('--scp', '--survival_chance_percentage', type=float,
                        default=0.5, help='percentage of filters that survive in each generation (based on their scores).',
                        )
    return parser.parse_args()


def parse_args_decompress():
    """command line arguments for decompression"""
    parser = argparse.ArgumentParser(
        description='Decompress a file using ConvPress.')
    parser.add_argument('input_file', type=argparse.FileType('rb'))
    parser.add_argument('output_file', type=argparse.FileType('wb'))
    return parser.parse_args()


if __name__ == "__main__":
    pass
