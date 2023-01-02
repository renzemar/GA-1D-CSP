from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import random
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import OrderedDict
import functions

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Import the test data
from data import objects, base_length

# Genetic Algorithm constants:
POPULATION_SIZE = 50
P_CROSSOVER = 0.9  # probability for crossover
MAX_GENERATIONS = 10
HALL_OF_FAME_SIZE = 1

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register('individualFunction', functions.create_individual, objects, base_length)
toolbox.register("individualCreator", tools.initRepeat, creator.Individual, toolbox.individualFunction, 1)
toolbox.register("population", tools.initRepeat, list, toolbox.individualCreator)


def crossoverFunction(ind1, ind2):
    offsprings = []

    while len(offsprings) < 2:
        offspring = functions.createOffspring(ind1[0], ind2[0])

        # create a new Individual object and set its fitness attribute
        offspring_individual = creator.Individual([offspring])

        offsprings.append(offspring_individual)

    return offsprings[0], offsprings[1]


# registering the fitness function
toolbox.register("evaluate", functions.patternsWaste)

# Tournament selection with tournament size of 3:
toolbox.register("select", tools.selRoulette)

# create operator for crossover
toolbox.register("mate", crossoverFunction)


# Genetic Algorithm flow:
def GA():
    # create initial population (generation 0):
    population = toolbox.population(n=POPULATION_SIZE)

    # prepare the statistics object:
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", np.max)
    stats.register("avg", np.mean)

    # define the hall-of-fame object:
    hof = tools.HallOfFame(HALL_OF_FAME_SIZE)

    # perform the Genetic Algorithm flow with hof feature added:
    population, logbook = algorithms.eaSimple(population, toolbox, cxpb=P_CROSSOVER, mutpb=0,
                                              ngen=MAX_GENERATIONS, stats=stats, halloffame=hof, verbose=True)

    # print best solution found:
    best = hof.items[0]
    print("-- Best Ever Individual = ", best)
    print("-- Best Ever Fitness = ", best.fitness.values[0])
    print("-- Waste of Individual = ", functions.patternsWaste(best))
    print("-- Sanity Check Of Individual = ", functions.sanityCheck(best))

    # extract statistics:
    maxFitnessValues, meanFitnessValues = logbook.select("max", "avg")

    # plot statistics:
    sns.set_style("whitegrid")
    plt.plot(maxFitnessValues, color='red')
    plt.plot(meanFitnessValues, color='green')
    plt.xlabel('Generation')
    plt.ylabel('Max / Average Fitness')
    plt.title('Max and Average fitness over Generations')
    plt.show()


GA()
