from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import functions_GA
import functions_dataprep
import time

# Import the test data
from data import objects, basePanels, lookup, subset_index, df_orders

# Genetic Algorithm constants:
POPULATION_SIZE = 100  # The size of the population of individuals
P_CROSSOVER = 0.9  # probability for crossover
MAX_GENERATIONS = 15  # The maximum number of generations
HALL_OF_FAME_SIZE = 5  # The size of the hall of fame

# Create the "FitnessMin" fitness class using the base Fitness class
# Weights are set to -1.0 because we want to minimize the fitness function
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

# Create the "Individual" class, which inherits from list and has a fitness attribute
# The fitness attribute is of type "FitnessMin"
creator.create("Individual", list, fitness=creator.FitnessMin)

# Initialize the toolbox
toolbox = base.Toolbox()

# Register the "individualFunction" function in the toolbox
# This function creates an individual by calling the "create_individual" function from the "functions" module
# It takes in the "objects" and "base_length" data as arguments
toolbox.register('individualFunction', functions_GA.create_individual, order_length_quantities=objects)

# Register the "individualCreator" function in the toolbox This function creates an individual by calling the
# "individualFunction" and using the "initRepeat" function from the "tools" module The created individual is
# initialized with the "Individual" class and is repeated once
toolbox.register("individualCreator", tools.initRepeat, creator.Individual, toolbox.individualFunction, 1)

# Register the "population" function in the toolbox This function creates a population of individuals by calling the
# "individualCreator" function and using the "initRepeat" function from the "tools" module The created population is
# initialized as a list and has a length of POPULATION_SIZE
toolbox.register("population", tools.initRepeat, list, toolbox.individualCreator)


def crossoverFunction(ind1, ind2):
    """
    This function creates offspring from two parent individuals by calling the `createOffspring` function and passing in
    the patterns of the parent individuals as arguments. It then creates new `Individual` objects using the offspring
    patterns and sets their fitness attributes.

    Parameters:
    ind1 (Individual): The first parent individual.
    ind2 (Individual): The second parent individual.

    Returns:
        tuple: A tuple containing the two offspring `Individual` objects.
    """
    offsprings = []

    while len(offsprings) < 2:
        offspring = functions_GA.createOffspring(ind1[0], ind2[0], order_length_quantities=objects)

        # create a new Individual object and set its fitness attribute
        offspring_individual = creator.Individual([offspring])

        offsprings.append(offspring_individual)

        # Sanity check
        sanity = functions_GA.sanityCheck(order_length_quantities=objects, population=offspring_individual)
        nr_of_bases = functions_GA.sum_baseLength(offspring_individual[0])

        if not sanity and nr_of_bases < basePanels:
            print('False offspring created')

    return offsprings[0], offsprings[1]


# registering the fitness function
toolbox.register("evaluate", functions_GA.individualWaste, order_length_quantities=objects)


# Roulette selection
toolbox.register("select", tools.selRoulette)

# Create operator for crossover
toolbox.register("mate", crossoverFunction)


@functions_GA.measure_time
def GA():
    """
    This is the main Genetic Algorithm function which performs the flow of the algorithm and plots the statistics of the
    fitness values.

    Returns:
        None
    """
    # Measure time
    time.sleep(1)

    # Create the initial population (generation 0)
    population = toolbox.population(n=POPULATION_SIZE)

    # Prepare the statistics object
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", np.min)
    stats.register("avg", np.mean)

    # Define the hall-of-fame object
    hof = tools.HallOfFame(HALL_OF_FAME_SIZE)

    # Perform the Genetic Algorithm flow with the hof feature added
    population, logbook = algorithms.eaSimple(population, toolbox, cxpb=P_CROSSOVER, mutpb=0,
                                              ngen=MAX_GENERATIONS, stats=stats, halloffame=hof, verbose=True)

    # Print the best solution found
    best = hof.items[0]

    # Print the best solution found
    for solution in hof.items:
        sanity = functions_GA.sanityCheck(order_length_quantities=objects, population=solution)

        if sanity:
            best = solution
            print('Valid solution found')
            break
        else:
            print('Invalid solution found')

    if best is None:
        print('No valid solution found')
        return

    # Define the best individuals' characteristics
    nr_of_bases = functions_GA.sum_baseLength(best[0])
    nr_of_patters = len(best[0])

    # Use this for when using fitness function of minimal waste
    # waste = functions_GA.individualWaste(best, order_length_quantities=objects)
    # base_panel_material = nr_of_bases * 12450
    # material_used = waste[0] + base_panel_material

    # Use this for when using fitness function of minimal waste
    material_used = functions_GA.individualWaste(best, order_length_quantities=objects)
    base_panel_material = nr_of_bases * 12450
    waste = material_used[0] - base_panel_material

    # Perform again if solution is invalid, this is a temporary fix
    # if not sanity and nr_of_bases < basePanels:
    #    print("-- Best Ever Individual = ", best)
    #    print('Invalid solution found, performing again')
    #    GA()
    #    return None

    # Print the best individual's characteristics
    print("-- Best Ever Individual = ", best)
    print("-- Best Ever Fitness = ", best.fitness.values[0])
    print("-- Total Waste = ", waste)
    print("-- Total Material Used = ", material_used)
    print("-- Number of Base Lengths = ", nr_of_bases)
    print("-- Number of Patterns = ", nr_of_patters)
    print("-- Sanity Check of Individual = ", sanity)
    print(functions_dataprep.performance_set(df_orders, lookup.loc[subset_index][0]))

    # Extract the statistics
    minFitnessValues, meanFitnessValues = logbook.select("min", "avg")

    # Plot the statistics
    sns.set_style("whitegrid")
    plt.plot(minFitnessValues, color='red')
    plt.plot(meanFitnessValues, color='green')
    plt.xlabel('Generation')
    plt.ylabel('Min / Average Fitness')
    plt.title('Min and Average fitness over Generations')
    plt.show()


GA()

