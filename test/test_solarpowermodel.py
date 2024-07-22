import json
import unittest
import numpy as np
import pandas as pd
from context import SolarPowerModel
from context import fetch_electricity_prices
from features.solarpower.models.battery.battery import Battery

from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.document import DocumentReference



class TestSolarPowerModel(unittest.TestCase):
    def test_set_solar_power(self):
        model = SolarPowerModel()
        model.set_load_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00'],
            'Load_kW': [100, 200]
        }))
        model.yearly_consumption_energy=300
        #print(model.get_columns(columns=['Load_kW']))
        self.assertEqual(model.get_columns(columns=['Load_kW']).shape, (2, 1))

        model.set_yearly_consumption_energy(200)
        print(model.get_columns(columns=['Load_kW']))
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
        #TODO: test setters better (removal of other columns, etc)
    
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
        #print(model.get_columns(columns=['Load_kW', 'PV_Power_kW', 'Belpex']))
        model.update_power_flow()
        model.update_dynamic_tariff()
        #print(model.get_columns(columns=['Load_kW', 'PV_Power_kW', 'Belpex', 'GridFlow', 'DynamicTariff','GridFlow_Load','DynamicTariff_Load']))
        self.assertEqual(round(model.get_total_cost()), 1301)
        model.append_pv_power_df(pd.DataFrame({
            'DateTime': ['2022-01-01 03:00:00', '2022-01-01 04:00:00'],
            'PV_Power_kW': [400, 500]
        }))
        #print(model.get_columns(columns=['Load_kW', 'PV_Power_kW', 'Belpex', 'GridFlow']))
        model.append_belpex_df(pd.DataFrame({
            'DateTime': ['2022-01-01 03:00:00', '2022-01-01 04:00:00'],
            'Belpex': [400, 500]
        }))
        model.append_load_df(pd.DataFrame({
            'DateTime': ['2022-01-01 03:00:00', '2022-01-01 04:00:00'],
            'Load_kW': [400, 500]
        }))
        model.update_power_flow()
        

    def test_belpex_fetch_input(self):
        model=SolarPowerModel()
        model.set_belpex_df(fetch_electricity_prices())
        #print(model.get_columns(columns=['Belpex']))

    # test calling SLP & SPP & when adding only single lines and converting to JSON

    def test_databasefunctions(self):
        model=SolarPowerModel(battery=Battery(battery_type="LG RESU Prime 16"))
        model.set_load_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00'],
            'Load_kW': [100, 200]
        }))
        #print(model.get_dataset().columns)
        #print(model.to_dict())

        json_file=model.__dict__
        #print(json)
        # Creating a new instance of the SolarPowerModel
        new_model = SolarPowerModel.__new__(SolarPowerModel)

        # Updating the new instance's __dict__ with the saved state
        new_model.__dict__.update(json_file)
        self.assertEqual(model.__dict__, new_model.__dict__)
        # Now the new_model should be an exact copy of the original model
        #print(new_model.__dict__)
        #print(model.battery.__dict__)
        #print(new_model.battery.__dict__)
        self.assertEqual(model.battery.__dict__, new_model.battery.__dict__)

        self.assertEqual(model.reference_id, None)

        #model_with_id=model.from_snapshot(snapshot=DocumentSnapshot(reference=DocumentReference(id="123"), data={"battery_type":"LG RESU Prime 16"}, exists=True,read_time=None,create_time=None,update_time=None))
        #self.assertEqual(model_with_id.reference_id,"123") TODO: check with real firestore link
    
    #def test_solarpowerstate():
        #state=SolarPowerState()
        #state.set_SLP()
    def test_SLP_fillin(self):
        model=SolarPowerModel()
        model.set_load_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00'],
            'Load_kW': [100, np.nan]
        }))
        model.append_load_df(pd.DataFrame({
            'DateTime': ['2020-01-01 01:00:00', '2020-01-01 02:00:00', '2020-01-01 03:00:00'],
            'Load_kW': [200, 300, 400]
        }),SLP=True)
        print(model.get_columns(columns=['Load_kW']))
        self.assertEqual(model.get_columns(columns=['Load_kW']).shape, (2, 1))

if __name__ == '__main__':
    unittest.main()


