#!/usr/bin/env python3
"""
File compression using convolutions and a genetic algorithm the find the best filters.
"""

import random
from arguments import parse_args_compress
from classes.ByteGenerator import ByteGenerator
from classes.ConvFilter import ConvFilter
from classes.Convpress import Convpress, RepetitionPenaltyType
from classes.ConvGeneticAlgorithm import ConvGeneticAlgorithm


def main():
    """Uses genetic algorithms and convolutions to compress a file."""

    args = parse_args_compress()

    byte_generator = ByteGenerator("latin1")
    convpress = Convpress(byte_generator)
    genetic_algorithm = ConvGeneticAlgorithm()

    print(f"Loading: {args.input_file.name}")
    convpress.load_file(filename=args.input_file)

    convpress.set_output_file(output_file=args.output_file)

    convpress.set_repetition_penalty_type(RepetitionPenaltyType.DIVIDE_BY_NUMBER_OF_REPETITIONS)

    

    for _ in range(args.ps):
        filter_size = random.randrange(args.fsmin, args.fsmax+1)
        new_filter = ConvFilter(filter_size)
        new_filter.randomize_from_list(
            unique_bytelist=convpress.get_unique_bytelist(),
            wildcard_chance=0.5,
            wildcard_byte=convpress.get_wildcard_byte()
        )
        genetic_algorithm.add_filter(new_filter)

    genetic_algorithm.set_mutation_chance(percentage=args.mcp)
    generation_to_run = args.g

    for generation in range(generation_to_run):

        print(f"generation {generation}")
        # genetic_algorithm.debug_population()

        convpress.convolve_all(
            filters_to_convolve=genetic_algorithm.get_population())
        generation_score = convpress.calculate_generation_score()

        print(f"score: {generation_score}")

        genetic_algorithm.add_generation_score(score=generation_score)
        genetic_algorithm.save_population()

        if generation >= generation_to_run - 1:
            break

        genetic_algorithm.natural_selection(
            chance_of_survival=args.scp,
            scores=convpress.get_current_filters_scores()
        )

        genetic_algorithm.reproduce(max_filters=args.ps)
        genetic_algorithm.mutation(
            mutation_byte_list=convpress.get_unique_bytelist())
        genetic_algorithm.wildcard_disease(
            wildcard_byte=convpress.get_wildcard_byte())

    print('-------------------------')
    generation_with_best_score = genetic_algorithm.get_generation_with_best_score()
    print(f"best generation: {generation_with_best_score}")

    genetic_algorithm.load_population_from_history(
        generation=generation_with_best_score)
    genetic_algorithm.remove_duplicates()

    # genetic_algorithm.debug_population()

    print("Compressing...")
    filters_actually_used = convpress.compress(
        filters_to_use=genetic_algorithm.get_population())

    genetic_algorithm.debug_population(list_of_filters=filters_actually_used)

    header = convpress.generate_header(used_filters=filters_actually_used)

    convpress.output_file_from_bytelist(header=header)


if __name__ == '__main__':
    main()
