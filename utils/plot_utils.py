import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import math


def one_dim_plot(sr, plot_type, axis):
    if plot_type == 'bar':
        axis.bar(sr.index, sr.values)
    elif plot_type == 'pie':
        axis.pie(sr.values, labels=sr.index, autopct='%1.1f%%')
    elif plot_type == 'line':
        axis.plot(sr.index, sr.values, marker='o')
    else:
        print("Invalid plot type. Please choose 'bar', 'pie', or 'line'.")


def get_frequent_elements(df, col_name, num_top_elements):
    return df[col_name].value_counts().nlargest(num_top_elements).sort_index()


def plot_frequent_elements(df, df_params):
    fig, axs = plt.subplots(1, len(df_params), figsize=(20, 5))
    axs = np.array(axs).reshape(-1)
    for i, row in df_params.iterrows():
        col_name = row['col_name']
        plot_type = row['plot_type']
        num_top_elements = row['num_top_elements']
        sr = get_frequent_elements(df, col_name, num_top_elements)
        one_dim_plot(sr, plot_type, axs[i])
        axs[i].set_xlabel(col_name)
        axs[i].set_ylabel('Frequency')


def cross_tabulation(df, col_name, other_col_name):
    return pd.crosstab(df[col_name], df[other_col_name], normalize="index")


def plot_cross_tabulation(df, col_names, other_col_name):
    fig, axes = plt.subplots(1, len(col_names), figsize=(20, 5))
    for i, col_name in enumerate(col_names):
        one_dim_plot(cross_tabulation(df, col_name, other_col_name), "line", axes[i])
        axes[i].set_xlabel(col_name)
        axes[i].set_ylabel(other_col_name)


def get_highly_correlated_cols(df):
    corr = df.select_dtypes("number", "category").corr()
    n = corr.shape[0]
    correlated_cols = []
    for i in range(n):
        for j in range(i + 1, n):
            if abs(corr.iloc[i, j]) >= 0.5:
                correlated_cols.append((i, j))
    correlations = [corr.iloc[i, j] for i, j in correlated_cols]
    return correlations, correlated_cols


def plot_high_correlated_scatters(df):
    _, tuple_arr = get_highly_correlated_cols(df)

    fig, axes = plt.subplots(nrows=1, ncols=len(tuple_arr))

    for i, (col1, col2) in enumerate(tuple_arr):
        axes[i].scatter(df.iloc[:, col1], df.iloc[:, col2])
        corr_val = df.iloc[:, [col1, col2]].corr().iloc[0, 1]
        title = f"corr('{df.columns[col1]}', '{df.columns[col2]}')={corr_val:4.2f}"
        axes[i].set_title(title)


def transfer_str_to_numeric_vals(dataset):
    # Transfer dataset's values to numeric ones
    for column in dataset.columns:
        labels = dataset[column].astype("category").cat.categories.to_list()
        lab_map = {value: index for index, value in enumerate(labels)}
        dataset[column] = dataset[column].map(lab_map)

    return dataset


def plot_frequencies(dataset):
    ordinal_cols = ['common_genre', 'release_year', 'release_month', 'popularity',
                    'intro_cnt', 'outro_cnt', 'verse_cnt', 'chorus_cnt']
    cols = min(len(ordinal_cols), 4)
    rows = math.ceil((len(ordinal_cols) / 4))

    for dummy in range(rows):
        sub_list = ordinal_cols[dummy * cols:(dummy + 1) * cols]
        plot_frequent_elements(
            dataset,
            pd.DataFrame({
                'plot_type': ['bar'] * len(sub_list),
                'col_name': sub_list,
                'num_top_elements': [7] * len(sub_list)
            })
        )

    numeric_cols = ['unique_words_ratio', 'stop_words_ratio', 'slang_words_ratio',
                    'positive', 'negative', 'neutral', 'compound']
    cols = min(len(numeric_cols), 4)
    rows = math.ceil((len(numeric_cols) / 4))

    for ridx in range(rows):
        fig, axs = plt.subplots(1, min(cols, len(numeric_cols) - ridx * 4), figsize=(20, 5))
        axs = np.array(axs).reshape(-1)
        for i, col in enumerate(numeric_cols[ridx * 4:(ridx + 1) * 4]):
            sns.histplot(dataset[col], ax=axs[i])


def plot_continuous_feature_relations(dataset):
    continuous_vars = ["duration", "line_cnt", "word_cnt", "unique_words_ratio", "stop_words_ratio",
                       "slang_words_ratio"]
    var_combinations = [(var1, var2) for var1 in continuous_vars for var2 in continuous_vars if var1 < var2]
    rows_num = math.ceil(len(var_combinations) / 3)
    for row_index in range(rows_num):
        fig, axs = plt.subplots(1, 3, figsize=(20, 5))
        axs = axs.flatten()
        for index, feature in enumerate(var_combinations[3 * row_index:3 * row_index + 3]):
            sns.scatterplot(dataset, x=feature[0], y=feature[1], ax=axs[index % 3])
