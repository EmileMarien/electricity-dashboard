from dataclasses import dataclass

from elecmodel.models.solarpowermodel.solarpowermodel import SolarPowerModel
from elecmodel.models.battery.battery import Battery
from elecmodel.models.inverter.inverter import Inverter
from elecmodel.models.solarpanel.solarpanel import SolarPanel

@dataclass
class ElecModelApp:
    model_repo: object
    belpex_repo: object
    slp_repo: object
    spp_repo: object

    def new_model(self, reference_id: str) -> SolarPowerModel:
        m = SolarPowerModel()
        m.set_reference_id(reference_id)
        # Firestore repo API
        self.model_repo.add_model(m)
        return m

    def load_model(self, reference_id: str) -> SolarPowerModel:
        # Firestore repo API
        return self.model_repo.get_model(reference_id)

    def save_model(self, model: SolarPowerModel) -> None:
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

    def change_components(
        self,
        reference_id: str,
        battery_type: str | None = None,
        inverter_type: str | None = None,
        solarpanel_type: str | None = None,
        yearly_consumption_energy: float | None = None,
        peak_production_power: float | None = None,
        solarpanel_count: int | None = None,
    ) -> None:
        m = self.load_model(reference_id)

        if yearly_consumption_energy is not None:
            m.set_yearly_consumption_energy(yearly_consumption_energy)

        if solarpanel_type is not None:
            m.set_solarpanel(SolarPanel(solar_panel_type=solarpanel_type))

        if peak_production_power is not None or solarpanel_count is not None:
            new_peak = peak_production_power if peak_production_power is not None else m.get_peak_power_panel()
            new_count = solarpanel_count if solarpanel_count is not None else m.get_solar_panel_count()
            m.set_production_power(new_peak, new_count)

        new_battery = Battery(battery_type=battery_type) if battery_type is not None else m.get_battery()
        new_inverter = Inverter(inverter_type=inverter_type) if inverter_type is not None else m.get_inverter()

        m.refresh_power_flow(new_battery=new_battery, new_inverter=new_inverter)
        m.update_dual_tariff()
        m.update_dynamic_tariff()

        self.save_model(m)

    def kpis(self, reference_id: str) -> dict:
        m = self.load_model(reference_id)
        return {
            "reference_id": reference_id,
            "total_cost_dynamic": float(m.get_total_cost(tariff="DynamicTariff")),
            "total_production_kwh": float(m.get_energy_TOT(column_name="PV_Power_kW", peak="all")),
            "total_consumption_kwh": float(m.get_energy_TOT(column_name="Load_kW", peak="all")),
            "peak_power_kw": float(m.get_peak_power()),
        }
