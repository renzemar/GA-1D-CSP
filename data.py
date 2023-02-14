import pandas as pd
import functions_dataprep

# Read the production data from alpha deuren
df_orders = pd.read_excel('AlphaProductionData.xlsx')
materials = df_orders['MateriaalPaneelTxt'].unique()

# This is not really safe, base length might be different for each material
base_length = functions_dataprep.extract_base_length(df_orders)

# Change the index to get the different subsets
# subset_index = 26  # set 14, 19 and 24 are large subsets, 26 is medium-sized, with a total of 29 subsets

subsets = functions_dataprep.panel_count(df_orders)
dict_subsets = functions_dataprep.create_subsets(df_orders, subsets)
list_subsets = functions_dataprep.list_subsets(dict_subsets)
lookup = pd.DataFrame()
lookup['Key'] = dict_subsets.keys()

# Create dictionary of materials and the number of base panels in stock
basePanels = functions_dataprep.create_base_panel_quantity(materials)

# Objects that we will exclude from the optimization (not yet implemented)
# objects_uncut = functions_dataprep.create_empty_dict(objects)

