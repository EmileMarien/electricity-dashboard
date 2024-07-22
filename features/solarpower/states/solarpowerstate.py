
# performs the logic when which has to run



from features.solarpower.models.battery.battery import Battery
from core.firestore_init import authenticate_to_firestore, load_key
from features.solarpower.repositories.data_repository_belpex import DataRepositoryBelpex
from features.solarpower.repositories.data_repository_solarmodel import DataRepositorySolarModel
from features.solarpower.repositories.data_repository_syntheticprofiles import DataRepositorySLP, DataRepositorySPP
from features.solarpower.models.solarpowermodel.solarpowermodel import SolarPowerModel
from features.solarpower.models.syntheticprofilefetching.syntheticprofilefetching import SLP_xls_to_pd, SPP_xls_to_pd
from features.solarpower.models.pricefetching.pricefetching import fetch_electricity_prices, fetch_electricity_prices_xlsx
from features.solarpower.models.inverter.inverter import Inverter
from features.solarpower.models.solarpanel.solarpanel import SolarPanel

#TODO: this should be the api

class SolarPowerState():
    def __init__(self):
        firestor_reference=authenticate_to_firestore(load_key())
        self.solarpowermodel=SolarPowerModel()
        self.data_repository_belpex=DataRepositoryBelpex(firestore_reference=firestor_reference)
        self.data_repository_solarmodel=DataRepositorySolarModel(firestore_reference=firestor_reference)
        self.data_repository_SLP=DataRepositorySLP(firestore_reference=firestor_reference)
        self.data_repository_SPP=DataRepositorySPP(firestore_reference=firestor_reference)
        self.solarpowermodel.set_reference_id('test')
    
    def get_total_savings(self):
        return self.solarpowermodel.get_total_cost()
    
    def get_total_production(self):
        return self.solarpowermodel.get_energy_TOT(column_name='PV_Power_kW')
    
    def set_SLP(self):
        SLP=SLP_xls_to_pd('data/slp_enu_cons.xls')
        self.data_repository_SLP.add_SLP(SLP=SLP)
        return None

    def set_SPP(self):
        SPP=SPP_xls_to_pd('data/SPP_2022_(Ex-ante_and_Ex-post)_v1_0_prod.xlsx')
        self.data_repository_SPP.add_SPP(SPP=SPP)
        return None
       
    
    def load_model(self):
        self.solarpowermodel=self.data_repository_solarmodel.get_model(reference_id=self.solarpowermodel.get_reference_id() if self.solarpowermodel.get_reference_id() is not None else 'test')
    
    def upload_model(self):
        id=self.data_repository_solarmodel.add_model(model=self.solarpowermodel)
        if self.solarpowermodel.get_reference_id() is None:
            self.solarpowermodel.set_reference_id(id)
        return None
    
    def update_belpex(self):
        prices=fetch_electricity_prices()
        self.data_repository_belpex.update(prices)
        all_prices=self.data_repository_belpex.get_belpex()

        self.solarpowermodel.append_belpex_df(all_prices)

        self.data_repository_solarmodel.update(self.solarpowermodel,fields_to_update={"dataframe": self.solarpowermodel.pd.rename(index=lambda x: x.strftime('%Y-%m-%d %H:%M:%S %Z')).to_dict(orient='index')})
        return all_prices

    def update_SLP(self):
        self.solarpowermodel.append_load_df(self.data_repository_SLP.get_SLP(),SLP=True)    #TODO: change to set_load_df
        self.data_repository_solarmodel.update(self.solarpowermodel,fields_to_update={"dataframe": self.solarpowermodel.pd.rename(index=lambda x: x.strftime('%Y-%m-%d %H:%M:%S %Z')).to_dict(orient='index')})            

    def update_SPP(self):
        self.solarpowermodel.append_pv_power_df(self.data_repository_SPP.get_SPP(),SPP=True)
        self.data_repository_solarmodel.update(self.solarpowermodel,fields_to_update={"dataframe": self.solarpowermodel.pd.rename(index=lambda x: x.strftime('%Y-%m-%d %H:%M:%S %Z')).to_dict(orient='index')})

    def update_calculations(self):
        self.solarpowermodel.update_power_flow()
        self.solarpowermodel.update_dual_tariff()
        self.solarpowermodel.update_dynamic_tariff()
        self.data_repository_solarmodel.update(self.solarpowermodel,fields_to_update={"dataframe": self.solarpowermodel.pd.rename(index=lambda x: x.strftime('%Y-%m-%d %H:%M:%S %Z')).to_dict(orient='index')})
        return "calculations updated"

    def get_columns(self,columns):
        return self.solarpowermodel.get_columns(columns=columns)
    
    def get_peak_power(self):
        return self.solarpowermodel.solarpanel.get_peak_power()
    
    def change_model(self,battery_type=None, inverter_type=None, solarpanel_type=None, peak_production_power=None, yearly_consumption_energy=None, solarpanel_count=None):
        """
        Checks if the provided components differ from the current installed ones and if so, refreshes the model and updates database
        """
        if not yearly_consumption_energy is None:
            self.solarpowermodel.set_yearly_consumption_energy(yearly_consumption_energy)
            updated=True

        if not solarpanel_type is None:
            solarpanel=SolarPanel(solarpanel_type=solarpanel_type)
            self.solarpowermodel.set_solarpanel(solarpanel)
            updated=True
            
        if not peak_production_power is None or not solarpanel_count is None:
            new_peak_power_panel=peak_production_power if peak_production_power is not None else self.solarpowermodel.get_peak_power_panel()
            new_solarpanel_count=solarpanel_count if solarpanel_count is not None else self.solarpowermodel.get_solar_panel_count()
            self.solarpowermodel.set_production_power(new_peak_power_panel,new_solarpanel_count)
            updated=True

        if not battery_type is None or battery_type!=self.solarpowermodel.battery.get_battery_type():
            new_battery=Battery(battery_type=battery_type)    
        else:
            new_battery=self.solarpowermodel.get_battery()

        if not inverter_type is None or inverter_type!=self.solarpowermodel.inverter.get_inverter_type():
            new_inverter=Inverter(inverter_type=inverter_type)
        else:
            new_inverter=self.solarpowermodel.get_inverter()


        self.solarpowermodel.refresh_power_flow(new_battery=new_battery,new_inverter=new_inverter)
        self.solarpowermodel.update_dual_tariff()
        self.solarpowermodel.update_dynamic_tariff()
        self.data_repository_solarmodel.update(self.solarpowermodel)

        return None

        
