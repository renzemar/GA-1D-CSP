from typing import List, Dict, Tuple, Any
import random
from data import objects, base_length
import time
import math


# Main functions for the Genetic Algorithm
# Used in the GA_CSP file

def sanityCheck(population: list[List[List[int]]]) -> str:
    """
    This function checks the sanity of the given population. It checks if the sum of the patterns in each individual
    equals the sum of the demand.

    Param: population (list): A list of lists, where each inner list represents an individual in the population
    and is a list of patterns. Each pattern is a list with the first element being the frequency and the remaining
    elements being the demand for each object.

    Returns:
        bool: True if the sum of the patterns in each individual equals the sum of the demand, False otherwise.
    """
    sanity = False
    total = 0

    for individual in population:
        for pattern in individual:
            x = pattern[1:]
            total += sum(x) * pattern[0]

        sum_demand = sum(objects.values())

        if total == sum_demand:
            sanity = True

    # if not sanity:
    #    print("Sanity check failed")
    # else:
    #    print("Sanity check passed")

    return sanity


def subtract_lists(list1: List[int], list2: List[int]) -> List[int]:
    """
    This function subtracts the elements of arr2 from arr1, until the result is non negative. It returns a new list with
    the number of times arr2 was subtracted from arr1 as the first element, followed by the resulting list.

    Parameters:
        list1 (list): The list to subtract from, which is the demand.
        list2 (list): The list to subtract, which is the pattern.

    Returns:
        list: A new list with the number of times list2 was subtracted from arr1 as the first element,
        followed by the resulting list.
    """
    # Initialize the count of how many times list2 has been subtracted from list1
    pattern_count = 1  # already subtracted once from demand

    # Make sure the lists have the same length
    if len(list1) != len(list2):
        # print("Unequal lists")
        return None

    # Subtract list2 from list1 until the result is non-negative
    while all(x - y >= 0 for x, y in zip(list1, list2)):
        list1 = [x - y for x, y in zip(list1, list2)]
        # print(f"{'list1 (demand) in loop'}: {list1}")
        pattern_count += 1

    # Create the result list and insert the pattern count as the first element
    result = list1
    result.insert(0, pattern_count)

    # print(f"{'list1 (demand) result'}: {list1}")

    return result


def demand_length(sorted_objects: Dict[int, int]) -> Tuple[List[int], List[int]]:
    """
    This function calculates the demand for each type of object and sorts the objects in descending order by length.

    Parameters:
    sorted_objects (dict): A dictionary containing the length of each object as the keys and the demand for each
    object as the values.

    Returns:
        tuple: A tuple containing two lists, the first list is the demand for each type of object and the second list
        is the length of each object sorted in descending order.
    """
    # Calculate the demand for each type of object
    demand = list(sorted_objects.values())

    # Sort the objects in descending order by length
    length = list(sorted_objects.keys())
    length.sort(reverse=True)

    return demand, length


def sort_rer_one(objects: Dict[str, int]) -> Tuple[List[int], List[int]]:
    """
    This function sorts the given dictionary of objects by their values in descending order,
    and returns two lists: one with the keys (demand) and one with the values (length).

    Parameters:
    objects (dict): A dictionary where the keys are strings and the values are integers.

    Returns:
        tuple: A tuple with two lists: one with the keys (demand) and one with the values (length).
    """
    # Sort the dictionary in descending order
    sorted_objects = dict(sorted(objects.items(), reverse=True))

    # Get the demand and length lists from the sorted objects
    demand, length = demand_length(sorted_objects)

    return demand, length


def sort_rer_two(objects: Dict[int, int]) -> Tuple[List[int], List[int]]:
    """
    This function shuffles a dictionary of objects randomly, and then returns the demand and length lists.

    Parameters:
    objects (dict): A dictionary of objects with the keys as the object IDs and the values as the lengths.

    Returns:
        tuple: A tuple containing the demand and length lists.
    """
    # Shuffle the objects randomly
    l = list(objects.items())
    random.shuffle(l)
    shuffled_objects = dict(l)

    # Calculate the demand for each type of object
    demand = list(shuffled_objects.values())

    # Sort the objects in descending order by length
    length = list(shuffled_objects.keys())

    return demand, length


def create_list_of_zeros(length: int) -> List[int]:
    """
    This function creates a list of zeros with the specified length.

    Parameters:
        length (int): The length of the list to be created.

    Returns:
        list: A list of zeros with the specified length.
    """

    empty_pattern = [0] * length
    return empty_pattern


def calc_total_length(lengths: List[int], pattern: List[int]) -> int:
    """
    This function calculates the total length of a pattern by multiplying the lengths of each object in the pattern
    by the number of times it appears.

    Parameters:
    lengths (list): A list of integers representing the lengths of each object in the pattern.
    pattern (list): A list of integers representing the number of times each object appears in the pattern.

    Returns:
        int: The total length of the pattern.
    """
    total_length = 0

    for i, val in enumerate(pattern):
        if i == 0:
            continue
        total_length += lengths[i - 1] * val

    return total_length


def zip_individual(individual: List[int]) -> List[List[int]]:
    """
    This function takes a list of integers and returns a list of sublists, each containing 5 elements from the
    original list. If the original list has a length that is not a multiple of 5, the last sublist will contain fewer
    than 5 elements.

    Parameters:
    individual (list): A list of integers to be divided into sublists of 5 elements each.

    Returns:
        list: A list of sublist, each containing 5 elements from the original list.
    """
    # Create a new list to store the sublist
    sublists = []

    # Iterate over the list with a step of 5
    for i in range(0, len(individual), 5):
        # Create a new sublist with the elements from i to i+5
        sublist = individual[i:i + 5]
        # Append the sublist to the sublist list
        sublists.append(sublist)

    # Return the resulting sublist
    return sublists


def create_pattern(objects: Dict, rer_one: bool) -> Tuple[List[int], List[int], List[int]]:
    """
    This function creates a cutting pattern based on the demand and lengths of the given objects. The pattern is
    sorted by the first sorting method if rer_one is True, and sorted by the second sorting method if rer_one is
    False. The function returns a tuple containing the cutting pattern, the lengths of the objects, and the demand
    for the objects.

    Parameters: objects (List[Object]): A list of objects to create the cutting pattern for. rer_one (bool): A
    boolean value indicating whether the first sorting method should be used (True) or the second sorting method (
    False).

    Returns: Tuple[List[int], List[int], List[int]]: A tuple containing the cutting pattern, the lengths of the
    objects, and the demand for the objects.
    """
    # If the first sorting method has already been used, sort the objects by demand
    if rer_one:
        demand, length = sort_rer_one(objects)
    elif not rer_one:
        demand, length = sort_rer_two(objects)

    # Create an empty population
    pattern = create_list_of_zeros(len(objects) + 1)

    max_times = 9999999

    if not rer_one:

        current_length = length[0]

        # calculate the number of times the base length can be added to the pattern
        max_count = math.floor(base_length / current_length)
        # calculate the remaining length after adding the base length to the pattern
        remaining = base_length - (max_count * current_length)

        if remaining < (0.025 * base_length):
            max_times = max_count
        else:
            # Get a random percentage of the remaining space
            random_percentage = random.randint(10, 100) / 100
            length_remaining = 12450 - (random_percentage * current_length)
            # Calculate the number of times item j can be cut from remaining space
            max_times = round(length_remaining / current_length)

    # Construct the cutting pattern
    for j in range(len(length)):

        # Check if the current object fits in the pattern
        times_cut = 0
        while (calc_total_length(length, pattern) + length[j] <= base_length) and sum(
                demand) > 0 and max_times > times_cut:

            # Check if there is still demand for the current object
            if demand[j] > 0:
                demand[j] -= 1
            else:
                break

            # Add the object to the pattern
            times_cut += 1

            # Increment the count of how many times the current object has been cut
            pattern[(j + 1)] = times_cut

            # Decrement the max times the object can be cut
            max_times -= 1

    return pattern, length, demand


def patternCalculations(pattern: List[int], length: List[int], demand: List[int], restore: bool) -> Tuple[List[int],
List[int],
List[int]]:
    """
    This function applies a given pattern to the demand for objects of different lengths, as often as possible given
    the demand. It also has the option to restore the pattern to its original sort order. Finally, it sets the first
    element of the pattern to the remaining demand for the first object.

    Parameters:
    pattern (list): The list representing the pattern to be applied.
    length (list): The list of lengths of the objects.
    demand (list): The list of demands for the objects.
    restore (bool): Flag to determine whether to restore the pattern to its original sort order.

    Returns:
        tuple: A tuple containing the updated pattern, length, and demand lists.
    """
    # Apply pattern as often as possible given the demand
    length_requirements = pattern[1:]
    demand = subtract_lists(demand, length_requirements)

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


# Only use rer_one for the first individual
rer_one = True


def create_individual(objects):
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
    global rer_one

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

    # Sanity check
    sanity = sanityCheck([individual])
    if not sanity:
        print('False offspring created')

    # Return the individual
    return individual


def create_initial_population(objects: List[Any], base_length: int, POPULATION_SIZE: int) -> List[List[Any]]:
    """
    This function generates a list of randomly generated individuals, with a given base length and number of objects.

    Parameters:
        objects (list): The list of objects to use for generating the individuals.
        base_length (int): The base length for each individual.
        POPULATION_SIZE (int): The size of the population to generate.

    Returns:
        list: A list of randomly generated individuals.
    """
    population = []

    for i in range(POPULATION_SIZE):
        individual = create_individual(objects, base_length)
        population.append(individual)

    return population


def patternsWaste(individual):
    """
    This function calculates the total waste for a given list of patterns. The waste is calculated
    by subtracting the total length of all patterns in the list from the base length of the patterns.
    The base length is the first element in each list in the list of patterns.

    Parameters:
    individual (list): A list of patterns. Each pattern is represented as a list of integers.

    Returns:
        tuple: A tuple containing the total waste as the only element.
    """
    lengths = list(objects.keys())
    # zipped_individual = zip_individual(individual)
    waste_total = 0

    for pattern in individual[0]:
        total_length = calc_total_length(lengths, pattern)
        waste = base_length - total_length
        # print(f"{'waste'}: {waste}")
        waste_total += waste

    # material_used = sum_baseLength(individual[0]) * 12450
    # waste_total += material_used

    return waste_total,  # return a tuple


def baseLengthsAmount(individual):
    """
    This function calculates the total length of the base patterns in an individual.
    The base pattern is the first element in each list in the list of patterns.

    Parameters:
    individual (list): A list containing the patterns of the individual.

    Returns:
        tuple: A tuple containing the total length of the base patterns.
    """
    baseLengths_total = 0
    for pattern in individual[0]:
        if pattern:  # make sure the list is not empty
            baseLengths_total += pattern[0]

    return baseLengths_total,  # return a tuple


def createOffspring(ind1: List[List[int]], ind2: List[List[int]]) -> List[List[int]]:
    """
    This function creates offspring patterns by combining patterns from two individual patterns, using a random selection
    process. It also applies the selected patterns to the demand for objects of different lengths, as often as possible.
    The function has the ability to switch between the two individuals during the selection process.

    Parameters:
    ind1 (list): The first individual pattern to be used in the offspring creation.
    ind2 (list): The second individual pattern to be used in the offspring creation.

    Returns:
        list: A list of the offspring patterns created.
    """
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
            if all(n >= 0 for n in demand_copy):
                demand = demand_copy.copy()
            else:

                if parent == individual1 and individual2:
                    parent = individual2
                elif parent == individual2 and individual1:
                    parent = individual1

                continue

            # print(f"{'demand after initial removal of pattern'}: {demand}")

            # Set the pattern cutting times, and return length and demand in original order
            pattern, length, demand = patternCalculations(gene, length, demand, restore=False)

            # print(f"{'demand after recalculation'}: {demand}")

            offspring.append(pattern)
            # print(f"{'pattern after recalculation'}: {pattern}")

            if parent == individual1 and individual2:
                parent = individual2
            elif parent == individual2 and individual1:
                parent = individual1

        else:

            # print("running RER1")

            # Set the length to create a dictionary with the residual demand
            length = list(objects.keys())

            # Update the objects dictionary with the remaining demand
            objects2 = dict(zip(length, demand))

            # Create pattern and return the length and demand in it's used sort order
            pattern, length, demand = create_pattern(objects2, True)

            # Set the pattern cutting times, and return length and demand in original order
            pattern, length, demand = patternCalculations(pattern, length, demand, restore=True)

            # Add the current pattern to the list of cutting patterns
            offspring.append(pattern)

            # print(f"{'pattern'}: {pattern}")

    # Sanity check
    sanity = sanityCheck([offspring])

    if not sanity:
        print('False offspring created')

    return offspring


def sum_baseLength(ind: List[List[int]]) -> int:
    """
    This function calculates the total amount of the base lengths used in a list of patterns.
    The base length is the first element in each list in the list of patterns.

    Parameters:
    ind (list): A list of patterns.

    Returns:
        int: The total length of the base patterns.
    """
    total = 0
    for pattern in ind:
        if pattern:  # make sure the list is not empty
            total += pattern[0]
    return total


def measure_time(func):
    """
    This is a decorator function that measures and prints the execution time of the decorated function.

    Parameters:
    func (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """

    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f'Finished {func.__name__} in {end_time - start_time:.6f} seconds')
        return result

    return wrapper