
# performs the logic when which has to run



from core.firestore_init import authenticate_to_firestore, load_key
from features.solarpower.repositories.data_repository_belpex import DataRepositoryBelpex
from features.solarpower.repositories.data_repository_solarmodel import DataRepositorySolarModel
from features.solarpower.repositories.data_repository_syntheticprofiles import DataRepositorySLP
from features.solarpower.models.solarpowermodel.solarpowermodel import SolarPowerModel
from features.solarpower.models.syntheticprofilefetching.syntheticprofilefetching import SLP_xls_to_pd


class SolarPowerState():
    def __init__(self):
        firestor_reference=authenticate_to_firestore(load_key())
        self.solarpowermodel=SolarPowerModel()
        self.data_repository_belpex=DataRepositoryBelpex(firestore_reference=firestor_reference)
        self.data_repository_solarmodel=DataRepositorySolarModel(firestore_reference=firestor_reference)
        self.data_repository_SLP=DataRepositorySLP(firestore_reference=firestor_reference)
    
    def set_SLP(self):
        SLP=SLP_xls_to_pd('data/slp_enu_cons.xls')
        self.data_repository_SLP.add_SLP(SLP=SLP)
        return SLP
    
    def load_model(self):
        self.solarpowermodel=self.data_repository_solarmodel.get_model(reference_id=self.solarpowermodel.get_reference_id() if self.solarpowermodel.get_reference_id() is not None else 'muFpAMmhxutpRvwnG1M4')
    
    def upload_model(self):
        id=self.data_repository_solarmodel.add_model(model=self.solarpowermodel)
        if self.solarpowermodel.get_reference_id() is None:
            self.solarpowermodel.set_reference_id(id)
        return None
    
    def update_belpex(self):
        self.solarpowermodel.append_belpex_df(self.data_repository_belpex.get_belpex())
        self.data_repository_solarmodel.update_model(self.solarpowermodel,fields_to_update={'pd':self.solarpowermodel.pd.to_dict()})

    def update_SLP(self):
        self.solarpowermodel.append_load_df(self.data_repository_SLP.get_SLP().rename(columns={'timestamp':'DateTime','value':'Load_kW'})
        self.data_repository_solarmodel.update_model(self.solarpowermodel,fields_to_update={'pd':self.solarpowermodel.pd.to_dict()})

        
