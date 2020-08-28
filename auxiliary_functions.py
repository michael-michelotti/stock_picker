import pandas as pd
import numpy as np


def impute_df(df, column_name):
    price_nulls = df[df[column_name].isnull()].index
    for nulls in price_nulls:
        null_loc = df.index.get_loc(nulls)
        if np.isnan(df[column_name].iloc[null_loc]):
            og_null_loc = null_loc
            total_nulls = 1
            ends_with_null = False
            starts_with_null = False
            while np.isnan(df[column_name].iloc[null_loc]):
                if null_loc == 0:
                    starts_with_null = True
                if null_loc == len(df[column_name])-1:
                    ends_with_null = True
                    break
                if np.isnan(df[column_name].iloc[null_loc+1]):
                    total_nulls += 1
                null_loc += 1

            first_point = og_null_loc - 1
            second_point = null_loc

            if ends_with_null:
                impute_value = df[column_name].iloc[first_point]
                df[column_name].iloc[og_null_loc:] = impute_value
            elif starts_with_null:
                impute_value = df[column_name].iloc[null_loc]
                df[column_name].iloc[:null_loc] = impute_value
            else:
                rise = df[column_name].iloc[second_point] - df[column_name].iloc[first_point]
                run = second_point - first_point
                slope = np.divide(rise, run)
                for nums in np.arange(start=1, stop=total_nulls+1):
                    df[column_name].iloc[first_point+nums] = slope * nums + df[column_name].iloc[first_point]
