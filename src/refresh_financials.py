import os.path
import pickle

import tools
from setup_logger import logger


# I found a list of all stocks listed on the NYSE and the NASDAQ at the following URLs:
# NYSE: https://datahub.io/core/nyse-other-listings#resource-nyse-listed
# NASDAQ: https://datahub.io/core/nasdaq-listings
# S&P500: https://datahub.io/core/s-and-p-500-companies
# These have been saved in the root directory as "nyse-listed.csv", "nasdaq-listed.csv", and "sp500-listed.csv"

# I need to create a dictionary with every ticker symbol mapped to my custom Ticker object, which has built in
# methods to pull price and financials from the Yahoo Finance API.
def main():
    start_date_str = input('Please input your desired start date in YYYY-MM-DD format: ')
    start_date_epoch = tools.get_epoch_timestamp(start_date_str)
    end_date_str = input('Please input your desired end date in YYYY-MM-DD format: ')
    end_date_epoch = tools.get_epoch_timestamp(end_date_str)

    # Set default behavior for the case that the ticker_dict.pkl file doesn't already exist
    reuse = tools.get_reload_param('../archive/ticker_dict.pkl')
    if reuse:
        logger.info('Loading Ticker Dictionary...')
        ticker_dict = pickle.load(open('../archive/ticker_dict.pkl', 'rb'))
    else:
        if os.path.isfile('../archive/ticker_dict.pkl'):
            tools.archive_file('../archive/ticker_dict.pkl')
        logger.info('Now constructing Ticker Dictionary')
        custom = input('You can load symbols from the symbol_src subdirectory, or you can input your own list of '
                       'tickers. Would you like to input your own list of tickers? (Y/N): ')
        if custom == 'Y':
            custom_list = input('Please input your custom list, separated by commas (ex. AAPL, GOOGL, JPM): ')
            ticker_dict = tools.parse_custom_list(custom_list)
        else:
            ticker_dict = tools.load_symbol_src('../symbol_src')

    # I now need to iterate over the entire dictionary and populate my Ticker objects with their price and financials
    # DataFrames. They will also write all of the CSVs to my output directories.
    for ticker_num, ticker in enumerate(ticker_dict.values()):
        tools.full_ticker_run(ticker, start_date_epoch, end_date_epoch)
        with open('../archive/ticker_dict.pkl', 'wb') as file:
            pickle.dump(ticker_dict, file, protocol=pickle.HIGHEST_PROTOCOL)
        if ticker_num % 20 == 0:
            logger.info(f'Completed processing {ticker_num} out of {len(ticker_dict)} tickers')

    # Dump my big ticker dictionary to my root directory
    logger.info('Completed processing all tickers')
    with open('../archive/ticker_dict.pkl', 'wb') as file:
        pickle.dump(ticker_dict, file, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
