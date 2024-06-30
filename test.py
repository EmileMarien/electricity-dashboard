import unittest

from solarpowermodel.solarpowermodel import SolarPowerModel
import pandas as pd


class TestSolarPowerModel(unittest.TestCase):
    def test_set_solar_power(self):
        model = SolarPowerModel()
        model.set_load_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00'],
            'Load_kW': [100, 200]
        }))
        #print(model.get_dataset())
        self.assertEqual(model.get_dataset().shape, (2, 1))

if __name__ == '__main__':
    unittest.main()