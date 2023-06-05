import pandas as pd
import functions_dataprep

# Read the production data from alpha deuren
# df_orders = pd.read_excel('AlphaProductionData.xlsx')
# df_production_orders = pd.read_excel('tProductieISO.xlsx')
df_production_orders_small = pd.read_excel('tProductieISO_Small.xlsx')
# materials = df_orders['MateriaalPaneelTxt'].unique()

# This is not really safe, base length might be different for each material
base_length = 12450  # functions_dataprep.extract_base_length(df_production_orders_small)

# Create dictionary of materials and the number of base panels in stock
# basePanels = functions_dataprep.create_base_panel_quantity(materials)

# Objects that we will exclude from the optimization (not yet implemented)
# objects_uncut = functions_dataprep.create_empty_dict(objects)
