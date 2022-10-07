#!/usr/bin/env python3
import random

from classes.ConvFilter import ConvFilter
from classes.Convpress import Convpress
from classes.ConvGeneticAlgorithm import ConvGeneticAlgorithm

def main():

    cp = Convpress()
    cp.loadFile("data/output001.cv")

    ga = ConvGeneticAlgorithm()

    max_population_size = 100
    for c in range(max_population_size):
        filter_size = random.randrange(2,5)
        new_filter = ConvFilter(filter_size)
        new_filter.randomize_from_list(cp.getByteList())
        ga.addFilter(new_filter)

    generations = 20
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

        ga.naturalSelection(chance_of_survival=0.66, scores=cp.get_current_filters_scores())
        ga.reproduce(max_population_size, cp.getUniqueByteList())
        ga.kill_duplicates()
        print('---------')
    
    generation_with_best_score = ga.get_generation_with_best_score()
    print(f"best generation: {generation_with_best_score}")

    cp.compress(
        filters = ga.getGeneration(generation_with_best_score),
        output = "data/output002.cv"
        )
    

if __name__ == '__main__':
    main()