#!/usr/bin/env python3
"""
Programa de compressão de arquivos.
"""

import random
from arguments import parse_args_compress
from classes.ConvFilter import ConvFilter
from classes.Convpress import Convpress
from classes.ConvGeneticAlgorithm import ConvGeneticAlgorithm

def main():
    """Uses genetic algorithms and convolutions to compress a file."""

    args = parse_args_compress()

    convpress = Convpress()
    print(f"Loading: {args.input_file.name}")
    convpress.load_file(args.input_file)
    convpress.set_output_file(args.output_file)

    genetic_algorithm = ConvGeneticAlgorithm()

    print('-------------------------')

    for _ in range(args.ps):
        filter_size = random.randrange(args.fsmin, args.fsmax+1)
        new_filter = ConvFilter(filter_size)
        new_filter.randomize_from_list(
            unique_bytelist=convpress.get_unique_bytelist(),
            wildcard_chance=0.33,
            wildcard_byte=convpress.get_wildcard_byte()
            )
        genetic_algorithm.add_filter(new_filter)

    genetic_algorithm.set_mutation_chance(args.mcp)
    generation_to_run = args.g

    for generation in range(generation_to_run):

        convpress.convolve_all(filters_to_convolve = genetic_algorithm.get_population())
        generation_score = convpress.calculate_generation_score()
        print(f"generation {generation} score: {generation_score}")
        # cp.debug_scores()

        genetic_algorithm.add_generation_score(generation_score)
        genetic_algorithm.save_population()

        if generation >= generation_to_run - 1:
            break

        genetic_algorithm.natural_selection(
            chance_of_survival=0.5,
            scores=convpress.get_current_filters_scores()
            )

        genetic_algorithm.reproduce(max_filters = args.ps)
        genetic_algorithm.mutation(mutation_byte_list = convpress.get_unique_bytelist())

    print('-------------------------')
    generation_to_use = genetic_algorithm.get_generation_with_best_score()
    print(f"best generation: {generation_to_use}")

    genetic_algorithm.load_population_from_history(generation_to_use)
    genetic_algorithm.kill_duplicates()

    print("Compressing...")
    convpress.compress(filters = genetic_algorithm.get_population())

if __name__ == '__main__':
    main()
