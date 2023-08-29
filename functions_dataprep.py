# Data parsing and preparation functions
# These functions are used in the data.py file to prepare the data for the genetic algorithm

def create_base_panel_quantity(materials):
    """
    This function creates base panel quantity for each material in the materials' dictionary.
    This is a test function that creates for each material 500 base panels in stock.

    :param materials: dictionary with materials as keys
    :return: dictionary with base panel quantity for each material
    """
    base_panel_quantity = {}

    for material in materials:
        base_panel_quantity[material] = 500

    return base_panel_quantity


def create_empty_dict(original_dict):
    """
    This function creates a new dictionary with the same keys as the original dictionary and assigns 0 as value for each key.
    :param original_dict: dictionary
    :return: new dictionary with 0 as value for each key
    """
    new_dict = {}
    for key in original_dict:
        new_dict[key] = 0
    return new_dict


def create_material_dict(df):
    """
    This function creates a dictionary for each material in the dataframe based on the 'MateriaalPaneelTxt' column
    :param df: dataframe
    :return: dictionary with materials as keys and dictionary of length counts as values
    """
    dict_materials = {}

    for material in df['MateriaalPaneelTxt'].unique():
        dict_materials[material] = create_empty_dict(df[df['MateriaalPaneelTxt'] == material])

    return dict_materials


def create_length_dict(df):
    """
    This function creates a dictionary with length as key and count as value for each unique length in the dataframe
    :param df: dataframe
    :return: dictionary with lengths as keys and counts as values
    """
    dict_lengths = {}

    for length in df['Lengtepaneel'].unique():
        sum_length = sum(df['Lengtepaneel'] == length)
        dict_lengths[length] = sum_length

    return dict_lengths


def extract_base_length(df):
    """
    This function extracts the first unique base length in the 'Lengte' column of the dataframe.
    :param df: dataframe
    :return: first unique base length
    """
    return df['Lengte'].unique()[0]


def panel_count(df):
    """
    This function groups the dataframe by 'MateriaalPaneelTxt', 'Dikte', 'Hoogte' and returns a dictionary with counts of the unique combinations
    :param df: dataframe
    :return: dictionary with counts of unique combinations of 'MateriaalPaneelTxt', 'Dikte', 'Hoogte'
    """
    # create a new DataFrame containing only the relevant columns
    df_subset = df[['MateriaalPaneelTxt', 'Dikte', 'Hoogte']]
    # group the DataFrame by the unique combinations of the columns
    groups = df_subset.groupby(['MateriaalPaneelTxt', 'Dikte', 'Hoogte']).size()
    # convert the result to a dictionary
    panel_count_dict = groups.to_dict()

    return panel_count_dict


def base_count(df):
    """
    This function creates a dictionary with base panel number as key and rest length as value for each unique base panel in the dataframe
    :param df: dataframe
    :return: dictionary with base panel number as key and rest length as value
    """
    dict_base = {}

    # create a new DataFrame containing only the relevant columns
    df_subset = df[['Basisnummer', 'Restlengte']]

    # Create the dict
    for basepanel in df_subset['Basisnummer'].unique():
        dict_base[basepanel] = df_subset.loc[df['Basisnummer'] == basepanel].iloc[0]['Restlengte']

    return dict_base


def create_subsets(df, subsets):
    """
    This function creates a dictionary for each subset in the subsets list, where each subset is a tuple of (material, thickness, height)
    :param df: dataframe
    :param subsets: list of tuples
    :return: dictionary with subsets as keys and dictionaries of length counts as values
    """
    dict_subsets = {}

    for subset in subsets:
        dict_subsets[subset] = create_length_dict(
            df[(df['MateriaalPaneelTxt'] == subset[0]) & (df['Dikte'] == subset[1]) & (df['Hoogte'] == subset[2])])

    return dict_subsets


def list_subsets(dict_subsets):
    """
    This function takes a dictionary of subsets and returns a list of the subsets' dictionaries
    :param dict_subsets: dictionary with subsets as keys and dictionaries as values
    :return: list of subsets' dictionaries
    """
    # list to store the created dictionaries
    subsets = []

    for key, value in dict_subsets.items():
        subsets.append(value)

    return subsets


def performance_set(df_orders, subset_keys):
    """
    This function calculates the performance of a subset based on the subset_keys tuple (material, thickness, height)
    :param subset_keys: tuple of (material, thickness, height)
    :return: print statement with results
    """
    k = subset_keys

    x = df_orders[(df_orders['MateriaalPaneelTxt'] == subset_keys[0]) & (df_orders['Dikte'] == subset_keys[1]) & (
            df_orders['Hoogte'] == subset_keys[2])]

    y = base_count(x)

    nr_of_panels = len(y.keys())

    z = sum(y.values()) / 12450

    waste = sum(y.values())

    total_material = (nr_of_panels * 12450)

    return k, nr_of_panels, waste, total_material


