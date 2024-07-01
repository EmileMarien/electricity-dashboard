import unittest

from solarpowermodel.solarpowermodel import SolarPowerModel
import pandas as pd


class TestSolarPowerModel(unittest.TestCase):
    def test_set_solar_power(self):

        #print(model.get_dataset())
        self.assertEqual(model.get_dataset().shape, (2, 1))

if __name__ == '__main__':
    unittest.main()