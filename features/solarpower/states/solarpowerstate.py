
# performs the logic when which has to run



from features.solarpower.models.battery.battery import Battery
from core.firestore_init import authenticate_to_firestore, load_key
from features.solarpower.repositories.data_repository_belpex import DataRepositoryBelpex
from features.solarpower.repositories.data_repository_solarmodel import DataRepositorySolarModel
from features.solarpower.repositories.data_repository_syntheticprofiles import DataRepositorySLP, DataRepositorySPP
from features.solarpower.models.solarpowermodel.solarpowermodel import SolarPowerModel
from features.solarpower.models.syntheticprofilefetching.syntheticprofilefetching import SLP_xls_to_pd, SPP_xls_to_pd
from features.solarpower.models.pricefetching.pricefetching import fetch_electricity_prices
from features.solarpower.models.inverter.inverter import Inverter
from features.solarpower.models.solarpanel.solarpanel import SolarPanel


class SolarPowerState():
    def __init__(self):
        firestor_reference=authenticate_to_firestore(load_key())
        self.solarpowermodel=SolarPowerModel()
        self.data_repository_belpex=DataRepositoryBelpex(firestore_reference=firestor_reference)
        self.data_repository_solarmodel=DataRepositorySolarModel(firestore_reference=firestor_reference)
        self.data_repository_SLP=DataRepositorySLP(firestore_reference=firestor_reference)
        self.data_repository_SPP=DataRepositorySPP(firestore_reference=firestor_reference)
        self.solarpowermodel.set_reference_id('test')
    
    def set_SLP(self):
        SLP=SLP_xls_to_pd('data/slp_enu_cons.xls')
        self.data_repository_SLP.add_SLP(SLP=SLP)
        return None

    def set_SPP(self):
        SPP=SPP_xls_to_pd('data/SPP_2022_(Ex-ante_and_Ex-post)_v1_0_prod.xlsx')
        self.data_repository_SLP.add_SPP(SPP=SPP)
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

        self.solarpowermodel.append_belpex_df(prices)

        self.data_repository_solarmodel.update(self.solarpowermodel,fields_to_update={"dataframe": self.solarpowermodel.pd.rename(index=lambda x: x.strftime('%Y-%m-%d %H:%M:%S %Z')).to_dict(orient='index')})

    def update_SLP(self):
        self.solarpowermodel.append_load_df(self.data_repository_SLP.get_SLP(),SLP=True)
        self.data_repository_solarmodel.update(self.solarpowermodel,fields_to_update={"dataframe": self.solarpowermodel.pd.rename(index=lambda x: x.strftime('%Y-%m-%d %H:%M:%S %Z')).to_dict(orient='index')})            

    def update_SPP(self):
        self.solarpowermodel.append_pv_power_df(self.data_repository_SPP.get_SPP(),SPP=True)
        self.data_repository_solarmodel.update(self.solarpowermodel,fields_to_update={"dataframe": self.solarpowermodel.pd.rename(index=lambda x: x.strftime('%Y-%m-%d %H:%M:%S %Z')).to_dict(orient='index')})

    def update_calculations(self):
        self.solarpowermodel.update_power_flow()
        self.solarpowermodel.update_dual_tariff()
        self.solarpowermodel.update_dynamic_tariff()
        return "calculations updated"

    def get_columns(self,columns):
        return self.solarpowermodel.get_columns(columns=columns)
    
    def change_model(self,battery:Battery=None,inverter:Inverter=None,solarpanel:SolarPanel=None):
        updated=False
        """
        Checks if the provided components differ from the current installed ones and if so, refreshes the model and updates database
        """
        if solarpanel.get_solarpanel_type()!=self.solarpowermodel.solarpanel.get_solarpanel_type() and solarpanel is not None:
            self.solarpowermodel.refresh_PV_Power_kW(new_solarpanel=solarpanel,SLP_data=self.data_repository_SLP.get_SLP())
            updated=True
        else:
            self.solarpowermodel.update_PV_Power_kW() #TODO: change so SLP can also be used!!

        if battery.get_battery_type()!=self.solarpowermodel.battery.get_battery_type() or inverter.get_inverter_type()!=self.solarpowermodel.inverter.get_inverter_type() or updated:
            new_battery= battery if ((battery is not None) or (battery.get_battery_type()!=self.solarpowermodel.battery.get_battery_type())) else self.solarpowermodel.get_battery()

            new_inverter= inverter if ((inverter is not None) or (inverter.get_inverter_type()!=self.solarpowermodel.inverter.get_inverter_type())) else self.solarpowermodel.get_inverter()

            self.solarpowermodel.refresh_power_flow(new_battery=new_battery,new_inverter=new_inverter)

            self.data_repository_solarmodel.update(self.solarpowermodel,fields_to_update={'battery':self.solarpowermodel.battery.to_dict(),'inverter':self.solarpowermodel.inverter.to_dict(),'solarpanel':self.solarpowermodel.solarpanel.to_dict(),'pd':self.solarpowermodel.pd.to_dict()})
        return None

        
