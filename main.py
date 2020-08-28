import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import style
from sklearn.ensemble import RandomForestRegressor


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
price_df = pd.read_csv('prices/AAPL_price.csv', parse_dates=True, index_col='Timestamp')
div_df = pd.read_csv('dividends/AAPLdividends.csv', parse_dates=True, index_col='Unnamed: 0')
bs_df = pd.read_csv('balance_sheet/AAPL_balance_sheet.csv', parse_dates=True, index_col='Unnamed: 0')
eps_df = pd.read_csv('eps/AAPL_eps.csv', parse_dates=True, index_col='Unnamed: 0')
rev_df = pd.read_csv('revenue/AAPL_revenue.csv', parse_dates=True, index_col = 'Unnamed: 0')
price_df['TotalRevenue'] = rev_df['TotalRevenue']
price_df['TotalRevenue'].value_counts()
rev_df.index.rename('Timestamp', inplace=True)
price_df.merge(rev_df, on='Timestamp', how='outer')
price_df.drop(columns='TotalRevenue', inplace=True)
price_df = price_df.merge(rev_df, on='Timestamp', how='outer')
price_df = price_df.sort_index()
my_ts = price_df[ price_df['TotalRevenue'].notnull() ].index[0]
price_df = price_df.loc[my_ts:]
price_df.drop(columns='EPS', inplace=True)
price_df[price_df['Price'].isnull()]



approved_tickers = []
# I guess the first thing I'll do is create the subplots first. My plan is to create three plots. One plot will be
# the price and the dividend sharing a y axis over the same period of time
# for ticker in approved_tickers:
my_df = pd.read_csv('prices/JPM_price.csv', parse_dates=True, index_col='Timestamp')
my_div = pd.read_csv('dividends/JPMdividends.csv', parse_dates=True, index_col='Unnamed: 0')

style.use('ggplot')
fig = plt.figure()
fig.suptitle('JPM Stock Information', fontsize=36)

ax1 = plt.subplot2grid(shape=(55, 2), loc=(0, 0), rowspan=30, colspan=2, fig=fig)
ax2 = ax1.twinx()
ax1.plot(my_df, label='Price')
ax1.set(xlabel='Year (YYYY)',
        ylabel='Price per Share (USD)')
ax2.plot(my_div, color='g', label='Dividend')
ax2.set(ylabel='Quarterly Dividends Paid (%)')
ax1.legend(loc=(0, 0.8))
ax2.legend(loc=(0, 0))

# The seocnd plot will have to do with the Balance Sheet, so I will just be plotting the short term/long term assets
# and the short term/long term liabilities

bal_df = pd.read_csv('balance_sheet/JPM_balance_sheet.csv', parse_dates=True, index_col='Unnamed: 0')

ax3 = plt.subplot2grid(shape=(55, 2), loc=(35, 0), rowspan=20, colspan=1, fig=fig)
ax3.plot(bal_df['ShortTermAssets'] / 10**6, label='ShortTermAssets')
ax3.plot(bal_df['TotalAssets'] / 10**6, label='TotalAssets')
ax3.plot(bal_df['ShortTermLiabilities'] / 10**6, label='ShortTermLiabilities')
ax3.plot(bal_df['TotalLiabilities'] / 10**6, label='TotalLiabilities')
ax3.set(xlabel='Date (YYYY-MM)',
        ylabel='Millions (USD)',
        title='Balance Sheet Information')
ax3.legend(loc=(0, 0))

# The third plot will have to do with EPS and revenues, hopefully plotted on the same chart, possibly sharing y scales
eps_df = pd.read_csv('eps/JPM_eps.csv', parse_dates=True, index_col='Unnamed: 0')
rev_df = pd.read_csv('revenue/JPM_revenue.csv', parse_dates=True, index_col= 'Unnamed: 0')

ax4 = plt.subplot2grid(shape=(55, 2), loc=(35, 1), rowspan=20, colspan=1, fig=fig)
ax4.plot(rev_df['TotalRevenue'] / 10**6, label='Revenue (Ann.)')
ax4.plot(rev_df['NetIncome'] / 10**6, label='Income (Ann.)')
ax4.set(xlabel='Date (YYYY-MM)',
        ylabel='Millions (USD)',
        title='Earnings Information')
ax5 = ax4.twinx()
ax5.plot(eps_df['EPS'], label='EPS (Qtrly)', color='g')
ax5.set(ylabel='Earnings Per Share Quarterly (USD)')
ax4.legend(loc=(0, 0))
ax5.legend(loc=(0.9, 0))