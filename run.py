#!/usr/bin/env python3
import random

from classes.ConvFilter import ConvFilter
from classes.Convpress import Convpress
from classes.ConvGeneticAlgorithm import ConvGeneticAlgorithm

def main():

    cp = Convpress("data/output.cv")
    ga = ConvGeneticAlgorithm()

    how_many_filters = 100
    for i in range(how_many_filters):
        filter_size = random.randrange(2,4)
        new_filter = ConvFilter(filter_size)
        new_filter.randomizeFromList(cp.getByteList())
        ga.addFilter(new_filter)

    generations = 30
    maxMutationChancePercentage = 0.1

    for g in range(generations):
        print(f"generation {g}")
        ga.set_mutation_chance( (g / generations) * maxMutationChancePercentage )
        cp.convolveAll(ga.getPopulation())
        print(f"string coverage (%): {cp.get_generation_scores()[-1]}")
        # cp.debugScores()
        ga.naturalSelection(chance_of_survival=0.66, scores=cp.getScores())
        ga.reproduce(how_many_filters, cp.getUniqueByteList())
        ga.killDuplicates()
        print('---------')
    
    generation_best_score = cp.get_generation_with_best_score()
    print(f"best generation: {generation_best_score}")

    cp.compress(
        filters = ga.getGeneration(cp.get_generation_with_best_score()),
        output = "data/output2.cv"
        )
    

if __name__ == '__main__':
    main()