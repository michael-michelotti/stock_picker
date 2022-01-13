from enum import Enum, auto
from datetime import datetime

from abc import ABC, abstractmethod


class DataInterval(Enum):
    DAILY = auto()
    WEEKLY = auto()
    MONTHLY = auto()
    ANNUALLY = auto()


class ApiAdapter(ABC):
    @abstractmethod
    def get_financial_data(
        self, symbol: str, start: datetime, end: datetime, interval: DataInterval
    ):
        ...

    @abstractmethod
    def _fetch_data(
        self, symbol: str, start: datetime, end: datetime, interval: DataInterval
    ):
        ...

    # @abstractmethod
    # def _validate_data(self, data):
    #     ...

    @abstractmethod
    def _format_data(self, data: dict):
        ...
