import pandas as pd

# Random testing data, not based on anything
# objects = {4: 300, 6: 200, 3: 400, 5: 200, 2: 500, 1: 600, 12: 150, 10: 200, 8: 250, 7: 300, 9: 250, 11: 200, 13: 150,
#           17: 200}

# base_length = 17

# Read the production data from alpha deuren
df_orders = pd.read_excel('AlphaProductionData.xlsx')
materials = df_orders['MateriaalPaneelTxt'].unique()


def basePanel_material(materials):
    """
    This function creates base panel quantity  for each material in the materials' dictionary. This is a
    test function that creates for each material 500 base panels in stock.

    :param materials:
    :return: dictionary with base panel quantity for each material
    """
    basePanel_material = {}

    for material in materials:
        basePanel_material[material] = 500

    return basePanel_material


def create_dict_zeros(original_dict):
    new_dict = {}
    for key in original_dict:
        new_dict[key] = 0
    return new_dict


def create_material_dict(df):
    dict_materials = {}

    for material in materials:
        dict_materials[material] = create_dict(df[df['MateriaalPaneelTxt'] == material])

    return dict_materials


def create_dict(df):
    # Take a subset of the data, not based on the material, but on portion of the entire data
    # df = df.iloc[:int(len(df) / 12)]
    # df = df.iloc[:int(len(df) / 6)]
    # df = df.iloc[:int(len(df) / 2)]

    dict_lengths = {}

    for length in df['Lengtepaneel'].unique():
        sum_length = sum(df['Lengtepaneel'] == length)
        dict_lengths[length] = sum_length

    return dict_lengths


def extract_base_length(df):
    # Not very safe. What to do when multiple base lengths are present?

    return df['Lengte'].unique()[0]


def panel_count(df):
    # create a new DataFrame containing only the relevant columns
    df_subset = df[['MateriaalPaneelTxt', 'Dikte', 'Hoogte']]
    # group the DataFrame by the unique combinations of the columns
    groups = df_subset.groupby(['MateriaalPaneelTxt', 'Dikte', 'Hoogte']).size()
    # convert the result to a dictionary
    panel_count_dict = groups.to_dict()

    return panel_count_dict


def base_count(df):
    # Initialize the lengths
    dict_base = {}

    # create a new DataFrame containing only the relevant columns
    df_subset = df[['Basisnummer', 'Restlengte']]

    # Create the dict
    for basepanel in df_subset['Basisnummer'].unique():
        dict_base[basepanel] = df_subset.loc[df['Basisnummer'] == basepanel].iloc[0]['Restlengte']

    return dict_base


def create_subsets(df, subsets):
    dict_subsets = {}

    for subset in subsets:
        dict_subsets[subset] = create_dict(
            df[(df['MateriaalPaneelTxt'] == subset[0]) & (df['Dikte'] == subset[1]) & (df['Hoogte'] == subset[2])])

    return dict_subsets


def list_subsets(dict_subsets):
    # list to store the created dictionaries
    subsets = []

    for key, value in dict_subsets.items():
        subsets.append(value)

    return subsets


def performance_set(subset_keys):
    k = subset_keys

    x = df_orders[(df_orders['MateriaalPaneelTxt'] == subset_keys[0]) & (df_orders['Dikte'] == subset_keys[1]) & (
            df_orders['Hoogte'] == subset_keys[2])]

    y = base_count(x)

    nr_of_panels = len(y.keys())

    z = sum(y.values()) / 12450

    a = sum(y.values())

    total_material = (nr_of_panels * 12450) + a

    return print(f"Analyzed subset: {k}; Base panels used: {nr_of_panels}; Base panels waste: {z}; Total waste: {a}"
                 f"; Total material used: {total_material}")


subset_index = 14  # Change the index to get the different subsets

subsets = panel_count(df_orders)
dict_subsets = create_subsets(df_orders, subsets)
list_subsets = list_subsets(dict_subsets)
lookup = pd.DataFrame()
lookup['Key'] = dict_subsets.keys()
original_performance = performance_set(lookup.loc[subset_index][0])

# Calculations for the performance of the current algorithm
# base_count(df_orders)
# sum(base_count(df_orders).values()) / 12450

# Create dictionary of materials and the number of base panels in stock
basePanels = basePanel_material(materials)

# The following materials are in this dataset: ['VN9005', 'VN8014', 'VN7005', 'VN7016', 'VN6005', 'VNS9006',
#        'NN9002', 'NNS9006', 'VN3000', 'VN9006', 'VN9010', 'VN5010',
#        'VN9007', 'NNS9002', 'VN9002', 'NNS7016', 'VN6009', 'VN7035']

objects = list_subsets[subset_index].copy()

# Objects that cannot be cut
objects_uncut = create_dict_zeros(objects)

# This is not really safe, base length might be different for each material
base_length = extract_base_length(df_orders)

# objects = create_dict(df_orders) # Run on entire dataset instead
print(objects)
#print(objects_uncut)
#print(basePanels)
print(original_performance)
base_length = extract_base_length(df_orders)
