import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import style
from sklearn.ensemble import RandomForestRegressor
from sklearn import model_selection


good_ticker_list = []
for ticker in ticker_dict.values():
    if not ticker.price.empty and not ticker.balance_sheet.empty and not ticker.income_statement.empty:
        good_ticker_list.append(ticker)

df_list = []
for ticker in good_ticker_list:
    ticker.create_combined_df()
    ticker.slice_df_on_revenue()
    for column_name in column_names:
        ticker.impute_combined_df(column_name)
    df_list.append(ticker.combined_df)

big_df = pd.concat(df_list, axis=0)

X = big_df.drop('Price', axis=1)
y = big_df['Price']

X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.2)

clf = RandomForestRegressor()
clf.fit(X_train, y_train)


# I guess the first thing I'll do is create the subplots first. My plan is to create three plots. One plot will be
# the price and the dividend sharing a y axis over the same period of time
# for ticker in approved_tickers:
style.use('ggplot')
for ticker in good_ticker_list:
    fig = plt.figure(figsize=(20,20))
    fig.suptitle(f'{ticker.symbol} Stock Information', fontsize=36)

    ax1 = plt.subplot2grid(shape=(55, 2), loc=(0, 0), rowspan=30, colspan=2, fig=fig)
    ax1.plot(ticker.price, label='Price')
    ax1.set(xlabel='Year (YYYY)',
            ylabel='Price per Share (USD)')
    ax1.legend(loc=(0, 0.8))
    if not ticker.dividends.empty:
        ax2 = ax1.twinx()
        ax2.plot(ticker.dividends, color='g', label='Dividend')
        ax2.set(ylabel='Quarterly Dividends Paid (%)')
        ax2.legend(loc=(0, 0))
    else:
        ax1.text(x=0, y=0, s=f'{ticker.symbol} pays no dividends.')

    # The seocnd plot will have to do with the Balance Sheet, so I will just be plotting the short term/long term assets
    # and the short term/long term liabilities
    ax3 = plt.subplot2grid(shape=(55, 2), loc=(35, 0), rowspan=20, colspan=1, fig=fig)
    ax3.plot(ticker.balance_sheet['ShortTermAssets'] / 10**6, label='ShortTermAssets')
    ax3.plot(ticker.balance_sheet['TotalAssets'] / 10**6, label='TotalAssets')
    ax3.plot(ticker.balance_sheet['ShortTermLiabilities'] / 10**6, label='ShortTermLiabilities')
    ax3.plot(ticker.balance_sheet['TotalLiabilities'] / 10**6, label='TotalLiabilities')
    ax3.set(xlabel='Date (YYYY-MM)',
            ylabel='Millions (USD)',
            title='Balance Sheet Information')
    ax3.legend(loc=(0, 0))

    # The third plot will have to do with EPS and revenues, plotted on the same chart, with differing y scales
    ax4 = plt.subplot2grid(shape=(55, 2), loc=(35, 1), rowspan=20, colspan=1, fig=fig)
    ax4.plot(ticker.income_statement['TotalRevenue'] / 10**6, label='Revenue (Ann.)')
    ax4.plot(ticker.income_statement['NetIncome'] / 10**6, label='Income (Ann.)')
    ax4.set(xlabel='Date (YYYY-MM)',
            ylabel='Millions (USD)',
            title='Earnings Information')
    ax5 = ax4.twinx()
    ax5.plot(ticker.eps['EPS'], label='EPS (Qtrly)', color='g')
    ax5.set(ylabel='Earnings Per Share Quarterly (USD)')
    ax4.legend(loc=(0, 0))
    ax5.legend(loc=(0.9, 0))
    plt.savefig(f'test_graph_{ticker.symbol}.png')