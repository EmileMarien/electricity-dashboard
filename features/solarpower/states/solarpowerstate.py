
# performs the logic when which has to run



from core.firestore_init import authenticate_to_firestore, load_key
from features.solarpower.repositories.data_repository_belpex import DataRepositoryBelpex
from features.solarpower.repositories.data_repository_solarmodel import DataRepositorySolarModel
from features.solarpower.repositories.data_repository_syntheticprofiles import DataRepositorySLP
from features.solarpower.models.solarpowermodel.solarpowermodel import SolarPowerModel
from features.solarpower.models.syntheticprofilefetching.syntheticprofilefetching import SPP_xls_to_pd


class SolarPowerState():
    def __init__(self):
        firestor_reference=authenticate_to_firestore(load_key())
        self.solarpowermodel=SolarPowerModel()
        self.data_repository_belpex=DataRepositoryBelpex(firestore_reference=firestor_reference)
        self.data_repository_solarmodel=DataRepositorySolarModel(firestore_reference=firestor_reference)
        self.data_repository_SLP=DataRepositorySLP(firestore_reference=firestor_reference)
    
    def set_SLP(self):
        SLP=SPP_xls_to_pd('data/slp_enu_cons.xls')
        self.data_repository_SLP.add_SLP(SLP=SLP)
        return SLP