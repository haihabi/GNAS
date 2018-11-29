import numpy as np
from random import choices
from gnas.search_space.search_space import SearchSpace
from gnas.search_space.cross_over import individual_uniform_crossover
from gnas.search_space.mutation import individual_flip_mutation


def genetic_algorithm_searcher(search_space: SearchSpace, population_size=10, n_generation=15, elitism=True):
    def population_initializer(p_size):
        return search_space.generate_population(p_size)

    def mutation_function(x):
        return individual_flip_mutation(x, 1 / 50)

    def cross_over_function(x0, x1):
        return individual_uniform_crossover(x0, x1)

    def selection_function(p):
        couples = choices(population=list(range(population_size)), weights=p,
                          k=2 * population_size)
        return np.reshape(np.asarray(couples), [-1, 2])

    return GeneticAlgorithms(population_initializer, mutation_function, cross_over_function, selection_function,
                             min_objective=True, n_generation=n_generation, population_size=population_size,
                             elitism=elitism)


class GeneticAlgorithms(object):
    def __init__(self, population_initializer, mutation_function, cross_over_function, selection_function,
                 population_size=20, n_generation=100, min_objective=False,
                 elitism=False):
        self.population_initializer = population_initializer
        self.mutation_function = mutation_function
        self.cross_over_function = cross_over_function
        self.selection_function = selection_function
        self.elitism = elitism
        self.population_size = population_size
        self.n_generation = n_generation
        self.i = 0
        self.g_index = 0
        self.population = None
        self.population_fitness = None
        self.min_objective = min_objective
        self._init_population()

    # def __iter__(self):
    #     return self
    #
    # def __next__(self):
    #     if self.g_index < self.n_generation:
    #         if (self.i % self.population_size) == 0 and self.i != 0:
    #             self._update_population()
    #         current_individuals = self.population[self.i % self.population_size]
    #         self.i += 1
    #         return current_individuals
    #     else:  # finished all generations
    #         raise StopIteration

    def _init_population(self):
        self.population = self.population_initializer(self.population_size)
        self.population_fitness = np.nan * np.ones(self.population_size)

    def _update_population(self):
        print("Update population")

        best_individual = self.population[np.nanargmax(self.population_fitness)]
        p = self.population_fitness / np.nansum(self.population_fitness)
        p[np.isnan(p)] = 0
        if self.min_objective == True:
            p = 1 - p
            best_individual = self.population[np.nanargmin(self.population_fitness)]

        couples = self.selection_function(p)  # selection
        child = [self.cross_over_function(self.population[c[0]], self.population[c[1]]) for c in couples]  # cross-over
        self.population = np.asarray([self.mutation_function(c) for c in child])  # mutation
        self.population_fitness = np.nan * np.ones(self.population_size)  # clear fitness results
        if self.elitism:
            best_index = np.random.random_integers(0, self.population_size - 1)
            self.population[best_index] = best_individual
        # update generation index and individual index
        self.i = 0
        self.g_index += 1

    def get_current_individual(self):
        if (self.i % self.population_size) == 0 and self.i != 0:
            self._update_population()
        current_individuals = self.population[self.i % self.population_size]
        self.i += 1
        return current_individuals

    def update_current_individual_fitness(self, individual_fitness):
        self.population_fitness[(self.i - 1) % self.population_size] = individual_fitness

    def sample_child(self):
        couple = np.random.randint(0, self.population_size, 2)
        child = self.cross_over_function(self.population[couple[0]], self.population[couple[1]])
        return self.mutation_function(child)
