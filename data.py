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

UbiOps_Data = {"root_ids": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "ids": [2956129, 2956130, 2956131, 2956132, 2956134, 2956133, 2956135, 2956136, 2956137, 2956138, 2956139,
                2956140, 2956141, 2956142, 2956143, 2956144, 2956186, 2956187, 2956188, 2956189],
        "lengths": [2833, 2833, 2833, 2833, 2833, 2833, 2833, 2833, 4903, 4903, 4903, 4903, 4903, 4903, 4903, 4903,
                    3033, 3033, 3033, 3033],
        "widths": [40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40],
        "heights": [610, 610, 610, 610, 610, 610, 610, 610, 610, 610, 610, 610, 610, 610, 610, 610, 610, 732, 732, 610],
        "materialtypes": ["VN7035", "VN7035", "VN7035", "VN7035", "VN7035", "VN7035", "VN7035", "VN7035", "VN6005",
                          "VN6005", "VN6005", "VN6005", "VN6005", "VN6005", "VN6005", "VN6005", "VN7016", "VN7016",
                          "VN7016", "VN7016"]}

df_UbiOps = pd.DataFrame(UbiOps_Data)

# Rename columns
df_UbiOps = df_UbiOps.rename(columns={
    "ids": "id",
    "lengths": "Lengtepaneel",
    "widths": "Dikte",
    "heights": "Hoogte",
    "materialtypes": "MateriaalPaneelTxt"
})