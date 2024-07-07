# Components Changeable  
# Solar panel Type 
class SolarPanel:
    def __init__(self, solar_panel_cost, solar_panel_count, solar_panel_lifetime, panel_surface, annual_degredation, panel_efficiency, temperature_coefficient):
        self.solar_panel_cost = solar_panel_cost
        self.solar_panel_count = solar_panel_count
        self.solar_panel_lifetime = solar_panel_lifetime
        self.panel_surface = panel_surface
        self.annual_degredation = annual_degredation
        self.panel_efficiency = panel_efficiency
        self.temperature_coefficient = temperature_coefficient
        self.calculate_total_cost()
        self.calculate_total_surface()

    def calculate_total_cost(self):
        self.total_solar_panel_cost = self.solar_panel_cost * self.solar_panel_count

    def calculate_total_surface(self):
        self.total_panel_surface = self.panel_surface * self.solar_panel_count

# Define different types of solar panels
solar_panel_types = {
    "Type A": SolarPanel(
        solar_panel_cost=100,            #cost of 1 solar panel
        solar_panel_count=10,            #aantal zonnepanelen
        solar_panel_lifetime=10,        
        panel_surface=1.5,              #oppervlakte van 1 zonnepaneel [m^2]
        annual_degredation=0.5,         #annual_degredation: efficientieverlies per jaar in [%]
        panel_efficiency=0.90,          #panel_efficiency: efficientie van het zonnepaneel in [%]
        temperature_coefficient=0.05    #temperature_coefficient: temperatuurafhankelijkheid 
    ),
    "Type B": SolarPanel(
        solar_panel_cost=120,           
        solar_panel_count=12,           
        solar_panel_lifetime=12,        
        panel_surface=1.8,              
        annual_degredation=0.6,         
        panel_efficiency=0.85,            
        temperature_coefficient=0.06   
    ),
    # Define more types as needed
}

# battery type 
class Battery:
    def __init__(self, battery_cost, battery_count, battery_lifetime, battery_capacity):
        self.battery_cost = battery_cost
        self.battery_count = battery_count
        self.battery_lifetime = battery_lifetime
        self.battery_capacity = battery_capacity
        self.calculate_total_cost()

    def calculate_total_cost(self):
        self.total_battery_cost = self.battery_cost * self.battery_count

# Define different types of batteries
battery_types = {
    "Type X": Battery(
        battery_cost=10000,         
        battery_count=5,            
        battery_lifetime=5,         
        battery_capacity=5000       
    ),
    "Type Y": Battery(
        battery_cost=12000,         
        battery_count=3,            
        battery_lifetime=6,         
        battery_capacity=8000       
    ),
    # Define more types as needed
}


class Inverter:
    def __init__(self, inverter_cost, inverter_lifetime, inverter_efficiency, DC_battery, DC_solar_panels, AC_output):
        self.inverter_cost = inverter_cost
        self.inverter_lifetime = inverter_lifetime
        self.inverter_efficiency = inverter_efficiency
        self.DC_battery = DC_battery
        self.DC_solar_panels = DC_solar_panels
        self.AC_output = AC_output

inverter_types = {
    "Type 1": Inverter(
        inverter_cost=5000,         
        inverter_lifetime=10,         
        inverter_efficiency=0.95,         
        DC_battery=48,         
        DC_solar_panels=400,         
        AC_output=2300       
    ),
    "Type 2": Inverter(
        inverter_cost=6000,         
        inverter_lifetime=10,         
        inverter_efficiency=0.96,         
        DC_battery=48,         
        DC_solar_panels=500,         
        AC_output=2500       
    ),
    # Define more types as needed
}
