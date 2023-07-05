import numpy as np
import pandas as pd


def remove_duplicates_and_drop_na(df: pd.DataFrame):
    clean_df = df.copy()
    clean_df.dropna(inplace=True)
    clean_df.drop_duplicates(["name", "artists"], inplace=True)

    return clean_df


def repair_numeric_missing_vals(df, numeric_cols):
    repaired_vals_map = {col: df[col].median() for col in numeric_cols}
    repaired_df = df.fillna(value=repaired_vals_map)

    return repaired_df


def my_dist_to_avg(col):
    z_score = (col - col.mean()) / col.std()
    col.loc[abs(z_score) > 3] = np.nan


def my_iqr(col):
    Q1 = col.quantile(0.25)
    Q3 = col.quantile(0.75)
    IQR = Q3 - Q1
    col.loc[(col < Q1 - 1.5 * IQR) | (col > Q3 + 1.5 * IQR)] = np.nan


def outlier_detection_iqr(df, dfunc):
    df_main = df.copy()
    [dfunc(df_main[col]) for col in df_main.select_dtypes('number')]

    return df_main


def transfer_to_categorical(df, bin_cols, categorical_col_names):
    transferred_df = df.copy()
    for col in bin_cols:
        transferred_df[f"{col}_categorical"] = pd.cut(
            transferred_df[col],
            5,
            labels=[1, 2, 3, 4, 5]
        )

    transferred_df = pd.get_dummies(
        data=transferred_df,
        columns=categorical_col_names,
        prefix=categorical_col_names
    )

    return transferred_df
