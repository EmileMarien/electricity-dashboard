import unittest
import pandas as pd
from context import SolarPowerModel
from context import fetch_electricity_prices

class TestSolarPowerModel(unittest.TestCase):
    def test_set_solar_power(self):
        model = SolarPowerModel()
        model.set_load_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00'],
            'Load_kW': [100, 200]
        }))
        #print(model.get_columns(columns=['Load_kW']))
        self.assertEqual(model.get_columns(columns=['Load_kW']).shape, (2, 1))

        model.set_irradiance_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00', '2022-01-01 02:00:00'],
            'DirectIrradiance': [100, 200, 300]
        }))
        #print(model.get_dataset())
        #print(model.get_columns(columns=['DirectIrradiance']))

        self.assertEqual(model.get_columns(columns=['DirectIrradiance']).shape, (3, 1))

        #TODO: model.append_irradiance_df(pd.DataFrame({
        #    'DateTime': ['2022-01-01 03:00:00', '2022-01-01 04:00:00'],
        #    'DirectIrradiance': [400, 500]
        #}))

        #print(model.get_columns(columns=['DirectIrradiance']))
        #self.assertEqual(model.get_columns(columns=['DirectIrradiance']).shape, (5, 1))
        
        model.set_belpex_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00'],
            'Belpex': [100, 200]
        }))
        #print(model.get_columns(columns=['Belpex']))
        self.assertEqual(model.get_columns(columns=['Belpex']).shape, (3, 1))
    
    def test_get_total_cost(self):
        model = SolarPowerModel()
        model.set_load_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00', '2022-01-01 02:00:00'],
            'Load_kW': [100, 200, 300]
        }))
        model.set_pv_power_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00', '2022-01-01 02:00:00'],
            'PV_Power_kW': [100, 200, 300]
        }))
        model.set_belpex_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00','2022-01-01 02:00:00'],
            'Belpex': [100, 200, 300]
        }))
        print(model.get_columns(columns=['Load_kW', 'PV_Power_kW', 'Belpex',]))
        model.power_flow()
        model.dynamic_tariff()
        print(model.get_columns(columns=['Load_kW', 'PV_Power_kW', 'Belpex', 'GridFlow', 'DynamicTariff','GridFlow_Load','DynamicTariff_Load']))
        self.assertEqual(round(model.get_total_cost()), 1285)

    def test_belpex_fetch_input(self):
        model=SolarPowerModel()
        model.set_belpex_df(fetch_electricity_prices())
        print(model.get_columns(columns=['Belpex']))

    # test calling SLP & SPP & when adding only single lines and converting to JSON

if __name__ == '__main__':
    unittest.main()


