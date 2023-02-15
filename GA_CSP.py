import pandas as pd
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
from data import list_subsets, basePanels, lookup, df_orders

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


def crossoverFunction(ind1, ind2, order_length_quantities):
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
        offspring = functions_GA.createOffspring(ind1[0], ind2[0], order_length_quantities=order_length_quantities)

        # create a new Individual object and set its fitness attribute
        offspring_individual = creator.Individual([offspring])

        offsprings.append(offspring_individual)

        # Sanity check
        sanity = functions_GA.sanityCheck(order_length_quantities=order_length_quantities, population=offspring_individual)
        nr_of_bases = functions_GA.sum_baseLength(offspring_individual[0])

        if not sanity and nr_of_bases < basePanels:
            print('False offspring created')

    return offsprings[0], offsprings[1]


def create_toolbox(order_length_quantities):
    # Initialize the toolbox
    toolbox = base.Toolbox()

    # Register the "individualFunction" function in the toolbox
    # This function creates an individual by calling the "create_individual" function from the "functions" module
    # It takes in the "objects" and "base_length" data as arguments
    toolbox.register('individualFunction', functions_GA.create_individual,
                     order_length_quantities=order_length_quantities)

    # Register the "individualCreator" function in the toolbox This function creates an individual by calling the
    # "individualFunction" and using the "initRepeat" function from the "tools" module The created individual is
    # initialized with the "Individual" class and is repeated once
    toolbox.register("individualCreator", tools.initRepeat, creator.Individual, toolbox.individualFunction, 1)

    # Register the "population" function in the toolbox This function creates a population of individuals by calling the
    # "individualCreator" function and using the "initRepeat" function from the "tools" module The created population is
    # initialized as a list and has a length of POPULATION_SIZE
    toolbox.register("population", tools.initRepeat, list, toolbox.individualCreator)

    # registering the fitness function
    toolbox.register("evaluate", functions_GA.individualWaste, order_length_quantities=order_length_quantities)

    # Roulette selection
    toolbox.register("select", tools.selRoulette)

    # Create operator for crossover
    toolbox.register("mate", crossoverFunction, order_length_quantities=order_length_quantities)

    return toolbox


@functions_GA.measure_time
def GA(order_length_quantities, subset_index):
    """
    This is the main Genetic Algorithm function which performs the flow of the algorithm and plots the statistics of the
    fitness values.

    Returns:
        None
    """
    # Measure time
    time.sleep(1)

    # Create the toolbox
    toolbox = create_toolbox(order_length_quantities=order_length_quantities)

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
        sanity = functions_GA.sanityCheck(order_length_quantities=order_length_quantities, population=solution)

        if sanity:
            best = solution
            break
        else:
            print('Invalid solution found')

    if best is None:
        print('No valid solution found')
        return

    # Define the best individuals' characteristics
    N_nr_of_bases = functions_GA.sum_baseLength(best[0])
    nr_of_patters = len(best[0])

    # Use this for when using fitness function of minimal waste
    # waste = functions_GA.individualWaste(best, order_length_quantities=objects)
    # base_panel_material = nr_of_bases * 12450
    # material_used = waste[0] + base_panel_material

    # Use this for when using fitness function of minimal waste
    N_waste = functions_GA.CalcWaste(best, order_length_quantities=order_length_quantities)
    N_material = best.fitness.values[0]

    # Perform again if solution is invalid, this is a temporary fix
    # if not sanity and nr_of_bases < basePanels:
    #    print("-- Best Ever Individual = ", best)
    #    print('Invalid solution found, performing again')
    #    GA()
    #    return None

    # Print the best individual's characteristics
    print("-- Best Ever Individual = ", best)
    print("-- Best Ever Fitness (Material used) = ", N_material)
    print("-- Total Waste = ", N_waste)
    print("-- Number of Base Lengths = ", N_nr_of_bases)
    print("-- Number of Patterns = ", nr_of_patters)
    print("-- Sanity Check of Individual = ", sanity)

    # Extract the statistics
    # minFitnessValues, meanFitnessValues = logbook.select("min", "avg")

    # Plot the statistics
    # sns.set_style("whitegrid")
    # plt.plot(minFitnessValues, color='red')
    # plt.plot(meanFitnessValues, color='green')
    # plt.xlabel('Generation')
    # plt.ylabel('Min / Average Fitness')
    # plt.title('Min and Average fitness over Generations')
    # plt.show()

    return N_waste, N_material, N_nr_of_bases


def loop():

    df_results = pd.DataFrame(columns=["O_material", "N_material", "O_waste", "N_waste", "O_panels", "N_panels"])

    for i in range(len(list_subsets)):
        subset_index = i
        order_length_quantities = list_subsets[subset_index].copy()
        k, O_nr_of_panels, O_waste, O_material = functions_dataprep.performance_set(df_orders, lookup.loc[subset_index][0])
        print(f"Performing GA iteration: {i}")
        N_waste, N_material, N_nr_of_bases = GA(order_length_quantities, subset_index)
        print(f"Optimized subset: {order_length_quantities}")
        print(
            f"-- Original Model Results = Analyzed subset: {k}, Total number of panels: {O_nr_of_panels}, Total material "
            f"used: {O_material}, Total waste: {O_waste}")
        print(f"Number of subsets: {len(list_subsets)}")

        new_row = pd.DataFrame(
            {'O_material': [O_material], 'N_material': [N_material], 'O_waste': [O_waste], 'N_waste': [N_waste],
             'O_panels': [O_nr_of_panels], 'N_panels': [N_nr_of_bases]})

        df_results = pd.concat([df_results, new_row], ignore_index=True)

    return df_results


df_results = loop()


print("Optimization complete - Results:")
print(df_results)

# Calculate the total values for each column
totals = df_results.sum()

# Define the pairs of variables to compare
pairs = [('O_material', 'N_material'), ('O_waste', 'N_waste'), ('O_panels', 'N_panels')]

# Create a figure with three subplots
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(12, 4))

# Loop over the subplots and create a bar plot for each pair of variables
for i, (var1, var2) in enumerate(pairs):
    ax = axes[i]
    ax.bar([var1, var2], [totals[var1], totals[var2]])
    ax.set_title(f'{var1} vs. {var2}')
    ax.set_ylabel('Total')

# Adjust the layout of the subplots and display the figure
plt.tight_layout()
plt.show()



