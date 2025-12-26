from dataclasses import dataclass

from buildingmodel.buildingmodel.models.Project import Project

@dataclass
class BuildingModelApp:
    #model_repo: object
    #belpex_repo: object TODO: this is old, has to be replaced

    def new_model(self, reference_id: str) -> Project:
        m = Project()
        m.set_reference_id(reference_id)
        # Firestore repo API
        self.model_repo.add_model(m)
        return m

    def load_model(self, reference_id: str) -> Project:
        # Firestore repo API
        return self.model_repo.get_model(reference_id)

    def save_model(self, model: Project) -> None:
        # Firestore repo API
        self.model_repo.update(model)

    def update_prices(self, reference_id: str) -> None:
        m = self.load_model(reference_id)
        prices_df = self.belpex_repo.fetch_latest_prices()
        m.append_belpex_df(prices_df)
        self.save_model(m)

    def update_profiles(self, reference_id: str) -> None:
        m = self.load_model(reference_id)
        m.append_load_df(self.slp_repo.get_SLP(), SLP=True)
        m.append_pv_power_df(self.spp_repo.get_SPP(), SPP=True)
        self.save_model(m)

    def update_calculations(self, reference_id: str) -> None:
        m = self.load_model(reference_id)
        m.update_power_flow()
        m.update_dual_tariff()
        m.update_dynamic_tariff()
        self.save_model(m)