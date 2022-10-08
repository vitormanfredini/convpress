#!/usr/bin/env python3
from pprint import pp
import random
from numpy import interp
from arguments import parse_args_compress
from classes.ConvFilter import ConvFilter
from classes.Convpress import Convpress
from classes.ConvGeneticAlgorithm import ConvGeneticAlgorithm

def main():

    args = parse_args_compress()

    cp = Convpress()
    cp.load_file(args.input_file)
    cp.set_output_file(args.output_file)

    ga = ConvGeneticAlgorithm()

    population_fixed_size = 100
    for c in range(population_fixed_size):
        filter_size = random.randrange(2,3)
        new_filter = ConvFilter(filter_size)
        new_filter.randomize_from_list(
            unique_bytelist=cp.getByteList(),
            wildcard_chance=0.33,
            wildcard_byte=cp.get_wildcard_byte()
            )
        ga.addFilter(new_filter)

    generations = 5
    maxMutationChancePercentage = 0.1

    for g in range(generations):
        print(f"generation {g}")

        # ramp up mutation chance
        ga.set_mutation_chance( (g / generations) * maxMutationChancePercentage )

        generation_score = cp.convolve_all_and_get_generation_score(ga.getPopulation())
        ga.addGenerationScore(generation_score)
        ga.save_population()
        print(f"string coverage (%): {generation_score}")
        # cp.debugScores()

        ga.naturalSelection(
            chance_of_survival=0.5,
            scores=cp.get_current_filters_scores()
            )
        
        ga.reproduce(population_fixed_size, cp.getUniqueByteList())
        # ga.kill_duplicates()
        print('---------')
    
    generation_to_use = ga.get_generation_with_best_score()
    print(f"best generation: {generation_to_use}")
    # generation_to_use = generations - 1

    cp.compress(filters = ga.getGeneration(generation_to_use))

if __name__ == '__main__':
    main()