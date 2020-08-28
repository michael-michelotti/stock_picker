import numpy as np
import pandas as pd
import requests
from datetime import datetime as dt
from time import sleep


# Yahoo Fundamentals: '/v10/finance/quoteSummary/{ticker}?modules='
# Yahoo Prices: '/v8/finance/chart/{ticker}?symbol={ticker}&period1=0&period2=9999999999&interval=3mo'
class Ticker:
    def __init__(self, symbol, start_date_epoch, end_date_epoch):
        self.symbol = symbol
        self.price = pd.DataFrame()
        self.dividends = pd.DataFrame()
        self.price_is_run = False
        self.balance_sheet = pd.DataFrame()
        self.eps = pd.DataFrame()
        self.income_statement = pd.DataFrame()
        self.financials_are_run = False
        self.combined_df = pd.DataFrame()
        self.combined_df_created = False
        self.combined_df_imputed = False
        self.start_date_epoch = start_date_epoch
        self.end_date_epoch = end_date_epoch

    # My first subplot will be a shared axis showing stock price and dividends over the last 10 years
    def run_price_and_dividends(self):
        if self.price_is_run:
            print(f'Price already loaded for {self.symbol}, skipping...')
        else:
            self.price_is_run = True
            print(f'\nBeginning Price and Dividend update for {self.symbol}')
            yahoo_api_base = 'query1.finance.yahoo.com'
            sleep(2)
            query_url = f'http://{yahoo_api_base}/v8/finance/chart/{self.symbol}?symbol={self.symbol}&period1=' \
                        f'{int(self.start_date_epoch)}&period2={int(self.end_date_epoch)}&interval=1mo&events=div'
            json = requests.get(query_url).json()
            if json['chart']['error']:
                print(f'{self.symbol} error: {json["chart"]["error"]["description"]}. Skipping financials')
                self.financials_are_run = True
                return
            if '1mo' not in json['chart']['result'][0]['meta']['validRanges']:
                print(f'1 month is not a valid price sample rate for {self.symbol}. Skipping price.')
                return
            if not json['chart']['result'][0]['indicators']['adjclose'][0]:
                print(f'Did not get any prices for {self.symbol}, but not sure why (no error but blank query). '
                      f'Skipping financials')
                self.financials_are_run = True
                return

            # Had to tease the values out of a lot of levels of this JSON reply!
            price_list = json['chart']['result'][0]['indicators']['adjclose'][0]['adjclose']
            self.price = pd.DataFrame(price_list, columns=['Price'])

            # Teased the timestamp out of the JSON response as well, and set the index of my price DF to that for a
            # Pandas datetime index
            self.price['Timestamp'] = json['chart']['result'][0]['timestamp']
            self.price['Timestamp'] = self.price['Timestamp'].apply(lambda x: dt.fromtimestamp(x))
            self.price.set_index('Timestamp', inplace=True)
            self.price.to_csv(f'prices/{self.symbol}_price.csv')

            # I want to create a dividends spreadsheet as well. I can tease the information out of the JSON response
            try:
                dividends_dict = json['chart']['result'][0]['events']['dividends']
                div_timestamps, div_values = [], []
                for v in dividends_dict.values():
                    div_timestamps.append(dt.fromtimestamp(v['date']))
                    div_values.append(v['amount'])
                self.dividends = pd.DataFrame(div_values, index=div_timestamps, columns=['Dividend'])
                self.dividends.index.rename('Timestamp', inplace=True)
                self.dividends.sort_index(inplace=True)
                self.dividends.to_csv(f'dividends/{self.symbol}_dividends.csv')
            except KeyError:
                print(f'Dividends not found for {self.symbol}. They may not pay out dividends.')

    # There are three CSVs that I'm creating from the run_financials section. I'm using the Balance Sheet to create a
    # "Assets vs Liabilities" table. I'm using the Earnings History to create a table of last years Earnings Per Share.
    # I'm using the Income Statement to make a table of revenues and profits.
    # Unclear as of right now exactly how these might fit into a plot.
    def run_financials(self):
        if self.financials_are_run:
            print(f'Financials skipping for {self.symbol}...')
        else:
            self.financials_are_run = True
            print(f'Beginning Financials update for {self.symbol}')
            yahoo_api_base = 'query1.finance.yahoo.com'
            # BALANCE SHEET SECTION
            sleep(2)
            query_url = f'http://{yahoo_api_base}/v10/finance/quoteSummary/{self.symbol}?modules=balanceSheetHistory'
            json = requests.get(query_url).json()
            if json['quoteSummary']['error']:
                print(json['quoteSummary']['error']['description'])
            else:
                # The below is a list where each element is one year
                annual_balance_sheet = json['quoteSummary']['result'][0]['balanceSheetHistory']['balanceSheetStatements']

                # Pull all of our parameters of interest into a Python list to use as columns for a Pandas DataFrame
                balance_timestamps = []
                short_term_assets, total_assets = [], []
                short_term_liabilities, total_liabilities = [], []
                fields = ['totalCurrentAssets', 'totalAssets', 'totalCurrentLiabilities', 'totalLiab']
                for year in annual_balance_sheet:
                    if all(fields in year for fields in fields):
                        if year['totalCurrentAssets'] and year['totalAssets'] and year['totalCurrentLiabilities'] and year['totalLiab']:
                            balance_timestamps.append(year['endDate']['fmt'])
                            short_term_assets.append(year['totalCurrentAssets']['raw'])
                            total_assets.append(year['totalAssets']['raw'])
                            short_term_liabilities.append(year['totalCurrentLiabilities']['raw'])
                            total_liabilities.append(year['totalLiab']['raw'])

                if balance_timestamps:
                    self.balance_sheet = pd.DataFrame({'ShortTermAssets': short_term_assets, 'TotalAssets': total_assets,
                                                       'ShortTermLiabilities': short_term_liabilities,
                                                       'TotalLiabilities': total_liabilities},
                                                      index=pd.to_datetime(balance_timestamps))
                    self.balance_sheet.index.rename('Timestamp', inplace=True)
                    self.balance_sheet.to_csv(f'balance_sheet/{self.symbol}_balance_sheet.csv')
                else:
                    print(f'Did not receive any Balance Sheet information for {self.symbol}')

            # EPS SECTION
            sleep(2)
            query_url = f'http://{yahoo_api_base}/v10/finance/quoteSummary/{self.symbol}?modules=earningsHistory'
            json = requests.get(query_url).json()
            if json['quoteSummary']['error']:
                print(json['quoteSummary']['error']['description'])
            else:
                # List of each quarter for the last year
                quarterly_eps = json['quoteSummary']['result'][0]['earningsHistory']['history']
                eps_timestamp, eps = [], []
                fields = ['quarter', 'epsActual']
                for quarter in quarterly_eps:
                    if all(fields in quarter for fields in fields):
                        if quarter['quarter'] and quarter['epsActual']:
                            eps_timestamp.append(quarter['quarter']['fmt'])
                            eps.append(quarter['epsActual']['raw'])
                if eps_timestamp:
                    self.eps = pd.DataFrame({'EPS': eps}, index=pd.to_datetime(eps_timestamp))
                    self.eps.index.rename('Timestamp', inplace=True)
                    self.eps.to_csv(f'eps/{self.symbol}_eps.csv')
                else:
                    print(f'Did not receive any EPS data for {self.symbol}')

            # REVENUE SECTION
            sleep(2)
            query_url = f'http://{yahoo_api_base}/v10/finance/quoteSummary/{self.symbol}?modules=incomeStatementHistory'
            json = requests.get(query_url).json()
            if json['quoteSummary']['error']:
                print(json['quoteSummary']['error']['description'])
            else:
                # List of annual income statement each year for the last 4 years
                annual_income_statement = json['quoteSummary']['result'][0]['incomeStatementHistory']['incomeStatementHistory']
                revenue_timestamp = []
                total_revenue, gross_profit, net_income = [], [], []
                fields = ['totalRevenue', 'grossProfit', 'netIncome']
                for year in annual_income_statement:
                    if all(fields in year for fields in fields):
                        if year['totalRevenue'] and year['grossProfit'] and year['netIncome']:
                            revenue_timestamp.append(year['endDate']['fmt'])
                            total_revenue.append(year['totalRevenue']['raw'])
                            gross_profit.append(year['grossProfit']['raw'])
                            net_income.append(year['netIncome']['raw'])

                if revenue_timestamp:
                    self.income_statement = pd.DataFrame({'TotalRevenue': total_revenue, 'GrossProfit': gross_profit,
                                                          'NetIncome': net_income}, index=pd.to_datetime(revenue_timestamp))
                    self.income_statement.index.rename('Timestamp', inplace=True)
                    self.income_statement.to_csv(f'revenue/{self.symbol}_revenue.csv')
                else:
                    print(f'Did not receive any revenue data for {self.symbol}')

    def impute_combined_df(self, column_name):
        if not self.combined_df_created:
            print(f'Combined DF is not created for {self.symbol}. Cannot impute')
        else:
            price_nulls = self.combined_df[self.combined_df[column_name].isnull()].index
            for nulls in price_nulls:
                null_loc = self.combined_df.index.get_loc(nulls)
                if np.isnan(self.combined_df[column_name].iloc[null_loc]):
                    og_null_loc = null_loc
                    total_nulls = 1
                    ends_with_null = False
                    starts_with_null = False
                    while np.isnan(self.combined_df[column_name].iloc[null_loc]):
                        if null_loc == 0:
                            starts_with_null = True
                        if null_loc == len(self.combined_df[column_name]) - 1:
                            ends_with_null = True
                            break
                        if np.isnan(self.combined_df[column_name].iloc[null_loc + 1]):
                            total_nulls += 1
                        null_loc += 1

                    first_point = og_null_loc - 1
                    second_point = null_loc

                    if ends_with_null:
                        impute_value = self.combined_df[column_name].iloc[first_point]
                        self.combined_df[column_name].iloc[og_null_loc:] = impute_value
                    elif starts_with_null:
                        impute_value = self.combined_df[column_name].iloc[null_loc]
                        self.combined_df[column_name].iloc[:null_loc] = impute_value
                    else:
                        rise = self.combined_df[column_name].iloc[second_point] - self.combined_df[column_name].iloc[first_point]
                        run = second_point - first_point
                        slope = np.divide(rise, run)
                        for nums in np.arange(start=1, stop=total_nulls + 1):
                            self.combined_df[column_name].iloc[first_point + nums] = slope * nums + self.combined_df[column_name].iloc[first_point]

    def create_combined_df(self):
        if self.dividends.empty:
            self.combined_df = pd.concat([self.price, self.balance_sheet, self.income_statement],
                                         axis=1, join='outer')
            self.combined_df['Dividend'] = 0
        else:
            self.combined_df = pd.concat([self.price, self.dividends, self.balance_sheet, self.income_statement],
                                         axis=1, join='outer')

        self.combined_df_created = True
        self.combined_df.to_csv(f'combined_dfs/{self.symbol}_combined_df.csv')

    def slice_df_on_revenue(self):
        if self.combined_df_created:
            filt = self.combined_df['TotalRevenue'].notnull()
            first_revenue = self.combined_df[filt].index[0]
            self.combined_df = self.combined_df.loc[first_revenue:]
        else:
            print(f'Combined DF is not created for {self.symbol}. Cannot slice')

