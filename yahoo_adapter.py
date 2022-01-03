import requests
from datetime import datetime
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

    def _validate_data(self, data: dict, interval: DataInterval):
        interval_str = self._convert_data_interval(interval)
        if data["chart"]["error"]:
            raise ValueError("Invalid ticker data.")
        if interval_str not in data["chart"]["result"][0]['meta']['validRanges']:
            raise ValueError(f"Invalid interval range for a ticker: {interval_str}.")
        if not data["chart"]["result"][0]["indicators"]["adjclose"][0]['adjclose']:
            raise ValueError(f"Did not get any price/dividend data for a ticker.")

        data_dict = data["chart"]["result"][0]["indicators"]
        print(data_dict)

    def _format_data(self):
        ...

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


if __name__ == '__main__':
    y = YahooFinanceApiAdapter()
    start = datetime(day=1, month=1, year=2021)
    end = datetime(day=31, month=12, year=2021)
    d = y._fetch_data('AAPL', start, end, DataInterval.DAILY)
    y._validate_data(d, DataInterval.DAILY)
