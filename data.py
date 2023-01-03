import pandas as pd

# objects = {4: 300, 6: 200, 3: 400, 5: 200, 2: 500, 1: 600, 12: 150, 10: 200, 8: 250, 7: 300, 9: 250, 11: 200, 13: 150,
#           17: 200}

# base_length = 17

df_orders = pd.read_excel('AlphaProductionData.xlsx')


def create_dict(df):

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


objects = create_dict(df_orders)
base_length = extract_base_length(df_orders)



