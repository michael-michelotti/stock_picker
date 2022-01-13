import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn import model_selection


ticker_dict = pickle.load(open('../archive/ticker_dict.pkl', 'rb'))

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