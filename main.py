import matplotlib.pyplot as plt
import pandas as pd
import pickle

import chart_ticker


if __name__ == "__main__":
    ticker_dict = pickle.load(open("ticker_dict.pkl", "rb"))
    for ticker in ticker_dict.values():
        if not (
            ticker.price.empty
            and ticker.balance_sheet.empty
            and ticker.income_statement.empty
        ):
            plt.rcParams = chart_ticker.configure_rc_params("full_chart")
            fig = chart_ticker.create_chart("full_chart")
            chart_ticker.chart_financials(ticker, fig)

    # df_list = []
    # for ticker in good_ticker_list:
    #     ticker.create_combined_df()
    #     ticker.slice_df_on_revenue()
    #     for column_name in column_names:
    #         ticker.impute_combined_df(column_name)
    #     df_list.append(ticker.combined_df)

    # big_df = pd.concat(df_list, axis=0)
