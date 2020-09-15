import unittest
import tools
from ticker import Ticker


class TestTools(unittest.TestCase):

    def test_get_epoch_timestamp(self):
        self.assertEqual(tools.get_epoch_timestamp('2020-08-20'), 1597906800.0)
        self.assertEqual(tools.get_epoch_timestamp('1973-01-01'), 94723200.0)

        with self.assertRaises(TypeError):
            tools.get_epoch_timestamp(20200820)

        with self.assertRaises(ValueError):
            tools.get_epoch_timestamp('2020-8-20')
        with self.assertRaises(ValueError):
            tools.get_epoch_timestamp('1969-01-03')
        with self.assertRaises(ValueError):
            tools.get_epoch_timestamp('3001-01-01')

    def test_archive_file(self):
        with self.assertRaises(TypeError):
            tools.archive_file(3021)
        with self.assertRaises(TypeError):
            tools.archive_file(['ticker_dict.pkl'])
        with self.assertRaises(FileNotFoundError):
            tools.archive_file('fake_file.txt')
        with self.assertRaises(ValueError):
            tools.archive_file('')

    # def test_parse_custom_list(self):
    #     self.assertEqual(tools.parse_custom_list('AAPL, GOOGL'))


if __name__ == '__main__':
    unittest.main()
