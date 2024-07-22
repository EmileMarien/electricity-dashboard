

import pandas as pd
from features.solarpower.models.battery.battery import Battery
from features.solarpower.models.solarpowermodel.solarpowermodel import SolarPowerModel
from features.solarpower.states.solarpowerstate import SolarPowerState
from features.solarpower.models.inverter.inverter import Inverter
from features.solarpower.models.solarpanel.solarpanel import SolarPanel

# TODO: this should call the API
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
    
    def refresh_SPP(self):
        return self.state.set_SPP()
    
    def load_model(self):
        self.state.load_model()

    def upload_model(self):
        return self.state.upload_model()
    
    def get_SLP_belpex(self):
        return self.state.get_columns(columns=['Load_kW', 'Belpex'])
    
    def get_peak_power(self):
        return self.state.get_peak_power()
    
    def update_model(self):
        self.state.update_belpex()
        self.state.update_SLP()
        self.state.update_SPP()
        self.state.update_calculations()
        return None
    
    def change_model(self, battery_type=None, inverter_type=None, solarpanel_type=None, peak_production_power=None, yearly_consumption_energy=None, solarpanel_count=None):

        return self.state.change_model(battery_type=battery_type, inverter_type=inverter_type, solarpanel_type=solarpanel_type,peak_production_power=peak_production_power,yearly_consumption_energy=yearly_consumption_energy,solarpanel_count=solarpanel_count)   #TODO: model parameters are not really changed after pushing the button
    
    def get_solarpanelname(self):
        return self.state.solarpowermodel.get_solarpanel().get_solarpanel_type()
    
    def get_batteryname(self):
        return self.state.solarpowermodel.get_battery().get_battery_type()
    
    def get_invertername(self):
        return self.state.solarpowermodel.get_inverter().get_inverter_type()
