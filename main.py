import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import style
from sklearn.ensemble import RandomForestRegressor
from sklearn import model_selection
from Ticker import Ticker
from pickle import load


# This will be the main function that I can come into and pull whatever information was made available in the
# refresh_financials function. I can manipuate that info and use scikitlearn to try and make some predictions about
# price of stocks going into the future based on information about how many dividends they paid out
# I really need to think now about what I'm going to try and predict and what I'm going to try to use to predict it.

# Obviously, my target column is stock price. I want to predict it based on all the parameters I have.
# All of my other data is sampled less often, so I think I need to do a lot of imputing. I think I will use dividend,
# revenue, and Total Assets - Total Liabilities to make these predictions.

# It's not really that useful to make the 'target' just a monthly price. Well, maybe not. What I really want to do is
# make the target the FUTURE price given the dividend, liability, and Total Assets - Total Liabilities. I think what
# I want to do is impute everything for revenues, assets, dividends. Then, I will shift the price column down one to be
# three months in the future. At that point, I can make my prediction. At that point, I can concatenate every single
# imputed dataframe and really train my model on a ton of data. I will require any stock that I model to have a
# revenue, dividend, and balance_sheet csv. Don't care about EPS, will only use that for charts.

# The first thing I want to do is drop every row that occurs before there is any revenue data
ticker_dict = load(open('ticker_dict.pkl', 'rb'))

# I think I only want to do stocks that have a balance sheet and revenue CSV. They can have no dividend csv, in that
# case I will just impute 0 into the dividend column
column_names = ['Price', 'TotalRevenue', 'GrossProfit', 'NetIncome', 'Dividend', 'ShortTermAssets',
                'TotalAssets', 'ShortTermLiabilities', 'TotalLiabilities']

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
my_df = pd.read_csv('prices/JPM_price.csv', parse_dates=True, index_col='Timestamp')
my_div = pd.read_csv('dividends/JPMdividends.csv', parse_dates=True, index_col='Unnamed: 0')

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