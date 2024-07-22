
import unittest
from context import fetch_electricity_prices_xlsx, fetch_electricity_prices
class TestPriceFetching(unittest.TestCase):
    def test_fetch_price(self):
        print(fetch_electricity_prices_xlsx())
        self.assertEqual(fetch_electricity_prices().shape, (216, 1))
        #check if numeric
        self.assertTrue(fetch_electricity_prices()['Belpex'].dtype == 'float64')
        #check if datetimeindex
        self.assertTrue(fetch_electricity_prices().index.dtype == 'datetime64[ns]')


if __name__ == '__main__':
    unittest.main()