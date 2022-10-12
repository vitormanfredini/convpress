"""
Genetic algorhithm for finding the best combination of filters for compressing a file
"""
import random
from typing import List
from classes.ConvFilter import ConvFilter

class ConvGeneticAlgorithm:
    """Genetic Algorhithm"""

    def __init__(self):
        self.population: ConvFilter = []
        self.mutation_chance = 0.05
        self.generations: List[ConvFilter] = []
        self.history = []
        self.generation_scores = []

    def addFilter(self, filter_to_add: ConvFilter):
        """Adds filter"""
        self.population.append(filter_to_add)

    def set_mutation_chance(self, percentage: float) -> None:
        """Set mutation chance with value between 0.0 and 1.0"""
        self.mutation_chance = percentage

    def get_population(self) -> List[ConvFilter]:
        return self.population

    def debugFilters(self):
        for i in range(len(self.population)):
            kernel = self.population[i].get_kernel()
            for c in range(len(kernel)):
                print(kernel[c],end=' ')
            print()
    
    def getGeneration(self, generation: int) -> List[ConvFilter]:
        return self.history[generation]
    
    def natural_selection(self, chance_of_survival: float, scores: list):
        """Order population by individual score and remove those below chance of survival"""

        max_stay_alive = int(len(scores) * chance_of_survival)
        self.population = [x for _, x in sorted(zip(scores, self.population), key=lambda pair: pair[0])][-max_stay_alive:]
    
    def save_population(self):
        self.history.append(self.population.copy())
    
    def load_population_from_history(self, generation: int):
        self.population = self.history[generation].copy()

    def should_mutate(self):
        randomint = random.randint(0,100000)
        return (randomint  / 100000) < self.mutation_chance

    def mutate(self, mutation_byte_list: List[bytes]):
        for filter in self.population:
            if self.should_mutate():
                rand_filter_idx = random.randrange(filter.get_size())
                rand_byte_idx = random.randrange(len(mutation_byte_list))
                filter.kernel[rand_filter_idx] = mutation_byte_list[rand_byte_idx]
    
    def get_generation_with_best_score(self):
        indexMax = 0
        maxScore = 0
        for idx, score in enumerate(self.generation_scores):
            if score > maxScore:
                maxScore = score
                indexMax = idx
        return indexMax

    def get_generation_scores(self):
        return self.generation_scores
    
    def add_generation_score(self, score: float):
        self.generation_scores.append(score)

    def reproduce(self, maxFilters: int):
        newFilters = []
        while len(newFilters) < maxFilters:
            
            rand_idx = random.randrange(len(self.population))
            parentA = self.population[rand_idx]
            rand_idx = random.randrange(len(self.population))
            parentB = self.population[rand_idx]
            
            babyFilter = parentA.crossover(parentB)
            newFilters.append(babyFilter)

        self.population = newFilters

    def kill_duplicates(self):
        withoutDuplicates = []
        for filter in self.population:
            if filter not in withoutDuplicates:
                withoutDuplicates.append(filter)
        self.population = withoutDuplicates