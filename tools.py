import pandas as pd
import re
import os
import os.path
import shutil
import logging
from datetime import datetime
from ticker import Ticker
from glob import glob


def get_epoch_timestamp(date_str):
    """
    Takes in a string in "YYYY-MM-DD" format. Returns the two dates in UTC Timestamp format. Valid date range:
    1970-01-02 -> 3000-12-31
    :return: UTC Epoch Timestamp parsed from string input
    """
    if not type(date_str) == str:
        raise TypeError('Date input must be a string')
    if not re.search(r'\d{4}-\d{2}-\d{2}', date_str):
        raise ValueError('Date string must be of format "YYYY-MM-DD"')
    parsed_dt = datetime.strptime(date_str, '%Y-%m-%d')
    if parsed_dt < datetime(1970, 1, 2) or datetime(3000, 12, 31) < parsed_dt:
        raise ValueError('Invalid date range. Select a date between 1970-01-02 and 3000-12-31')
    return parsed_dt.timestamp()


def archive_file(file_name):
    """
    Takes in a file name as a string and moves that file from the root stock_picker directory to the "archive"
    sub-directory, tagged with the year, month, day, hour, and minute
    :param: file_name: Name of file to archive in string format
    :return: None
    """
    if not type(file_name) == str:
        raise TypeError('File name must be a string')
    if not file_name:
        raise ValueError('File name cannot be empty')
    if not os.path.isfile(file_name):
        raise FileNotFoundError('This file does not exist in the root directory')
    logging.info(f'Saving {file_name} to archive folder...')
    shutil.move(f'{file_name}', 'archive')
    curr = datetime.now()
    name, ext = os.path.splitext(file_name)
    os.rename(f'archive/{file_name}',
              'archive/{}_{}-{:02d}{:02d}{}'.format(name, curr.date(), curr.hour, curr.minute, ext))


def parse_custom_list(cus_str):
    """
    Takes in a comma separated string of stock symbols and returns a dictionary where the keys are the symbols and
    the values are Ticker objects created from those symbols
    :param cus_str: Comma separated string of stock symbols
    :return: Dictionary of Ticker objects based on input symbols
    """
    if not type(cus_str) == str:
        raise TypeError('Custom list input must be a string')
    cus_list = cus_str.split(',')
    filt_set = {ticker.strip() for ticker in cus_list if not re.search(r'[\W]', ticker.strip())}
    return {symbol: Ticker(symbol) for symbol in filt_set}


def load_symbol_src():
    """
    Loads in all files of .csv format from the symbol_src directory. Parses symbols from any column that has "Symbol"
    in the title. Symbols which contain anything other than word characters (A-Z, a-z, 0-9) will be discarded.
    :return: Dictionary of Ticker objects based on symbols parsed from symbol_src directory
    """
    load_files = glob('symbol_src/*.csv')
    dfs = [pd.read_csv(file) for file in load_files]
    symbol_series = pd.Series(dtype=str)
    for df in dfs:
        symbol_series = symbol_series.append(df['Symbol'])

    filt_set = {symbol for symbol in symbol_series if not re.search(r'[\W]', symbol)}
    return {symbol: Ticker(symbol) for symbol in filt_set}


def full_ticker_run(ticker, start_timestamp, end_timestamp):
    """
    Takes in a Ticker object and runs its "run_price_and_dividends" and "run_financials" methods. Returns the same
    Ticker object containing new financials information.
    :param ticker: Ticker object to pull all financials
    :param start_timestamp: UTC timestamp to mark start date of price and dividend query
    :param end_timestamp: UTC timestamp to mark end date of price and dividend query
    :return: Ticker object with financial information
    """
    ticker.start_date_epoch = start_timestamp
    ticker.end_date_epoch = end_timestamp
    try:
        ticker.run_price_and_dividends()
    except Exception as err:
        logging.error(f'Following error reported: {err}. Most likely Yahoo closed out connection')
        input('Input any character when you are ready to continue (probably wait a bit)')
    try:
        ticker.run_financials()
    except Exception as err:
        logging.error(f'Following error reported: {err}. Most likely Yahoo closed out connection')
        input('Input any character when you are ready to continue (probably wait a bit)')
    return ticker


def get_reload_param(file_name):
    """
    Takes in a file name. Checks whether the file name exists in the root directory, and queries user whether they
    would like to reuse that file for the current run.
    :param file_name: Name of file that user may want to reload
    :return: True if user requests a reload, False if they do not
    """
    reload_input_flag = False
    if os.path.isfile(file_name):
        reload = input(f'{file_name} already exists from previous run. '
                       f'Would you like to continue working with {file_name} (Y/N): ')
        reload_input_flag = True
        if reload == 'Y':
            return True
    if reload_input_flag:
        verify = input(f'Are you sure you want to continue? This will write over {file_name} (Y/N): ')
        if verify == 'Y':
            return False
        else:
            get_reload_param(file_name)
    else:
        return False


if __name__ == '__main__':
    archive_file('fake_file')