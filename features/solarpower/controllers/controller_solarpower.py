

import pandas as pd
from features.solarpower.models.solarpowermodel.solarpowermodel import SolarPowerModel
from features.solarpower.states.solarpowerstate import SolarPowerState


class ControllerSolarPower:
    def __init__(self):
        self.model = SolarPowerModel() #TODO: model should not be accessible from here
        self.state = SolarPowerState()
        
    def get_gridflow(self):
        self.model.set_load_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00', '2022-01-01 02:00:00'],
            'Load_kW': [100, 200, 300]
        }))
        self.model.set_pv_power_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00', '2022-01-01 02:00:00'],
            'PV_Power_kW': [100, 200, 300]
        }))
        self.model.set_belpex_df(pd.DataFrame({
            'DateTime': ['2022-01-01 00:00:00', '2022-01-01 01:00:00','2022-01-01 02:00:00'],
            'Belpex': [100, 200, 300]
        }))
        self.model.update_power_flow()
        return self.model.get_columns(columns=['Load_kW', 'PV_Power_kW', 'Belpex'])
    
    def refresh_SLP(self):
        return self.state.set_SLP()
    
    def load_model(self):
        self.state.load_model()

    def upload_model(self):
        self.state.upload_model()