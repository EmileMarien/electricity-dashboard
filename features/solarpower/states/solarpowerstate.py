
# performs the logic when which has to run



from core.firestore_init import authenticate_to_firestore, load_key
from features.solarpower.repositories.data_repository_belpex import DataRepositoryBelpex
from features.solarpower.repositories.data_repository_solarmodel import DataRepositorySolarModel
from features.solarpower.repositories.data_repository_syntheticprofiles import DataRepositorySLP
from features.solarpower.models.solarpowermodel.solarpowermodel import SolarPowerModel
from features.solarpower.models.syntheticprofilefetching.syntheticprofilefetching import SLP_xls_to_pd
from features.solarpower.models.pricefetching.pricefetching import fetch_electricity_prices


class SolarPowerState():
    def __init__(self):
        firestor_reference=authenticate_to_firestore(load_key())
        self.solarpowermodel=SolarPowerModel()
        self.data_repository_belpex=DataRepositoryBelpex(firestore_reference=firestor_reference)
        self.data_repository_solarmodel=DataRepositorySolarModel(firestore_reference=firestor_reference)
        self.data_repository_SLP=DataRepositorySLP(firestore_reference=firestor_reference)
        self.solarpowermodel.set_reference_id('test')
    
    def set_SLP(self):
        SLP=SLP_xls_to_pd('data/slp_enu_cons.xls')
        self.data_repository_SLP.add_SLP(SLP=SLP)
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

        self.data_repository_solarmodel.update(self.solarpowermodel,fields_to_update={"pd": self.solarpowermodel.pd.rename(index=lambda x: x.strftime('%Y-%m-%d %H:%M:%S')).to_dict(orient='index')})

    def update_SLP(self):
        self.solarpowermodel.append_load_df(self.data_repository_SLP.get_SLP(),SLP=True)
        self.data_repository_solarmodel.update(self.solarpowermodel,fields_to_update={"pd": self.solarpowermodel.pd.rename(index=lambda x: x.strftime('%Y-%m-%d %H:%M:%S')).to_dict(orient='index')})            

    
    def get_columns(self,columns):
        return self.solarpowermodel.get_columns(columns=columns)
    
    def change_model(self,Battery=None,Inverter=None,SolarPanel=None):
        if Battery!=self.solarpowermodel.battery or Inverter!=self.solarpowermodel.inverter or SolarPanel!=self.solarpowermodel.solar:
            self.solarpowermodel.refresh_power_flow(Battery=Battery,Inverter=Inverter,SolarPanel=SolarPanel)

            self.data_repository_solarmodel.update(self.solarpowermodel,fields_to_update={'battery':self.solarpowermodel.battery.to_dict(),'inverter':self.solarpowermodel.inverter.to_dict(),'solarpanel':self.solarpowermodel.solarpanel.to_dict(),'pd':self.solarpowermodel.pd.to_dict()})
        return None

        
