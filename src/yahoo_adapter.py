import requests
from datetime import datetime

import pandas as pd

from api_adapter import DataInterval
from api_adapter import ApiAdapter


class YahooFinanceApiAdapter(ApiAdapter):
    def get_financial_data(
        self, symbol: str, start: datetime, end: datetime, interval: DataInterval
    ):
        ...

    def _fetch_data(
        self, symbol: str, start: datetime, end: datetime, interval: DataInterval
    ) -> dict:
        """
        Create URL and fetch data from the Yahoo! Finance API
        :param symbol: ticker symbol for a stock
        :type symbol: str
        :param start: datetime to start collecting data from
        :type start: datetime
        :param end: datetime to end collecting data at
        :type end: datetime
        :param interval: frequency of data to collect
        :type interval: DataInterval
        :return: JSON response from Yahoo! Finance API parsed into a dictionary
        :rtype: dict
        """
        if symbol is None:
            raise TypeError("You must enter a symbol to fetch data for.")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"
        }
        interval_str = self._convert_data_interval(interval)
        url = (
            f"http://query1.finance.yahoo.com/v8/finance/chart/?symbol={symbol}&period1={int(start.timestamp())}"
            f"&period2={int(end.timestamp())}&interval={interval_str}&events=div"
        )
        return requests.get(url, headers=headers).json()

    def _validate_data(self, data: dict, interval: DataInterval) -> dict:
        interval_str = self._convert_data_interval(interval)
        if data["chart"]["error"]:
            raise ValueError("Invalid ticker data.")
        if interval_str not in data["chart"]["result"][0]["meta"]["validRanges"]:
            raise ValueError(f"Invalid interval range for a ticker: {interval_str}.")
        if not data["chart"]["result"][0]["indicators"]["adjclose"][0]["adjclose"]:
            raise ValueError(f"Did not get any price data for a ticker.")
        if not data["chart"]["result"][0]["events"]["dividends"]:
            raise ValueError(f"Did not get any dividends for a ticker")

        return data

    def _format_data(self, data: dict):
        price = data["chart"]["result"][0]["indicators"]["adjclose"][0]["adjclose"]
        price_timestamps = data["chart"]["result"][0]["timestamp"]
        dividends = data["chart"]["result"][0]["events"]["dividends"]

        price_df = pd.DataFrame(price, columns=["adj_close"])
        price_df["timestamp"] = price_timestamps
        price_df["timestamp"] = price_df["timestamp"].apply(datetime.fromtimestamp)
        price_df = price_df.set_index("timestamp")

        div_df = pd.DataFrame(
            [(ts, dividends[ts]["amount"]) for ts in dividends],
            columns=["timestamp", "dividend"],
        )
        div_df["timestamp"] = div_df["timestamp"].apply(datetime.fromtimestamp)
        div_df = div_df.set_index("timestamp")
        print(div_df)

    @staticmethod
    def _convert_data_interval(interval: DataInterval) -> str:
        if interval is DataInterval.DAILY:
            return "1d"
        if interval is DataInterval.WEEKLY:
            return "5d"
        if interval is DataInterval.MONTHLY:
            return "1mo"
        if interval is DataInterval.ANNUALLY:
            return "1y"


def convert_data_interval(interval: DataInterval) -> str:
    """
    Convert an instance of DataInterval enum into corresponding Yahoo! Finance string

    :param interval: interval to convert to a string
    :type interval: DataInterval
    :return: string Yahoo! Finance API uses to represent specified interval
    :rtype: str
    """
    if interval is DataInterval.DAILY:
        return "1d"
    if interval is DataInterval.WEEKLY:
        return "5d"
    if interval is DataInterval.MONTHLY:
        return "1mo"
    if interval is DataInterval.ANNUALLY:
        return "1y"


if __name__ == "__main__":
    y = YahooFinanceApiAdapter()
    start = datetime(day=1, month=1, year=2021)
    end = datetime(day=31, month=12, year=2021)
    d = y._fetch_data("AAPL", start, end, DataInterval.DAILY)
    d = y._validate_data(d, DataInterval.DAILY)
    y._format_data(d)
