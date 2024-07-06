import unittest
import pandas as pd
from context import SolarPowerModel

class TestSolarPowerModel(unittest.TestCase):
    def test_set_solar_power(self):
        model = SolarPowerModel()
        model.set_load_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00'],
            'Load_kW': [100, 200]
        }))
        print(model.get_columns(columns=['Load_kW']))
        self.assertEqual(model.get_columns(columns=['Load_kW']).shape, (2, 1))

        model.set_irradiance_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00', '2022-01-01 02:00:00'],
            'DirectIrradiance': [100, 200, 300]
        }))
        print(model.get_dataset())
        print(model.get_columns(columns=['DirectIrradiance']))

        self.assertEqual(model.get_columns(columns=['DirectIrradiance']).shape, (3, 1))

        #model.append_irradiance_df(pd.DataFrame({
        #    'DateTime': ['2022-01-01 03:00:00', '2022-01-01 04:00:00'],
        #    'DirectIrradiance': [400, 500]
        #}))

        #print(model.get_columns(columns=['DirectIrradiance']))
        #self.assertEqual(model.get_columns(columns=['DirectIrradiance']).shape, (5, 1))
        
        model.set_belpex_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00'],
            'Belpex': [100, 200]
        }))
        print(model.get_columns(columns=['Belpex']))
        self.assertEqual(model.get_columns(columns=['Belpex']).shape, (3, 1))
    
    def test_get_total_cost(self):
        model = SolarPowerModel()
        model.set_load_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00'],
            'Load_kW': [100, 200]
        }))
        model.set_pv_power_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00'],
            'PV_Power_kW': [100, 200]
        }))
        model.set_belpex_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00'],
            'Belpex': [100, 200]
        }))
        model.power_flow()
        model.dynamic_tariff()
        self.assertEqual(model.get_total_cost(), 300)


if __name__ == '__main__':
    unittest.main()


