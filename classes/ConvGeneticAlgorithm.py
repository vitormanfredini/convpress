"""
Genetic algorhithm for finding the best combination of filters for compressing a file
"""
import random
from typing import List
from classes.ConvFilter import ConvFilter
from utils.banner import print_banner


class ConvGeneticAlgorithm:
    """Genetic Algorhithm"""

    def __init__(self):
        self.population: List[ConvFilter] = []
        self.mutation_chance = 0.05
        self.generations: List[List[ConvFilter]] = []
        self.history = []
        self.generation_scores = []

    def add_filter(self, filter_to_add: ConvFilter):
        """Adds filter"""
        self.population.append(filter_to_add)

    def set_mutation_chance(self, percentage: float) -> None:
        """Set mutation chance with value between 0.0 and 1.0"""
        self.mutation_chance = percentage

    def get_population(self) -> List[ConvFilter]:
        """get list of all filters in the current population"""
        return self.population

    def debug_population(self, list_of_filters: list = None):
        """
        prints all filters' kernels
        in the list of filters passed.
        if no argument is passed,
        then use current population.
        """

        if list_of_filters is None:
            list_of_filters = self.population

        print_banner("population debug")
        for idx, filter_to_debug in enumerate(list_of_filters):
            print(f"idx {idx}: {filter_to_debug}")

    def get_generation(self, generation: int) -> List[ConvFilter]:
        """get specific generation list of filters"""
        return self.history[generation]

    def natural_selection(self, chance_of_survival: float, scores: list):
        """Order population by individual score and remove those below chance of survival"""

        max_stay_alive = int(len(scores) * chance_of_survival)
        self.population = [x for _, x in sorted(
            zip(scores, self.population), key=lambda pair: pair[0])][-max_stay_alive:]

    def save_population(self):
        """save current population of filters in the history"""
        self.history.append(self.population.copy())

    def load_population_from_history(self, generation: int):
        """load population of filters from history"""
        self.population = self.history[generation].copy()

    def should_mutate(self):
        """random chance of mutation"""
        return random.uniform(0, 1) < self.mutation_chance

    def mutation(self, mutation_byte_list: List[bytes]):
        """Mutate one byte of the kernel"""
        for filter_to_mutate in self.population:
            if self.should_mutate():
                rand_filter_idx = random.randrange(filter_to_mutate.get_size())
                rand_byte_idx = random.randrange(len(mutation_byte_list))
                filter_to_mutate.kernel[rand_filter_idx] = mutation_byte_list[rand_byte_idx]

    def get_generation_with_best_score(self):
        """find generation with the best score"""
        index_max = 0
        max_score = 0
        for idx, score in enumerate(self.generation_scores):
            if score > max_score:
                max_score = score
                index_max = idx
        return index_max

    def get_generation_scores(self):
        """get list of the scores from all generations"""
        return self.generation_scores

    def add_generation_score(self, score: float):
        """add one generation score"""
        self.generation_scores.append(score)

    def reproduce(self, max_filters: int):
        """cross filters' kernels to produce new filters"""
        new_filters = []
        while len(new_filters) < max_filters:

            rand_idx = random.randrange(len(self.population))
            mommy = self.population[rand_idx]
            rand_idx = random.randrange(len(self.population))
            daddy = self.population[rand_idx]

            baby = mommy.crossover(daddy)
            new_filters.append(baby)

        self.population = new_filters

    def remove_duplicates(self):
        """removes duplicates from the current population"""

        without_duplicates = []
        for filter_to_check in self.population:
            if filter_to_check not in without_duplicates:
                without_duplicates.append(filter_to_check)
        self.population = without_duplicates

    def wildcard_disease(self, wildcard_byte: bytes):
        """removes all filters with a wildcard_byte as first or last byte in the kernel"""

        survivors = []
        for filter_to_check in self.population:
            kernel = filter_to_check.get_kernel()
            if kernel[0] == wildcard_byte:
                continue
            if kernel[filter_to_check.get_size()-1] == wildcard_byte:
                continue
            survivors.append(filter_to_check)
        self.population = survivors
