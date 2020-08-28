import pandas as pd
import re
import os
import pickle
import sys
from datetime import datetime
from Ticker import Ticker
from pickle import dump, load
from shutil import move
from os.path import isfile


start_date = input('Please input your desired start date in YYYY-MM-DD format: ')
end_date = input('Please input your desired end date in YYYY-MM-DD format: ')

# I need to convert my date inputs from strings into Python datetime objects
start_date = datetime.strptime(start_date, '%Y-%m-%d')
end_date = datetime.strptime(end_date, '%Y-%m-%d')

# I need to convert my dates into Unix epoch time, as that is the date format used by the Yahoo Finance API
start_date_epoch = start_date.timestamp()
end_date_epoch = end_date.timestamp()

# I found a list of all stocks listed on the NYSE and the NASDAQ at the following URLs:
# NYSE: https://datahub.io/core/nyse-other-listings#resource-nyse-listed
# NASDAQ: https://datahub.io/core/nasdaq-listings
# S&P500: https://datahub.io/core/s-and-p-500-companies
# These have been saved in the root directory as "nyse-listed.csv", "nasdaq-listed.csv", and "sp500-listed.csv"

# I need to create a dictionary with every ticker symbol mapped to my custom Ticker object, which has built in
# methods to pull price and financials from the Yahoo Finance API.
reuse_input_flag = False
reuse = 'N'
verify = 'Y'
if isfile('ticker_dict.pkl'):
    reuse = input('Ticker Dictionary already exists from previous run. '
                  'Would you like to continue writing to that dictionary (Y/N): ')
    reuse_input_flag = True
if reuse == 'Y':
    print('\nLoading Ticker Dictionary...')
    ticker_dict = load(open('ticker_dict.pkl', 'rb'))
else:
    if reuse == 'N' and reuse_input_flag:
        verify = input('Are you sure you want to continue? This will start over your Ticker Dictionary (Y/N): ')
    if verify == 'Y':
        if isfile('ticker_dict.pkl'):
            print('Saving old Ticker Dictionary to archive folder...')
            move('ticker_dict.pkl', f'archive/')
            now = datetime.now()
            os.rename(f'archive/ticker_dict.pkl', f'archive/ticker_dict_{now.year}_{now.month}_{now.day}.pkl')
        print('\nConstructing Ticker Dictionary')
        custom = input('You can load all NYSE, NASDAQ, and S&P500 tickers from the root directory CSV files, or you can'
                       ' input your own list of tickers. Would you like to input your own list of tickers?  (Y/N): ')
        if custom == 'Y':
            custom_list = input('Please input your custom list, separated by commas (ex. AAPL, GOOGL, JPM): ')
            custom_list = custom_list.split(',')
            custom_list = [item.strip() for item in custom_list]
            filtered_set = set(custom_list)
        else:
            nyse_df = pd.read_csv('nyse-listed.csv')
            nasdaq_df = pd.read_csv('nasdaq-listed.csv')
            sp500_df = pd.read_csv('sp500-listed.csv')

            ticker_set = {ticker for ticker in nyse_df['ACT Symbol']}
            for ticker in nasdaq_df['Symbol']:
                ticker_set.add(ticker)
            for ticker in sp500_df['Symbol']:
                ticker_set.add(ticker)
            filtered_set = [ticker for ticker in ticker_set if not re.search(r'[\W]', ticker)]

        ticker_dict = dict()
        for symbol in filtered_set:
            ticker_dict.update({symbol: Ticker(symbol, start_date_epoch, end_date_epoch)})
    else:
        sys.exit('Please verify whether you want to load an old ticker dictionary, or start a new one')

# I now need to iterate over the entire dictionary and populate my Ticker objects with their price and financials
# DataFrames. They will also write all of the CSVs to my output directories.
for ticker in ticker_dict.values():
    try:
        ticker.run_price_and_dividends()
    except Exception as e:
        print(f'Following error reported: {e}. Most likely Yahoo closed out connection')
        cont = input('Input "Y" when you are ready to continue (probably wait a bit)')
    try:
        ticker.run_financials()
    except Exception as e:
        print(f'Following error reported: {e}. Most likely Yahoo closed out connection')
        cont = input('Input "Y" when you are ready to continue (probably wait a bit)')

    with open('ticker_dict.pkl', 'wb') as file:
        dump(ticker_dict, file, protocol=pickle.HIGHEST_PROTOCOL)

# Dump my big ticker dictionary to my root directory
with open('ticker_dict.pkl', 'wb') as file:
    dump(ticker_dict, file, protocol=pickle.HIGHEST_PROTOCOL)
