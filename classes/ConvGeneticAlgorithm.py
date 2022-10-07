import random
from typing import List
from classes.ConvFilter import ConvFilter

class ConvGeneticAlgorithm:

    def __init__(self):
        self.population: ConvFilter = []
        self.mutation_chance = 0.05
        self.generations: List[ConvFilter] = []
        self.current_generation = 0
        self.history = []

    def addFilter(self, filter: ConvFilter):
        self.population.append(filter)

    def set_mutation_chance(self, percentage: float) -> None:
        self.mutation_chance = percentage
    
    def getPopulation(self) -> List[ConvFilter]:
        return self.population

    def debugFilters(self):
        for i in range(len(self.population)):
            filterBytes = self.population[i].getFilter()
            for c in range(len(filterBytes)):
                print(filterBytes[c],end=' ')
            print()
    
    def getGeneration(self, generation) -> List[ConvFilter]:
        return self.history[generation]
    
    def naturalSelection(self, chance_of_survival: float, scores: list):

        self.history.append(self.population.copy())

        max = 0
        for s in range(len(scores)):
            if scores[s] > max:
                max = scores[s]

        alive = []
        scoreSubtract = 0
        while len(alive) < len(scores) * chance_of_survival:
            scoreToBeAlive = max - scoreSubtract
            for c in range(len(scores)):
                if scores[c] == scoreToBeAlive:
                    alive.append(self.population[c])
            scoreSubtract += 1

        self.population = alive[0:int(len(scores) * chance_of_survival)]
        self.current_generation += 1

    def shouldMutate(self):
        randomint = random.randint(0,100000)
        return (randomint  / 100000) < self.mutation_chance

    def crossover(self, filterA: ConvFilter, filterB: ConvFilter, mutation_byte_list: list):
        
        newFilter = ConvFilter(filterA.getSize())
        newFilter.filter = filterA.filter.copy()
        
        randomSkip = 0
        sizeDiff = abs(filterA.getSize() - filterB.getSize())
        if sizeDiff > 0:
            randomSkip = random.randrange(sizeDiff)
        
        smallerSize = filterA.getSize()
        if filterB.getSize() < smallerSize:
            smallerSize = filterB.getSize()

        for c in range(smallerSize):
            if random.randrange(2) == 0:
                if filterA.getSize() > filterB.getSize():
                    newFilter.filter[randomSkip + c] = filterB.filter[c]
                else:
                    newFilter.filter[c] = filterB.filter[randomSkip + c]
        
        if self.shouldMutate():
            rand_filter_idx = random.randrange(newFilter.getSize())
            rand_byte_idx = random.randrange(len(mutation_byte_list))
            newFilter.filter[rand_filter_idx] = mutation_byte_list[rand_byte_idx]

        return newFilter

    def reproduce(self, maxFilters: int, mutation_byte_list: list):
        newFilters = []
        while len(newFilters) < maxFilters:
            
            rand_idx = random.randrange(len(self.population))
            parentA = self.population[rand_idx]
            rand_idx = random.randrange(len(self.population))
            parentB = self.population[rand_idx]
            
            babyFilter = self.crossover(parentA, parentB, mutation_byte_list)
            newFilters.append(babyFilter)

        self.population = newFilters

    def killDuplicates(self):
        withoutDuplicates = []
        for filter in self.population:
            if filter not in withoutDuplicates:
                withoutDuplicates.append(filter)
        self.population = withoutDuplicates