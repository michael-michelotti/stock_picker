import math
import pytest
from src import tools
import time
# from src.ticker import Ticker


def test_get_epoch_timestamp():
    assert math.isclose(tools.get_epoch_timestamp('2020-08-20'), 1597906800.0)
    assert math.isclose(tools.get_epoch_timestamp('1973-01-01'), 94723200.0)

    with pytest.raises(TypeError):
        tools.get_epoch_timestamp(20200820)

    time.sleep(5)

    with pytest.raises(ValueError):
        tools.get_epoch_timestamp('2020-8-20')
    with pytest.raises(ValueError):
        tools.get_epoch_timestamp('1969-01-03')
    with pytest.raises(ValueError):
        tools.get_epoch_timestamp('3001-01-01')


def test_progress():
    time.sleep(5)
    assert 1 == 1


def test_progress_again():
    time.sleep(5)
    assert 1 == 1


# def test_archive_file(self):
#     with self.assertRaises(TypeError):
#         tools.archive_file(3021)
#     with self.assertRaises(TypeError):
#         tools.archive_file(['ticker_dict.pkl'])
#     with self.assertRaises(FileNotFoundError):
#         tools.archive_file('fake_file.txt')
#     with self.assertRaises(ValueError):
#         tools.archive_file('')


# def test_parse_custom_list(self):
#     result = tools.parse_custom_list('AAPL, GOOGL')
#
#     self.assertEqual(len(result), 2)
#     self.assertEqual(type(result), dict)
#     self.assertIsInstance(result['AAPL'], Ticker)
#     self.assertIsInstance(result['GOOGL'], Ticker)
#
#     # Not properly handling a tab or underscore delimiter right now
#     with self.assertRaises(ValueError):
#         tools.parse_custom_list('AAPL.GOOGL')
#     with self.assertRaises(ValueError):
#         tools.parse_custom_list('AAPL, 2GOOG')
#     # with self.assertRaises(ValueError):
#     #     tools.parse_custom_list('AAPL   GOOG')
#     with self.assertRaises(ValueError):
#         tools.parse_custom_list('')
#     with self.assertRaises(TypeError):
#         tools.parse_custom_list(23)
#     with self.assertRaises(TypeError):
#         tools.parse_custom_list(['AAPL', 'GOOGL'])
#     with self.assertRaises(TypeError):
#         tools.parse_custom_list(set('AAPL', 'GOOGL'))
#
#
# def test_load_symbol_src(self):
#     result = tools.load_symbol_src('../dev_data')
#     self.assertEqual(type(result), dict)
#
#     with self.assertRaises(TypeError):
#         tools.load_symbol_src(234)
#     with self.assertRaises(ValueError):
#         tools.load_symbol_src('')
#     with self.assertRaises(FileNotFoundError):
#         tools.load_symbol_src('fakedir2030912')
