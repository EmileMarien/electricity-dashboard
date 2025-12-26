from electricitycost import electricity_cost
from components import SolarPanel, Battery, Inverter, solar_panel_types, battery_types, inverter_types

def calculate_npv(battery_cost, total_solar_panel_cost, inverter_cost, discount_rate, initial_cash_flow, annual_degradation):
    # Calculate the least common multiple (LCM) of battery and solar panel lifetimes

    installation_cost = 0
    BOS_cost = 0
    capex = BOS_cost + installation_cost + total_solar_panel_cost + inverter_cost  + battery_cost  # multiplication for installation_cost + maintenance_cost
    
    investment_cost = capex + \
                      (inverter_cost + battery_cost) / pow(1 + discount_rate, 10) + \
                      (inverter_cost + battery_cost) / pow(1 + discount_rate, 20) - \
                      (inverter_cost + battery_cost) / pow(1 + discount_rate, 25) 
    print("Investment cost:", investment_cost)
    Year_1_payback = initial_cash_flow/investment_cost
    print("Year 1 payback:", Year_1_payback)
    cost_savings = sum((initial_cash_flow * pow(1 - annual_degradation, t - 1)) / pow(1 + discount_rate, t) for t in range(1, 26))
    print("Total cost savings:", cost_savings)
    
    npv = -investment_cost + cost_savings

    return npv


# Inputs
# Components Changeable  
# Solar panel Type 
class SolarPanelType:
    def __init__(self, solar_panel_cost, solar_panel_count, solar_panel_lifetime, panel_surface, annual_degradation, panel_efficiency, temperature_coefficient):
        self.solar_panel_cost = solar_panel_cost
        self.solar_panel_count = solar_panel_count
        self.solar_panel_lifetime = solar_panel_lifetime
        self.panel_surface = panel_surface
        self.annual_degradation = annual_degradation
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
  "Canadian": SolarPanelType(
        solar_panel_cost=110.4,            #cost of 1 solar panel
        solar_panel_count=10,            #aantal zonnepanelen
        solar_panel_lifetime=25,        
        panel_surface=1.953,              #oppervlakte van 1 zonnepaneel [m^2]
        annual_degradation=0.0035,         #annual_degradation: efficientieverlies per jaar in [%]
        panel_efficiency= 0.225,          #panel_efficiency: efficientie van het zonnepaneel in [%]
        temperature_coefficient=-0.0026    #temperature_coefficient: temperatuurafhankelijkheid 
    ),
    "Jinko": SolarPanelType(
        solar_panel_cost=105.6,           
        solar_panel_count=10,           
        solar_panel_lifetime=25,        
        panel_surface=1.998,              
        annual_degradation=0.004,         
        panel_efficiency= 0.2253,            
        temperature_coefficient=-0.0030  
    ),
    "Longi": SolarPanelType(
        solar_panel_cost=121.2,           
        solar_panel_count=10,           
        solar_panel_lifetime=25,        
        panel_surface=1.953,              
        annual_degradation=0.004,         
        panel_efficiency= 0.230,            
        temperature_coefficient=-0.0029  
    ),
    "REC": SolarPanelType(
        solar_panel_cost=181.8,           
        solar_panel_count=10,           
        solar_panel_lifetime=25,        
        panel_surface=1.934,              
        annual_degradation=0.0025,         
        panel_efficiency= 0.223,            
        temperature_coefficient=-0.0026 
    ),
    "Sunpower": SolarPanelType(
        solar_panel_cost=294,           
        solar_panel_count=10,           
        solar_panel_lifetime=40,        
        panel_surface=1.895,              
        annual_degradation=0.0025,         
        panel_efficiency= 0.219,            
        temperature_coefficient=-0.0027 
    ),
        "Poly": SolarPanelType(
        solar_panel_cost=60.48,           
        solar_panel_count=10,           
        solar_panel_lifetime=25,        
        panel_surface=1.62688,              
        annual_degradation=0.008,         
        panel_efficiency= 0.177,            
        temperature_coefficient=-0.0035 
    ),
    }



# Choose solar panel type:
chosen_panel_type = "Jinko"  # Change this to switch between different types
chosen_panel = solar_panel_types[chosen_panel_type]
total_solar_panel_cost = chosen_panel.total_solar_panel_cost
solar_panel_lifetime = chosen_panel.solar_panel_lifetime
total_panel_surface = chosen_panel.total_panel_surface
annual_degradation =  chosen_panel.annual_degradation
panel_efficiency = chosen_panel.panel_efficiency
temperature_coefficient = chosen_panel.temperature_coefficient
panel_surface = chosen_panel.panel_surface
solar_panel_count = chosen_panel.solar_panel_count

# battery type 
class BatteryType:
    def __init__(self, battery_cost, battery_lifetime, battery_capacity, battery_inverter,
                 battery_Roundtrip_Efficiency, battery_PeakPower, battery_Degradation):
        self.battery_cost = battery_cost
        self.battery_lifetime = battery_lifetime
        self.battery_capacity = battery_capacity
        self.battery_inverter = battery_inverter
        self.battery_Roundtrip_Efficiency = battery_Roundtrip_Efficiency
        self.battery_PeakPower = battery_PeakPower
        self.battery_Degradation = battery_Degradation

# Define different types of batteries
battery_types = {
    "no battery": BatteryType(
        battery_inverter = 1, #if this is 0 switch of inverter choice, if this is 1 switch on
        battery_cost= 0,                
        battery_lifetime=0,         
        battery_capacity= 0,
        battery_Roundtrip_Efficiency= 0,  
        battery_PeakPower= 0,  
        battery_Degradation= 0, 
        battery_count = 0
    ),    
     "LG RESU Prime 2.9": BatteryType(
        battery_inverter = 1,
        battery_cost=2349*1.25,                
        battery_lifetime=10,         
        battery_capacity=2.9,
        battery_Roundtrip_Efficiency=95,  
        battery_PeakPower=3.3,  
        battery_Degradation=4,   
        battery_count = 1  
    ),
    "LG RESU Prime 5.9": BatteryType(
        battery_inverter = 1,
        battery_cost=3327.5*1.25,                
        battery_lifetime=10,         
        battery_capacity=5.9,
        battery_Roundtrip_Efficiency=95,  
        battery_PeakPower=4.6,  
        battery_Degradation=4,   
        battery_count = 1  
    ),
    "LG RESU Prime 9.6": BatteryType(
        battery_inverter = 1,
        battery_cost=6497*1.25,         #in Eur, times for installation cost       
        battery_lifetime=10,         #in years 
        battery_capacity=9.6,#in kWh 
        battery_Roundtrip_Efficiency=97.5, #in procent 
        battery_PeakPower=7,  #in kW
        battery_Degradation=3,   #in procent per year 
        battery_count = 1
    ),
    "LG RESU Prime 16": BatteryType(
        battery_inverter = 1,
        battery_cost=8987*1.25,                
        battery_lifetime=10,         
        battery_capacity=16,
        battery_Roundtrip_Efficiency=97.5,  
        battery_PeakPower=11,  
        battery_Degradation=3,   
        battery_count = 1  
    ),
    
}

# Choose battery type:
chosen_battery_type = "no battery" # Change this to switch between different types
chosen_battery = battery_types[chosen_battery_type]
print(f"Total cost for {chosen_battery_type}: {chosen_battery.battery_cost}")
battery_cost = chosen_battery.battery_cost
battery_lifetime = chosen_battery.battery_lifetime
battery_capacity = chosen_battery.battery_capacity

# bedenkingen 
# panel_efficiency degradation into account nemen -> dus geen constanr cash flows 
# energieprijzen van energiecrisis in rekening gebracht? -> zoja factor reduceren
class InverterType:
    def __init__(self, inverter_cost, inverter_size_AC, inverter_maxbattery_DC, inverter_lifetime, inverter_efficiency, inverter_maxsolar_DC):
        self.inverter_cost = inverter_cost
        self.inverter_size_AC = inverter_size_AC
        self.inverter_maxsolar_DC = inverter_maxbattery_DC
        self.inverter_maxsolar_DC = inverter_maxsolar_DC
        self.inverter_lifetime = inverter_lifetime
        self.inverter_efficiency = inverter_efficiency
        self.inverter_maxbattery_DC = inverter_maxbattery_DC
# Define different types of batteries
inverter_types = {
    "no inverter": InverterType(
        inverter_cost = 0,
        inverter_size_AC = 100000,
        inverter_maxbattery_DC = 100000,
        inverter_maxsolar_DC = 100000,
        inverter_lifetime = 100,
        inverter_efficiency = 1,
    ),
    "Sungrow_3": InverterType(
        inverter_cost = 1219,
        inverter_size_AC = 3,
        inverter_maxbattery_DC = 6.6,
        inverter_maxsolar_DC = 10,
        inverter_lifetime = 10,
        inverter_efficiency = 0.97,
    ),
    "Sungrow_3.6": InverterType(
        inverter_cost = 1380,
        inverter_size_AC = 3.68,
        inverter_maxbattery_DC = 6.6,
        inverter_maxsolar_DC = 10.7,
        inverter_lifetime = 10,
        inverter_efficiency = 0.971,  
    ),
    "Sungrow_4": InverterType(
        inverter_cost = 1460,
        inverter_size_AC = 4,
        inverter_maxbattery_DC = 6.6,
        inverter_maxsolar_DC = 11,
        inverter_lifetime = 10,
        inverter_efficiency = 0.972,
    ),
    "Sungrow_5": InverterType(
        inverter_cost = 1570,
        inverter_size_AC = 5,
        inverter_maxbattery_DC = 6.6,
        inverter_maxsolar_DC = 12,
        inverter_lifetime = 10,
        inverter_efficiency = 0.972,
    ),
    "Fronius_3": InverterType(
        inverter_cost = 1579,
        inverter_size_AC = 3,
        inverter_maxbattery_DC = 3.11,
        inverter_maxsolar_DC = 4.5,
        inverter_lifetime = 10,
        inverter_efficiency = 0.968,
    ),
    "Fronius_3.6": InverterType(
        inverter_cost = 1650,
        inverter_size_AC = 3.68,
        inverter_maxbattery_DC = 3.81,
        inverter_maxsolar_DC = 5.52,        
        inverter_lifetime = 10,
        inverter_efficiency = 0.97,   
    ),
    "Fronius_4": InverterType(
        inverter_cost = 1702,
        inverter_size_AC = 4,
        inverter_maxbattery_DC = 4.14,
        inverter_maxsolar_DC = 6,
        inverter_lifetime = 10,
        inverter_efficiency = 0.971,    
    ),
    "Fronius_4.6": InverterType(
        inverter_cost = 1826,
        inverter_size_AC = 4.6,
        inverter_maxbattery_DC = 4.75,
        inverter_maxsolar_DC = 6.9,
        inverter_lifetime = 10,
        inverter_efficiency = 0.972,    
    ),
    "Fronius_5": InverterType(
        inverter_cost = 1922,
        inverter_size_AC = 5,
        inverter_maxbattery_DC = 5.17,
        inverter_maxsolar_DC = 7.5,
        inverter_lifetime = 10,
        inverter_efficiency = 0.972,    
    ),
    # Define more types as needed
}
chosen_inverter_type = "no inverter" # Change this to switch between different types
chosen_inverter = inverter_types[chosen_inverter_type]
inverter_cost = chosen_inverter.inverter_cost
inverter_maxsolar_DC = chosen_inverter.inverter_maxsolar_DC
inverter_size_AC = chosen_inverter.inverter_size_AC
inverter_efficiency = chosen_inverter.inverter_efficiency
inverter_maxbattery_DC = chosen_inverter.inverter_maxbattery_DC
print(f"Total cost for {chosen_inverter_type}: {chosen_inverter.inverter_cost}")


# Set-up
tilt_angle = -1 #tilt_angle: angle of the solar panel, 
Orientation = 'EW'#Orientation: richting naar waar de zonnepanelen staan 
	

# non-changeable 

#Economics
discount_rate = 0.0658                                    #Discount rate


#Calculations of the cashflows 



print(solar_panel_count, panel_surface, annual_degradation, panel_efficiency, temperature_coefficient, tilt_angle, Orientation, battery_capacity)
cost_grid_with_PV = electricity_cost(solar_panel_count = solar_panel_count, panel_surface = panel_surface, annual_degradation = annual_degradation, panel_efficiency = panel_efficiency, temperature_coefficient = temperature_coefficient, inverter_size_AC = inverter_size_AC, inverter_maxsolar_DC = inverter_maxsolar_DC, inverter_maxbattery_DC = inverter_maxbattery_DC, tilt_angle = tilt_angle, Orientation = Orientation, battery_capacity = battery_capacity)
print("cost grid:", cost_grid_with_PV)
cost_grid_with_PV_and_battery = electricity_cost(solar_panel_count = solar_panel_count, panel_surface = panel_surface, annual_degradation = annual_degradation, panel_efficiency = panel_efficiency, temperature_coefficient = temperature_coefficient, inverter_size_AC = inverter_size_AC, inverter_maxsolar_DC = inverter_maxsolar_DC, inverter_maxbattery_DC = inverter_maxbattery_DC, tilt_angle = tilt_angle, Orientation = Orientation, battery_capacity = battery_capacity)
print("cost grid:", cost_grid_with_PV_and_battery)
solar_panel_count = 0 
panel_surface = 0 
Cost_with_no_PV = electricity_cost(solar_panel_count = solar_panel_count, panel_surface = panel_surface, annual_degradation = annual_degradation, panel_efficiency = panel_efficiency, temperature_coefficient = temperature_coefficient, inverter_size_AC = inverter_size_AC, inverter_maxsolar_DC = inverter_maxsolar_DC, inverter_maxbattery_DC = inverter_maxbattery_DC, tilt_angle = tilt_angle, Orientation = Orientation, battery_capacity = battery_capacity)

print("cost witn no PV:", Cost_with_no_PV)

initial_cash_flow = Cost_with_no_PV - cost_grid_with_PV   #Besparing van kosten door zonnepanelen, kan men zien als de profit
print("initial cash flow:", initial_cash_flow)
# Calculate NPV
npv = calculate_npv(battery_cost, total_solar_panel_cost, inverter_cost, discount_rate, initial_cash_flow, annual_degradation)
print("Net Present Value (NPV):", npv)

import matplotlib.pyplot as plt

# Dictionary to store NPV values for each solar panel type
npv_values = {}
#  battery_inverter = 1,
#         battery_cost=15384*1.25*0.94,                
#         battery_lifetime=10,         
#         battery_capacity=18000,
#         battery_Roundtrip_Efficiency=96.5,  
#         battery_PeakPower=6000,  
#         battery_Degradation=3, 
# Iterate through each Battery type and calculate NPV
for battery_type, battery in battery_types.items():
    battery_cost = battery.battery_cost
    battery_lifetime = battery.battery_lifetime
    battery_capacity = battery.battery_capacity


    # Calculate initial cash flow for the current solar panel type
    cost_grid_with_PV = electricity_cost(solar_panel_count = solar_panel_count, panel_surface = panel_surface, annual_degradation = annual_degradation, panel_efficiency = panel_efficiency, temperature_coefficient = temperature_coefficient, inverter_size_AC = inverter_size_AC, inverter_maxsolar_DC = inverter_maxsolar_DC, inverter_maxbattery_DC = inverter_maxbattery_DC, tilt_angle = tilt_angle, Orientation = Orientation, battery_capacity = 0)
    cost_grid_with_PV_and_battery = electricity_cost(solar_panel_count = solar_panel_count, panel_surface = panel_surface, annual_degradation = annual_degradation, panel_efficiency = panel_efficiency, temperature_coefficient = temperature_coefficient, inverter_size_AC = inverter_size_AC, inverter_maxsolar_DC = inverter_maxsolar_DC, inverter_maxbattery_DC = inverter_maxbattery_DC, tilt_angle = tilt_angle, Orientation = Orientation, battery_capacity = battery_capacity)
    initial_cash_flow = cost_grid_with_PV - cost_grid_with_PV_and_battery

    # Calculate NPV for the current solar panel type
    npv = calculate_npv(battery_cost, total_solar_panel_cost, inverter_cost, discount_rate, initial_cash_flow, annual_degradation)

    # Store NPV value
    npv_values[battery_type] = npv

# Plotting
plt.figure(figsize=(10, 6))
plt.bar(npv_values.keys(), npv_values.values(), color='skyblue')
plt.xlabel('Battery Type')
plt.ylabel('Net Present Value (NPV)')
plt.title('Comparison of NPV for Different Battery Types')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
