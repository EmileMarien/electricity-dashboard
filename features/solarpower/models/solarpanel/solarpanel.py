class SolarPanel:
    def __init__(self, solar_panel_type=None, solar_panel_cost=None, solar_panel_count=None, solar_panel_lifetime=None, panel_surface=None, annual_degradation=None, panel_efficiency=None, temperature_coefficient=None):
        """
        solar_panel_cost: cost of a single solar panel
        solar_panel_count: number of solar panels
        solar_panel_lifetime: lifetime of a single solar panel
        panel_surface: surface of a single solar panel
        annual_degradation: annual degradation of a single solar panel
        panel_efficiency: efficiency of a single solar panel
        temperature_coefficient: temperature coefficient of a single solar panel
        solar_panel_type: type of solar panel, choose from the following: "Canadian", "Jinko", "Longi", "REC", "Sunpower", "Poly"
        """
        if solar_panel_type is None:
            self.solar_panel_cost = solar_panel_cost
            self.solar_panel_count = solar_panel_count
            self.solar_panel_lifetime = solar_panel_lifetime
            self.panel_surface = panel_surface
            self.annual_degradation = annual_degradation
            self.panel_efficiency = panel_efficiency
            self.temperature_coefficient = temperature_coefficient
        else:
            solar_panel_types = {
                "Canadian": {
                    "solar_panel_cost": 110.4,
                    "solar_panel_count": 10,
                    "solar_panel_lifetime": 25,
                    "panel_surface": 1.953,
                    "annual_degradation": 0.0035,
                    "panel_efficiency": 0.225,
                    "temperature_coefficient": -0.0026
                },
                "Jinko": {
                    "solar_panel_cost": 105.6,
                    "solar_panel_count": 10,
                    "solar_panel_lifetime": 25,
                    "panel_surface": 1.998,
                    "annual_degradation": 0.004,
                    "panel_efficiency": 0.2253,
                    "temperature_coefficient": -0.0030
                },
                "Longi": {
                    "solar_panel_cost": 121.2,
                    "solar_panel_count": 10,
                    "solar_panel_lifetime": 25,
                    "panel_surface": 1.953,
                    "annual_degradation": 0.004,
                    "panel_efficiency": 0.230,
                    "temperature_coefficient": -0.0029
                },
                "REC": {
                    "solar_panel_cost": 181.8,
                    "solar_panel_count": 10,
                    "solar_panel_lifetime": 25,
                    "panel_surface": 1.934,
                    "annual_degradation": 0.0025,
                    "panel_efficiency": 0.223,
                    "temperature_coefficient": -0.0026
                },
                "Sunpower": {
                    "solar_panel_cost": 294,
                    "solar_panel_count": 10,
                    "solar_panel_lifetime": 40,
                    "panel_surface": 1.895,
                    "annual_degradation": 0.0025,
                    "panel_efficiency": 0.219,
                    "temperature_coefficient": -0.0027
                },
                "Poly": {
                    "solar_panel_cost": 60.48,
                    "solar_panel_count": 10,
                    "solar_panel_lifetime": 25,
                    "panel_surface": 1.62688,
                    "annual_degradation": 0.008,
                    "panel_efficiency": 0.177,
                    "temperature_coefficient": -0.0035
                }
            }
            self.solar_panel_cost = solar_panel_types[solar_panel_type]["solar_panel_cost"]
            self.solar_panel_count = solar_panel_types[solar_panel_type]["solar_panel_count"]
            self.solar_panel_lifetime = solar_panel_types[solar_panel_type]["solar_panel_lifetime"]
            self.panel_surface = solar_panel_types[solar_panel_type]["panel_surface"]
            self.annual_degradation = solar_panel_types[solar_panel_type]["annual_degradation"]
            self.panel_efficiency = solar_panel_types[solar_panel_type]["panel_efficiency"]
            self.temperature_coefficient = solar_panel_types[solar_panel_type]["temperature_coefficient"]
                        
 
            self.total_solar_panel_cost = self.solar_panel_cost * self.solar_panel_count if self.solar_panel_cost is not None and self.solar_panel_count is not None else None

            self.total_panel_surface = self.panel_surface * self.solar_panel_count if self.panel_surface is not None and self.solar_panel_count is not None else None
    
    from .utils._getters import get_solar_panel_cost
    from .utils._getters import get_solar_panel_count
    from .utils._getters import get_solar_panel_lifetime
    from .utils._getters import get_panel_surface
    from .utils._getters import get_annual_degradation
    from .utils._getters import get_panel_efficiency
    from .utils._getters import get_temperature_coefficient
    from .utils._getters import get_total_solar_panel_cost
    from .utils._getters import get_total_panel_surface

    from .utils._repository import from_snapshot
