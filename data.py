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
        basePanel_material[material] = 3

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


# Create dictionary of materials and the number of base panels in stock
basePanels = basePanel_material(materials)


# The following materials are in this dataset: ['VN9005', 'VN8014', 'VN7005', 'VN7016', 'VN6005', 'VNS9006',
#        'NN9002', 'NNS9006', 'VN3000', 'VN9006', 'VN9010', 'VN5010',
#        'VN9007', 'NNS9002', 'VN9002', 'NNS7016', 'VN6009', 'VN7035']

Material_objects = create_material_dict(df_orders)

# Run on a subset of the dataset
# objects = Material_objects['VN9005'] #!
objects, basePanels = Material_objects['VN8014'], basePanels['VN8014']
# objects = Material_objects['VN7005']
# objects = Material_objects['VN7016']  # DEMO SET 2
# objects = Material_objects['VN6005']
# objects = Material_objects['VNS9006']
# objects = Material_objects['NN9002']
# objects = Material_objects['NNS9006']
# objects = Material_objects['VN3000']
# objects = Material_objects['VN9006']  # DEMO SET 1
# objects = Material_objects['VN9010']
# objects = Material_objects['VN5010']
# objects = Material_objects['VN9007']
# objects = Material_objects['NNS9002']  # DEMO SET 3
# objects = Material_objects['VN9002']
# objects = Material_objects['NNS7016']
# objects = Material_objects['VN6009']
# objects = Material_objects['VN7035']

# Objects that cannot be cut
objects_uncut = create_dict_zeros(objects)

# This is not really safe, base length might be different for each material
base_length = extract_base_length(df_orders)

# objects = create_dict(df_orders) # Run on entire dataset instead
print(objects)
print(objects_uncut)
print(basePanels)
base_length = extract_base_length(df_orders)
