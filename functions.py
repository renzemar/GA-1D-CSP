import numpy as np
import random


objects = {4: 300, 6: 220, 3: 400, 5: 280}
base_length = 15


def sanityCheck(population):
    sanity = []
    total = 0

    for individual in population:
        for pattern in individual:
            x = pattern[1:]
            total += sum(x) * pattern[0]

        if total == 50:
            sanity += ['True']
        else:
            sanity += [total]

        total = 0

    return sanity


def subtract_lists(list1, list2):
    """
    This function subtracts the elements of arr2 from arr1, until the result is non negative. It returns a new list with
    the number of times arr2 was subtracted from arr1 as the first element, followed by the resulting list.

    Parameters:
        list1 (list): The list to subtract from.
        list2 (list): The list to subtract.

    Returns:
        list: A new list with the number of times list2 was subtracted from arr1 as the first element,
        followed by the resulting list.
    """
    # Initialize the count of how many times list2 has been subtracted from list1
    pattern_count = 1  # already substracted once from demand

    # Make sure the lists have the same length
    if len(list1) != len(list2):
        # print("Unequal lists")
        return None

    # Subtract list2 from list1 until the result is non negative
    while all(x - y >= 0 for x, y in zip(list1, list2)):
        list1 = [x - y for x, y in zip(list1, list2)]
        # print(f"{'list1 (demand) in loop'}: {list1}")
        pattern_count += 1

        ## For some reason pattern with 0 items is allowed in the population

    # Create the result list and insert the pattern count as the first element
    result = list1
    result.insert(0, pattern_count)

    # print(f"{'list1 (demand) result'}: {list1}")

    return result


def demand_length(sorted_objects):
    # Calculate the demand for each type of object
    demand = list(sorted_objects.values())

    # Sort the objects in descending order by length
    length = list(sorted_objects.keys())

    return demand, length


def sort_rer_one(objects):
    sorted_objects = dict(sorted(objects.items(), reverse=True))

    demand, length = demand_length(sorted_objects)

    return demand, length


def sort_rer_two(objects):
    # Shuffle the objects randomly
    l = list(objects.items())
    random.shuffle(l)
    shuffled_objects = dict(l)

    demand, length = demand_length(shuffled_objects)

    return demand, length


def create_list_of_zeros(length):
    empty_pattern = [0] * length
    return empty_pattern


def calc_total_length(lengths, pattern):
    total_length = 0

    for i, val in enumerate(pattern):
        # print(f"{'i'}: {i}")
        # print(f"{'val'}: {val}")
        if i == 0:
            continue
        # print(f"{'object i'}: {sorted_objects[i-1]}")
        total_length += lengths[i - 1] * val

    # print(f"{'total length'}: {total_length}")

    return total_length


def zip_individual(individual):
    # Create a new list to store the sublists
    sublists = []

    # Iterate over the list with a step of 5
    for i in range(0, len(individual), 5):
        # Create a new sublist with the elements from i to i+5
        sublist = individual[i:i+5]
        # Append the sublist to the sublists list
        sublists.append(sublist)

    # Print the resulting sublists
    return sublists


# Create pattern and return the length and demand in it's used sort order
def create_pattern(objects, rer_one):
    # If the first sorting method has already been used, sort the objects by demand
    if rer_one:
        demand, length = sort_rer_one(objects)
    elif not rer_one:
        demand, length = sort_rer_two(objects)

    # Create an empty population
    pattern = create_list_of_zeros(len(objects) + 1)

    # Construct the cutting pattern
    for j in range(len(length)):
        # Check if the current object fits in the pattern
        times_cut = 0
        while (calc_total_length(length, pattern) + length[j] <= base_length) and sum(demand) > 0:

            # Check if there is still demand for the current object
            if demand[j] > 0:
                demand[j] -= 1
            else:
                break

            # Add the object to the pattern
            times_cut += 1

            # Increment the count of how many times the current object has been cut
            pattern[(j + 1)] = times_cut

    return pattern, length, demand


def patternCalculations(pattern, length, demand, restore):
    # Apply pattern as often as possible given the demand
    length_requirements = pattern[1:]
    # print(f"{'patternCalculations: length_requirements'}: {length_requirements}")
    demand = subtract_lists(demand, length_requirements)
    # print(f"{'patternCalculations: demand'}: {demand}")

    # Restore pattern to original sort order
    if restore:
        pattern_dict = dict(zip(length, length_requirements))
        pattern_dict_sorted = dict(map(lambda k: (k, pattern_dict[k]), objects.keys()))
        pattern = list(pattern_dict_sorted.values())

        # Insert a zero at the beginning of the pattern
        pattern.insert(0, 0)

    # Set the first element of the pattern to the remaining demand for the first object
    pattern[0] = demand[0]
    demand.pop(0)

    return pattern, length, demand


def create_individual(objects, base_length):
    """
    Create a cutting pattern for a given set of objects and base length.

    Parameters:
    objects (dict): Dictionary containing the objects to be cut with their corresponding length and demand.
    base_length (int): The length of the base material.

    Returns:
    individual (list): List of cutting patterns.
    """

    # Create a copy of the objects dictionary to avoid modifying the original input
    objects2 = objects.copy()

    # Sort the objects by length and get the sorted lengths and demand
    demand = list(objects2.values())

    # Initialize the list to store the cutting patterns
    individual = []

    # Initialize the flag to use the first sorting method
    rer_one = True

    # Loop until all objects have been cut
    while sum(demand) > 0:

        # Create pattern and return the length and demand in it's used sort order
        pattern, length, demand = create_pattern(objects2, rer_one)

        # Set the pattern cutting times, and recalculate demand given the current sort order
        pattern, length, demand = patternCalculations(pattern, length, demand, restore=True)

        # Update the objects dictionary with the remaining demand
        objects2 = dict(zip(length, demand))

        # Add the current pattern to the list of cutting patterns
        individual.append(pattern)

        # Toggle the flag to use the other sorting method in the next iteration
        if rer_one:
            rer_one = False

    # Flatten the individual into one list
    # individual = [val for sublist in individual for val in sublist]

    # Return the individual
    return individual


def create_initial_population(objects, base_length, POPULATION_SIZE):
    population = []

    for i in range(POPULATION_SIZE):
        individual = create_individual(objects, base_length)
        population.append(individual)

    return population


# fitness calculation
def patternsWaste(individual):

    lengths = list(objects.keys())
    # zipped_individual = zip_individual(individual)
    waste_total = 0

    for pattern in individual[0]:
        total_length = calc_total_length(lengths, pattern)
        waste = base_length - total_length
        # print(f"{'waste'}: {waste}")
        waste_total += waste

    return waste_total,  # return a tuple


def createOffspring(ind1, ind2):
    # print(f"{'ind1'}: {ind1}")
    # print(f"{'ind2'}: {ind2}")

    offspring = []

    # Store the original demand
    demand, length = demand_length(objects)

    # Create copies of the individual to work with
    individual1 = ind1.copy()
    individual2 = ind2.copy()

    # Start with parent to be individual 1
    parent = individual1

    while sum(demand) > 0:

        # print(f"{'begin of iteration demand'}: {demand}")

        # Take a random pattern
        if parent:

            # Select a random gene (pattern) and remove it from the parent
            gene = random.choice(parent)
            parent.remove(gene)

            # print(f"{'gene'}: {gene}")
            # print(f"{'length'}: {length}")
            # print(f"{'demand'}: {demand}")

            # Remove initial pattern from demand
            demand_copy = demand.copy()
            demand_copy = [x - y for x, y in zip(demand_copy, gene[1:])]
            if all(n > 0 for n in demand_copy):
                demand = demand_copy.copy()
            else:
                continue

            # print(f"{'demand after initial removal of pattern'}: {demand}")

            # Set the pattern cutting times, and return length and demand in original order
            pattern, length, demand = patternCalculations(gene, length, demand, restore=False)

            # print(f"{'demand after recalculation'}: {demand}")

            offspring.append(pattern)
            # print(f"{'pattern after recalculation'}: {pattern}")

            # Generate a random integer between 0 and 1
            random_int = random.randint(0, 1)

            # Include a check on whether the individuals are not empty
            if random_int == 0:
                parent = individual1
            else:
                parent = individual2

        else:

            # print("running RER1")

            # Set the length to create a dictionary with the residual demand
            lengths = list(objects.keys())

            # Update the objects dictionary with the remaining demand
            objects2 = dict(zip(length, demand))

            # Create pattern and return the length and demand in it's used sort order
            pattern, length, demand = create_pattern(objects2, True)

            # Set the pattern cutting times, and return length and demand in original order
            pattern, length, demand = patternCalculations(pattern, length, demand, restore=True)

            # Reinitialize the objects2 to match original order
            objects2 = dict(zip(length, demand))

            # Add the current pattern to the list of cutting patterns
            offspring.append(pattern)

            # print(f"{'pattern'}: {pattern}")

    return offspring


