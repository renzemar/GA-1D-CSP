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
from data import df_production_orders

# Genetic Algorithm constants:
POPULATION_SIZE = 250  # The size of the population of individuals
P_CROSSOVER = 0.9  # probability for crossover
MAX_GENERATIONS = 15  # The maximum number of generations
HALL_OF_FAME_SIZE = 3  # The size of the hall of fame

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
        sanity = functions_GA.sanityCheck(order_length_quantities=order_length_quantities,
                                          population=offspring_individual)
        # nr_of_bases = functions_GA.sum_baseLength(offspring_individual[0])

        if not sanity:
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


def OptimizeDay(data_day, date):

    subsets = functions_dataprep.panel_count(data_day)
    dict_subsets = functions_dataprep.create_subsets(data_day, subsets)
    day_subsets = functions_dataprep.list_subsets(dict_subsets)
    lookup = pd.DataFrame()
    lookup['Key'] = dict_subsets.keys()

    df_results = pd.DataFrame(columns=["Subset", "O_material", "N_material", "O_waste", "N_waste", "O_panels", "N_panels"])

    for i in range(len(day_subsets)):
        subset_index = i
        order_length_quantities = day_subsets[subset_index].copy()
        analyzed_subset, O_nr_of_panels, O_waste, O_material = functions_dataprep.performance_set(data_day,
                                                                                    lookup.loc[subset_index][0])
        print(f"Performing GA iteration: {i}")
        N_waste, N_material, N_nr_of_bases = GA(order_length_quantities, subset_index)
        print(f"Optimized subset: {order_length_quantities}")
        print(
            f"-- Original Model Results on {date} = Analyzed subset: {analyzed_subset}, Total number of panels: {O_nr_of_panels}"
            f", Total material "
            f"used: {O_material}, Total waste: {O_waste}")
        print(f"Number of subsets: {len(day_subsets)}")

        subset_string = ', '.join(map(str, analyzed_subset))

        new_row = pd.DataFrame(
            {'Subset': [subset_string], 'O_material': [O_material], 'N_material': [N_material], 'O_waste': [O_waste], 'N_waste': [N_waste],
             'O_panels': [O_nr_of_panels], 'N_panels': [N_nr_of_bases]})

        df_results = pd.concat([df_results, new_row], ignore_index=True)

    return df_results


def OptimizeRange(df_production_orders, nr_of_days, days):
    df_production_orders['ProductieTijd'] = pd.to_datetime(df_production_orders['ProductieTijd'])
    df_production_orders['ProductieTijd'] = df_production_orders['ProductieTijd'].dt.date
    amount_of_days_available = len(df_production_orders['ProductieTijd'].unique())

    if amount_of_days_available < nr_of_days:
        print(f"Not enough days in the dataset. Changing nr_of_days to the number of days in the dataset: "
              f"{amount_of_days_available}")
        nr_of_days = amount_of_days_available

    if days:
        print(f"List of days is provided: {days}. Optimizing only for these days. nr_of_days is ignored.")
        input_dates = pd.to_datetime(days)
        input_dates = pd.to_datetime(input_dates).date

        results = pd.DataFrame()
        for date in input_dates:
            filtered_df = df_production_orders[df_production_orders['ProductieTijd'] == date]
            results = pd.concat([results, filtered_df])

        df_production_orders = results
        nr_of_days = len(df_production_orders['ProductieTijd'].unique())

    groups = df_production_orders.groupby("ProductieTijd")
    groups_list = [g[1] for g in list(groups)]

    for data_day in groups_list[:nr_of_days]:
        unique_bases = len(data_day['Lengte'].unique())
        date = data_day.iloc[0]['ProductieTijd']

        if unique_bases > 1:
            print(f"Performing GA iteration on: {date}")
            print('More than one base length found, skipping day')
            continue

        else:
            df_results = OptimizeDay(data_day, date)
            # Print the results
            print("Optimization complete - Results:")
            print(df_results)
            visualize_results(df_results, date)


def visualize_results(df_results, date):
    # Calculate the total values for each column
    totals = df_results.drop('Subset', axis=1).sum()

    # Define the pairs of variables to compare
    pairs = [('O_material', 'N_material'), ('O_waste', 'N_waste'), ('O_panels', 'N_panels')]

    # Create a figure with three subplots
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(12, 4))

    # Loop over the subplots and create a bar plot for each pair of variables
    for i, (var1, var2) in enumerate(pairs):
        ax = axes[i]
        values = [totals[var1], totals[var2]]
        ax.bar([var1, var2], values)
        ax.set_title(f'{var1} vs. {var2}')
        ax.set_ylabel('Total')

        # Add the precise values from totals into each bar
        for j, v in enumerate(values):
            ax.text(j, v, str(v), ha='center', va='bottom')

        # Adjust the y-limits to add extra space between the end of the bar and the boundary of the graph
        ylim_min = 0
        ylim_max = max(values) * 1.15
        ax.set_ylim(ylim_min, ylim_max)

    # Adjust the layout of the subplots and display the figure
    plt.suptitle(f"Results for {date}")
    plt.tight_layout()

    # Save the figure as a PNG file with the filename equal to the date variable
    filename = f"{date}.png"
    plt.savefig(filename)

    plt.show()


OptimizeRange(df_production_orders=df_production_orders, nr_of_days=99, days=[])
