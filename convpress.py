#!/usr/bin/env python3
import random
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

    # generatin initial population
    for c in range(args.ps):
        filter_size = random.randrange(args.fsmin, args.fsmax+1)
        new_filter = ConvFilter(filter_size)
        new_filter.randomize_from_list(
            unique_bytelist=cp.get_unique_bytelist(),
            wildcard_chance=0.33,
            wildcard_byte=cp.get_wildcard_byte()
            )
        ga.addFilter(new_filter)

    maxMutationChancePercentage = args.mmp
    generation_to_run = args.g
    
    for g in range(generation_to_run):
        print('-------------------------')
        print(f"generation {g}")
        
        # ga.kill_duplicates()

        # ramp up mutation chance
        ga.set_mutation_chance( (g / generation_to_run) * maxMutationChancePercentage )

        generation_score = cp.convolve_all_and_get_generation_score(ga.getPopulation())
        print(f"string coverage (%): {generation_score}")
        cp.debug_scores()
        ga.add_generation_score(generation_score)
        ga.save_population()
        
        if g >= generation_to_run - 1:
            break

        ga.natural_selection(
            chance_of_survival=0.5,
            scores=cp.get_current_filters_scores()
            )
        
        ga.reproduce(maxFilters = args.ps)
        ga.mutate(mutation_byte_list = cp.get_unique_bytelist())
        
    print('-------------------------')
    generation_to_use = ga.get_generation_with_best_score()
    print(f"best generation: {generation_to_use}")

    ga.load_population_from_history(generation_to_use)
    ga.kill_duplicates()

    cp.compress(filters = ga.getPopulation())

if __name__ == '__main__':
    main()