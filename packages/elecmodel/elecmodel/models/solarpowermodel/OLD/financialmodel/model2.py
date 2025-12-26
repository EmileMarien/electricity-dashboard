from gridcost import grid_cost


def calculate_npv(capex, battery_lifetime, battery_cost, solar_panel_lifetime, total_solar_panel_cost, discount_rate, total_panel_surface ,annual_degredation, panel_efficiency, temperature_Coefficient,  tilt_angle, Orientation, battery_capacity, battery_count):
    # Calculate the least common multiple (LCM) of battery and solar panel lifetimes
    

    def lcm(x, y):
        from math import gcd
        return x * y // gcd(x, y)

    lcm_lifetime = lcm(battery_lifetime, solar_panel_lifetime)

    # Calculate cash flows for total project
    total_cash_flows = [-capex]

    for i in range(1, lcm_lifetime + 1):
        # Calculate cash flow for the current year
        current_year_in_cycle = (i - 1) % solar_panel_lifetime + 1
        current_cash_flow = grid_cost_initial - grid_cost(year_in_lifetime=current_year_in_cycle, total_panel_surface ,annual_degredation, panel_efficiency, temperature_Coefficient,  tilt_angle, Orientation, battery_capacity, battery_count)
        total_cash_flows.append(current_cash_flow)

        # Check if it's time for reinvestment in solar panels
        if i % solar_panel_lifetime == 0:
            total_cash_flows[i] -= total_solar_panel_cost

        # Check if it's time for reinvestment in batteries
        if i % battery_lifetime == 0:
            total_cash_flows[i] -= battery_cost

    # Calculate NPV
    npv = 0
    for i, cash_flow in enumerate(total_cash_flows):
        npv += cash_flow / (1 + discount_rate) ** i

    return npv
    


# Inputs
  
# Set-up
tilt_angle = ... #tilt_angle: angle of the solar panel, 
Orientation = ...#Orientation: richting naar waar de zonnepanelen staan N, E, S, W 

# Components Changeable  
# Solar panel Type 
class SolarPanelType:
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
    "Type A": SolarPanelType(
        solar_panel_cost=100,            #cost of 1 solar panel
        solar_panel_count=10,            #aantal zonnepanelen
        solar_panel_lifetime=10,        
        panel_surface=1.5,              #oppervlakte van 1 zonnepaneel [m^2]
        annual_degredation=0.5,         #annual_degredation: efficientieverlies per jaar in [%]
        panel_efficiency=0.90,          #panel_efficiency: efficientie van het zonnepaneel in [%]
        temperature_coefficient=0.05    #temperature_coefficient: temperatuurafhankelijkheid 
    ),
    "Type B": SolarPanelType(
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




# Choose solar panel type:
chosen_panel_type = "Type A"  # Change this to switch between different types
chosen_panel = solar_panel_types[chosen_panel_type]
print(f"Total cost for {chosen_panel_type}: {chosen_panel.total_solar_panel_cost}")
print(f"Total surface for {chosen_panel_type}: {chosen_panel.total_panel_surface}")

# battery type 
class BatteryType:
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
    "Type X": BatteryType(
        battery_cost=10000,         
        battery_count=5,            
        battery_lifetime=5,         
        battery_capacity=5000       
    ),
    "Type Y": BatteryType(
        battery_cost=12000,         
        battery_count=3,            
        battery_lifetime=6,         
        battery_capacity=8000       
    ),
    # Define more types as needed
}

# Choose battery type:
chosen_battery_type = "Type X"  # Change this to switch between different types
chosen_battery = battery_types[chosen_battery_type]
print(f"Total cost for {chosen_battery_type}: {chosen_battery.total_battery_cost}")

# non-changeable 
invertor_cost= 500
installation_cost= 1000
maintenance_cost = 0

#Economics
discount_rate = 0.1                                          #Discount rate
capex = total_solar_panel_cost + total_battery_cost + installation_cost + invertor_cost + maintenance_cost

#Calculations of the cashflows 


npv_result = calculate_npv(capex, battery_lifetime, battery_cost, solar_panel_lifetime, total_solar_panel_cost, discount_rate, total_panel_surface ,annual_degredation, panel_efficiency, temperature_Coefficient,  tilt_angle, Orientation, battery_capacity, battery_count)



# Calculate NPV
npv = calculate_npv(battery_cost, solar_panel_cost, battery_lifetime, solar_panel_lifetime, discount_rate, constant_cash_flow)
print("Net Present Value (NPV):", npv)


