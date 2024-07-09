
import pandas as pd


def capacity_tariff(self,baseload:bool=False,capacity_tariff:int=41.3087):
    """
    Calculates the capacity tariff cost for the full period which is depending on the highest consumption for each month
    """
    # Check if 'GridFlow' does not contain None values

    
    highest_periods = []
    for month in range(1, 13):
        grouped_data = self.pd["GridFlow_Load"][self.pd["GridFlow_Load"].index.month == month].resample('15min').sum() / 60 if baseload else self.pd["GridFlow"][self.pd["GridFlow"].index.month == month].resample('15min').sum() / 60 #TODO: check if shorter possible
        highest_period = grouped_data.max()
        highest_periods.append(highest_period)
    print(highest_periods)
    Capacity_cost = max((sum(highest_periods) / 12), 2.5) * capacity_tariff #TODO: change so whatever the dataset is, it always returns the right value indep. of the # months
    return Capacity_cost


def refresh_dynamic_tariff(self,A_injection=0.1,B_injection=-0.905,A_offtake=0.1,B_offtake=1.1):
    """
    Calculates the dynamic tariff for a specific time, day and location

    X=A*BELPEX+B
    """ 
    assert self.pd['GridFlow'].dtype == 'float64', "GridPower should be a float64" #TODO: check if enoguh for not none
    assert self.pd['GridFlow_Load'].dtype == 'float64', "GridPower should be a float64" #TODO: check if enoguh for not none
    self.tariff_dynamic_A_injection=A_injection
    self.tariff_dynamic_B_injection=B_injection
    self.tariff_dynamic_A_offtake=A_offtake
    self.tariff_dynamic_B_offtake=B_offtake
    # Check if both 'GridFlow' and 'BelpexFilter' do not contain None values


    # Define a function to calculate the dynamic tariff for a single row
    cost_list = []
    cost_load_list = []
    for _, row in self.pd.iterrows():
        grid_flow = row['GridFlow']
        grid_flow_load=row['GridFlow_Load']
        dynamic_cost = row['Belpex'] # euro per MWh to cent per kWh
        if grid_flow < 0: # Energy is taken off the grid
            cost_per = A_offtake*dynamic_cost+B_offtake # cent cost per kWh
            cost = (-grid_flow)*(cost_per) # total cost
        elif grid_flow > 0: # Energy is injected in the grid
            cost_per = (A_injection*dynamic_cost +B_injection) # cent profit per kWh
            cost = (-grid_flow)*(cost_per) # cent total profit 
        else:
            cost = 0
        
        if grid_flow_load < 0: # Energy is taken off the grid
            cost_per = A_offtake*dynamic_cost+B_offtake # cent cost per kWh
            cost_load = (-grid_flow_load)*(cost_per) # total cost
        elif grid_flow_load > 0: # Energy is injected in the grid
            cost_per = (A_injection*dynamic_cost +B_injection) # cent profit per kWh
            cost_load = (-grid_flow_load)*(cost_per) # cent total profit 
        else:
            cost_load = 0
        cost_list.append(cost*0.01)
        cost_load_list.append(cost_load*0.01)#TODO: add more clear that it is from cents

    
    self.pd['DynamicTariff'] = cost_list
    self.pd['DynamicTariff_Load'] = cost_load_list
    return None

def update_dynamic_tariff(self,):
    """
    Calculates the dynamic tariff for a specific time, day and location.
    
    X = A * BELPEX + B

    Args:
        A_injection (float, optional): Coefficient A for injection. Defaults to 0.1.
        B_injection (float, optional): Coefficient B for injection. Defaults to -0.905.
        A_offtake (float, optional): Coefficient A for offtake. Defaults to 0.1.
        B_offtake (float, optional): Coefficient B for offtake. Defaults to 1.1.
    """
    # Create masks for rows where 'DynamicTariff' and 'DynamicTariff_Load' are NaN
    mask_dynamic_tariff = self.pd['DynamicTariff'].isna()
    mask_dynamic_tariff_load = self.pd['DynamicTariff_Load'].isna()

    # Iterate over DataFrame rows where either mask is True
    for idx, row in self.pd[mask_dynamic_tariff | mask_dynamic_tariff_load].iterrows():
        assert row['GridFlow'] is not None, "GridFlow is None for row {}".format(idx)
        assert row['GridFlow_Load'] is not None, "GridFlow_Load is None for row {}".format(idx)
        assert row['Belpex'] is not None, "Belpex is None for row {}".format(idx)

        grid_flow = row['GridFlow']
        grid_flow_load = row['GridFlow_Load']
        dynamic_cost = row['Belpex']  # euro per MWh to cent per kWh

        # Calculate dynamic tariff for grid flow
        if grid_flow < 0:  # Energy is taken off the grid
            cost_per = self.tariff_dynamic_A_offtake * dynamic_cost + self.tariff_dynamic_B_offtake  # cent cost per kWh
            cost = (-grid_flow) * (cost_per)  # total cost
        elif grid_flow > 0:  # Energy is injected into the grid
            cost_per = self.tariff_dynamic_A_injection * dynamic_cost + self.tariff_dynamic_B_injection  # cent profit per kWh
            cost = (-grid_flow) * (cost_per)  # cent total profit
        else:
            cost = 0
        
        # Calculate dynamic tariff for grid flow load
        if grid_flow_load < 0:  # Energy is taken off the grid
            cost_per = self.tariff_dynamic_A_offtake * dynamic_cost + self.tariff_dynamic_B_offtake  # cent cost per kWh
            cost_load = (-grid_flow_load) * (cost_per)  # total cost
        elif grid_flow_load > 0:  # Energy is injected into the grid
            cost_per = self.tariff_dynamic_A_injection * dynamic_cost + self.tariff_dynamic_B_injection  # cent profit per kWh
            cost_load = (-grid_flow_load) * (cost_per)  # cent total profit
        else:
            cost_load = 0

        # Update the DataFrame with calculated values only where they were NaN
        if pd.isna(self.pd.at[idx, 'DynamicTariff']):
            self.pd.at[idx, 'DynamicTariff'] = cost * 0.01  # convert to euros
        if pd.isna(self.pd.at[idx, 'DynamicTariff_Load']):
            self.pd.at[idx, 'DynamicTariff_Load'] = cost_load * 0.01  # convert to euros

    return None

def refresh_dual_tariff(self, peak_tariff:int=0.1701, offpeak_tariff:int=0.1463,fixed_tariff:int=0.01554,injection_tariff:int=0.03):
    
    """
    Calculates the dual tariff for a specific time, day and colation
    """

    # Check if 'GridFlow' does not contain None values

    assert self.pd['GridFlow'].dtype == 'float64', "GridPower should be a float64"

    cost_list = []
    cost_load_list = []
    # Define a function to calculate the dual tariff for a single row
    for _, row in self.pd.iterrows():
        
        #Calculates the dual tariff for a single row
        grid_flow = row['GridFlow']
        grid_flow_load=row['GridFlow_Load']
        if grid_flow < 0: # Energy is being consumed
                
            if row.name.weekday() < 5:  # Weekdays (Monday=0, Sunday=6)
                if 7 <= row.name.hour < 22:  # Peak hours from 7:00 to 22:00
                    variable_tariff = peak_tariff
                else:
                    variable_tariff = offpeak_tariff
            else:  # Weekends
                variable_tariff = offpeak_tariff

            cost = (variable_tariff+fixed_tariff) * (-grid_flow)
        else:  # Energy is being produced
            cost = injection_tariff * (-grid_flow)

        if grid_flow_load < 0: # Energy is being consumed
                
            if row.name.weekday() < 5:  # Weekdays (Monday=0, Sunday=6)
                if 7 <= row.name.hour < 22:  # Peak hours from 7:00 to 22:00
                    variable_tariff = peak_tariff
                else:
                    variable_tariff = offpeak_tariff
            else:  # Weekends
                variable_tariff = offpeak_tariff

            cost_load= (variable_tariff+fixed_tariff) * (-grid_flow_load)
        else:  # Energy is being produced
            cost_load = injection_tariff * (-grid_flow_load)

        cost_list.append(cost)
        cost_load_list.append(cost_load)
    self.pd['DualTariff'] = cost_list
    self.pd['DualTariff_Load'] = cost_load_list    

    
    return None


def update_dual_tariff(self):
    """
    Calculates the dual tariff for a specific time, day, and location.
    
    Args:
        peak_tariff (float): The peak tariff rate.
        offpeak_tariff (float): The off-peak tariff rate.
        fixed_tariff (float): The fixed tariff rate.
        injection_tariff (float): The tariff rate for injected energy.
    """
    
    # Check if 'GridFlow' does not contain None values
    assert self.pd['GridFlow'].dtype == 'float64', "GridFlow should be a float64"
    
    # Create masks for rows where 'DualTariff' and 'DualTariff_Load' are NaN
    mask_dual_tariff = self.pd['DualTariff'].isna()
    mask_dual_tariff_load = self.pd['DualTariff_Load'].isna()
    
    # Iterate over DataFrame rows where either mask is True
    for idx, row in self.pd[mask_dual_tariff | mask_dual_tariff_load].iterrows():
        assert row['GridFlow'] is not None, "GridFlow is None for row {}".format(idx)
        assert row['GridFlow_Load'] is not None, "GridFlow_Load is None for row {}".format(idx)

        
        grid_flow = row['GridFlow']
        grid_flow_load = row['GridFlow_Load']
        
        if grid_flow < 0:  # Energy is being consumed
            if row.name.weekday() < 5:  # Weekdays (Monday=0, Sunday=6)
                if 7 <= row.name.hour < 22:  # Peak hours from 7:00 to 22:00
                    variable_tariff = self.tariff_dual_peak
                else:
                    variable_tariff = self.tariff_dual_offpeak
            else:  # Weekends
                variable_tariff = self.tariff_dual_offpeak
            
            cost = (variable_tariff + self.tariff_dual_fixed) * (-grid_flow)
        else:  # Energy is being produced
            cost = self.tariff_dual_injection * (-grid_flow)
        
        if grid_flow_load < 0:  # Energy is being consumed
            if row.name.weekday() < 5:  # Weekdays (Monday=0, Sunday=6)
                if 7 <= row.name.hour < 22:  # Peak hours from 7:00 to 22:00
                    variable_tariff = self.tariff_dual_peak
                else:
                    variable_tariff = self.tariff_dual_offpeak
            else:  # Weekends
                variable_tariff = self.tariff_dual_offpeak
            
            cost_load = (variable_tariff + self.tariff_dual_fixed) * (-grid_flow_load)
        else:  # Energy is being produced
            cost_load = self.tariff_dual_injection * (-grid_flow_load)
        
        # Update the DataFrame with calculated values only where they were NaN
        if pd.isna(self.pd.at[idx, 'DualTariff']):
            self.pd.at[idx, 'DualTariff'] = cost
        if pd.isna(self.pd.at[idx, 'DualTariff_Load']):
            self.pd.at[idx, 'DualTariff_Load'] = cost_load
    
    return None