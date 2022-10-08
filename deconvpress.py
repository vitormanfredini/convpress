#!/usr/bin/env python3
from pprint import pp
import random
from arguments import parse_args_decompress
from classes.ConvFilter import ConvFilter
from classes.Convpress import Convpress
from classes.ConvGeneticAlgorithm import ConvGeneticAlgorithm

def main():
    
    args = parse_args_decompress()

    cp = Convpress()
    cp.load_file_for_decompression(args.input_file)
    cp.set_output_file(args.output_file)
    cp.decompress()

if __name__ == '__main__':
    main()