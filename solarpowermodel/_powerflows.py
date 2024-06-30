import pandas as pd



def power_flow(self, max_charge: int = 8, max_AC_power_output: int = 5, max_DC_batterypower: int = 5, max_PV_input: int = 10, max_EV_power: int = 3.7, max_EV_charge=82.3,EV_type:str='no_EV',battery_roundtrip_efficiency:float=97.5, battery_PeakPower:int=11):
    """
    Calculates power flows, how much is going to and from the battery and how much is being tapped from the grid
    #TODO: add units, PV_Power_kW and Load_kW are both in kW. Depending on the frequency of this data, a different amount is subtracted from the battery charge (in kWh?) (e.g. if 1h freq, the load of each line can be subtracted directly since 1kW*1h=1kWh. If in minutes, then 1kW*1min=1/60kWh) 
    ADD BATTERY DEGRADATION

    Args:
        max_charge (int, optional): Maximum charge capacity of the battery in kWh. Defaults to 8.
        max_AC_power_output (int): Maximum power that can be sent to the grid in kW. Defaults to 2.
        max_DC_batterypower_output (int, optional): Maximum power that can be sent to the battery in kW. Defaults to 2.
        max_PV_input (int, optional): Maximum power that can be sent to the battery in kW. Defaults to 10.
        max_EV_power (int, optional): Maximum power that can be sent to the EV in kW. Defaults to 3.7.
        max_EV_charge (int, optional): Maximum charge capacity of the EV in kWh. Defaults to 82.3.
    Returns:
        None
    """ 
    
    # Check if all required columns are present
    required_columns = ['PV_Power_kW','Load_kW'] # [kW]
    missing_columns = [col for col in required_columns if col not in self.pd.columns]
    assert not missing_columns, f"The following columns are missing: {', '.join(missing_columns)}"

    # Check if no None values are present

    # convert charges to unit of frequency of the data
    interval = 3600/pd.Timedelta(self.pd.index.freq).total_seconds() # hours to seconds
    max_charge = max_charge*interval
    max_EV_charge = max_EV_charge*interval

    # Initialize variables
    previous_charge_battery = 0.1*max_charge  # Initialize as integer
    previous_charge_EV = 0.5*max_EV_charge  # Initialize as integer

    # Initialize counters
    length=self.pd.shape[0]
    counter=0

    # Set lists to store calculated values
    battery_charge_list = []  # List to store calculated battery charges
    grid_flow_list = []  # List to store calculated grid flows
    power_loss_list = [] # List to store calculated power loss
    battery_flow_list = [] # List to store flow to and from the battery
    EV_charge_list = [] # List to store calculated EV charges
    EV_flow_list = [] # List to store flow to and from the EV
    PV_power=[]
    loss=[]
    # Iterate over DataFrame rows
    for _, row in self.pd.iterrows():
        print(f"Calculating power flows for row {counter}/{length}", end="\r")
        counter+=1
        PV_power = min(row['PV_Power_kW'], max_PV_input) #power_loss = row['PV_Power_kW'] - PV_power
        loss+=row['PV_Power_kW'] - PV_power
        load = -row['Load_kW']
 
        excess_load=-max(0,-load-max_AC_power_output) #load that is immediately sent to the grid
        load=load-excess_load #load that is left after the excess load is sent to the grid 
        load_to_EV =PV_power+load
        load_to_battery, new_charge_EV= EV(row=row,load_to_EV=load_to_EV,old_capacity=previous_charge_EV,EV_type=EV_type,max_EV_charge=max_EV_charge,max_EV_power=max_EV_power,freq=interval)
        load_from_battery, new_charge_battery = battery(row,load_to_battery, previous_charge_battery,max_charge=max_charge,max_DC_batterypower=max_DC_batterypower,battery_PeakPower=battery_PeakPower,battery_roundtrip_efficiency=battery_roundtrip_efficiency)
        grid_flow = load_from_battery
        
        grid_flow = min(grid_flow, max_AC_power_output) # Limit positive grid flow to max AC power output
        grid_flow = grid_flow + excess_load # Add the excess load to the grid flow
        previous_charge_battery=new_charge_battery
        previous_charge_EV=new_charge_EV

        # Append calculated values to lists
        battery_charge_list.append(new_charge_battery/interval) 
        grid_flow_list.append(grid_flow)
        power_loss_list.append(0)
        battery_flow_list.append(load_to_battery-load_from_battery) # Battery flow is positive when charging, negative when discharging
        EV_charge_list.append(new_charge_EV/interval)
        EV_flow_list.append(load_to_EV-load_to_battery)     # EV flow is positive when charging, negative when discharging


    self.pd['BatteryCharge'] = battery_charge_list
    self.pd['GridFlow'] = grid_flow_list
    self.pd['GridFlow_Load']=self.pd['Load_kW']*0.9 #TODO: add efficiencies of the inverter
    #row['PowerLoss'] = power_loss
    self.pd['BatteryFlow'] = battery_flow_list
    self.pd['EVCharge'] = EV_charge_list
    self.pd['EVFlow'] = EV_flow_list
    return None

def battery(row,load_to_battery:float,old_capacity:float,max_charge: int = 8, max_DC_batterypower: int = 2,battery_roundtrip_efficiency:float=97.5, battery_PeakPower:int=11):
    """
    Calculate load after the battery and the new battery capacity using the old capacity and load
    """
    #power_loss=0
    min_capacity=0#max_charge*0.1
    max_capacity=max_charge#max_charge*0.9
    max_DC_batterypower=min(max_DC_batterypower,battery_PeakPower)
    if load_to_battery > 0:  # Excess power from PV
        max_input=min(max_capacity-old_capacity,load_to_battery,max_DC_batterypower) #TODO: add function that it can be better to charge at a later time and move more to the grid now
        load_from_battery=load_to_battery-max_input
        new_capacity=old_capacity+max_input
        #power_loss += min(max_capacity-old_capacity, load) - max_input
    
    # Insufficient PV power, need to draw from battery and not between 22:00 and 6:00
    elif (load_to_battery < 0) and (row.name.hour>=4 and row.name.hour<23):
        max_output=min(max_DC_batterypower,old_capacity-min_capacity,-load_to_battery)
        load_from_battery=(load_to_battery+max_output)*battery_roundtrip_efficiency/100
        new_capacity=old_capacity-max_output
        #power_loss += old_capacity - min(min_capacity, old_capacity) - max_output

    else:  # No excess power or deficit
        load_from_battery=load_to_battery
        new_capacity=old_capacity

    return load_from_battery,new_capacity

def EV(row,load_to_EV:float,old_capacity:float,EV_type:str='B2G',max_EV_power: int = 3.7, max_EV_charge=82.3,freq:int=60):
    """
    Calculate load after the EV and the new EV capacity using the old capacity and load
    
    Args:
        row (pd.Series): The row of the DataFrame
        load_to_EV (float): The load that is sent to the EV
        old_capacity (float): The old capacity of the EV
        EV_type (str): The type of EV, either 'B2G', 'with_SC', 'no_SC' or 'no_EV'
        max_EV_power (int, optional): The maximum power that can be sent to the EV in kW. Defaults to 3.7.
        max_EV_charge (int, optional): The maximum charge capacity of the EV in kWh. Defaults to 82.3.
        
    Returns:
        tuple[float,float]: The load that is sent from the EV and the new EV capacity
    """
    max_EV_charge=max_EV_charge #kWmin
    max_input_power=max_EV_power
    max_output_power=max_EV_power
    min_capacity_evening=max_EV_charge*0.2

    min_capacity_morning=max_EV_charge*0.4
    max_capacity=0.8*max_EV_charge
    if EV_type=='B2G':
        # During the weekdays
        if row.name.weekday()<5:
            # During the weekdays, without wednesday, from 9:00 to 17:00, or wednesday from 9-12, the load of the EV is zero so it returns the same load as the household, but the EV battery decreases by 14 kWh per 7 hours
            if (row.name.hour>=9 and row.name.hour<17 and row.name.weekday()!=2) or (row.name.hour>=9 and row.name.hour<13 and row.name.weekday()==2):
                load_from_EV=load_to_EV
                new_capacity=old_capacity-1.3
            
            # During the weekdays in the morning, from 7:00 to 9:00, and evening, from 17:00 to 21:00, or on wednesday from 13:00-17:00, the EV is uncharging, reducing the household load and the battery capacity as long as the battery capacity is greater than 40 kWh in the morning and 20kWh at 19:00
            elif (row.name.hour>=6 and row.name.hour<9) or (row.name.hour>=17 and row.name.hour<22) or (row.name.hour>=13 and row.name.hour<17 and row.name.weekday()==2):
                min_capacity= min_capacity_morning if row.name.hour<9 else min_capacity_evening # minimal capacity of the battery
                if load_to_EV<0:
                    max_output=min(max_output_power,old_capacity-min_capacity,-load_to_EV)
                    max_input=0
                    load_from_EV=load_to_EV+max_output
                    new_capacity=old_capacity-max_output
                else:
                    max_output=0
                    max_input=min(max_input_power,max_capacity-old_capacity,load_to_EV) 
                    load_from_EV=load_to_EV-max_input
                    new_capacity=old_capacity+max_input
            
            # During the weekdays in the rest of the hours, the EV is charging, increasing the household load and the battery capacity as long as the battery capacity is less than 60 kWh
            else:
                max_input=min(max_input_power,max_capacity-old_capacity)
                load_from_EV=load_to_EV-max_input
                new_capacity=old_capacity+max_input
            
        # During the weekends
        elif row.name.weekday()>=5:
            # During the weekends, from 11:00 to 17:00, the car is charged using the solar energy 
            if row.name.hour>=11 and row.name.hour<17:
                max_input=min(max_input_power,max_capacity-old_capacity)
                load_from_EV=load_to_EV-max_input
                new_capacity=old_capacity+max_input
            # During the weekends in the night, from 22:00 to 9:00, and evening, from 17:00 to 19:00, the EV is uncharging, reducing the household load and the battery capacity as long as the battery capacity is greater than 40 kWh in the morning and 20kWh at 19:00
            elif (row.name.hour<9) or (row.name.hour>=17 and row.name.hour<19) or (row.name.hour>=22):
                min_capacity= min_capacity_evening if row.name.hour<9 else min_capacity_morning # minimal capacity of the battery
                max_output=min(max_output_power,old_capacity-min_capacity,-load_to_EV) #If you see the charge of the load reducing, that means you are done with morning stuff
                load_from_EV=load_to_EV+max_output
                new_capacity=old_capacity-max_output 
            
            else:
                # The car is out of the house
                load_from_EV=load_to_EV
                new_capacity=old_capacity-1.5
        
        #TODO: finish this part, check if to be charged the whole night
    elif EV_type=='with_SC':
        power_to_EV=row['Load_EV_kW_with_SC']
        load_from_EV=load_to_EV-power_to_EV
        new_capacity=0
    elif EV_type=='no_SC':
        power_to_EV=row['Load_EV_kW_no_SC']
        load_from_EV=load_to_EV-power_to_EV
        new_capacity=0
    elif EV_type=='no_EV':
        load_from_EV=load_to_EV
        new_capacity=0
    else:
        raise ValueError('EV_type should be either B2G, with_SC, no_SC or no_EV')
    return load_from_EV,new_capacity    

def nettoProduction(self):
    """
    Calculates the netto production by subtracting the load from the PV generated power
    """

    assert 'PV_Power_kW' in self.pd.columns, 'The column PV_Power_kW is missing'
    assert 'Load_kW' in self.pd.columns, 'The column Load_kW is missing'

    self.pd['NettoProduction'] = self.pd['PV_Power_kW'] - self.pd['Load_kW']
    return None



def optimized_charging(time:pd.DatetimeIndex, max_charge: int = 8, max_AC_power_output: int = 2, max_DC_batterypower: int = 2, max_PV_input: int = 10):
    """
    Calculates power flows, how much is going to and from the battery and how much is being tapped from the grid
    """
    return None

"""
import numpy as np
from scipy.optimize import minimize

def objective_function(X, B):
    return -np.dot(X, B)  # Maximizing X * B is equivalent to minimizing -X * B

def constraint(X, total_sum):
    return np.sum(X) - total_sum  # Constraint on the total sum of X

# Initial guess for vector X
initial_guess_X = np.zeros_like(B)

# Total sum constraint for vector X
total_sum_constraint = 10  # Change this value to your desired total sum

# Bounds for each element of vector X
bounds = [(0, None) for _ in range(len(B))]  # Each element of X should be non-negative

# Define the optimization problem
problem = {
    'fun': objective_function,
    'x0': initial_guess_X,
    'args': (B,),
    'constraints': {'type': 'eq', 'fun': constraint, 'args': (total_sum_constraint,)},
    'bounds': bounds
}

# Solve the optimization problem
result = minimize(**problem)

# Extract the optimized vector X
optimized_X = result.x

print("Optimized vector X:", optimized_X)
print("Maximum value of X * B:", -result.fun)  # Since we were minimizing -X * B


"""



