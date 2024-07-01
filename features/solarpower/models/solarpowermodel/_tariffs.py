
def capacity_tariff(self, tariff:int=41.3087,baseload:bool=False):
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
    Capacity_cost = max((sum(highest_periods) / 12), 2.5) * tariff #TODO: change so whatever the dataset is, it always returns the right value indep. of the # months
    return Capacity_cost


def dynamic_tariff(self,A_injection=0.1,B_injection=-0.905,A_offtake=0.1,B_offtake=1.1):
    """
    Calculates the dynamic tariff for a specific time, day and location

    X=A*BELPEX+B
    """ 
    # Check if both 'GridFlow' and 'BelpexFilter' do not contain None values


    # Define a function to calculate the dynamic tariff for a single row
    def calculate_tariff_row(row):
        grid_flow = row['GridFlow']
        grid_flow_load=row['GridFlow_Load']
        dynamic_cost = row['BelpexFilter'] # euro per MWh to cent per kWh
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
        return (cost*0.01,cost_load*0.01) #TODO: add more clear that it is from cents

    
    self.pd['DynamicTariff','DynamicTariff_Load'] = self.pd.apply(
        lambda row: calculate_tariff_row(row=row), axis=1
    )
    return None


def dual_tariff(self, peak_tariff:int=0.1701, offpeak_tariff:int=0.1463,fixed_tariff:int=0.01554,injection_tariff:int=0.03):
    
    """
    Calculates the dual tariff for a specific time, day and colation
    """

    # Check if 'GridFlow' does not contain None values

    assert self.pd['GridFlow'].dtype == 'float64', "GridPower should be a float64"

    # Define a function to calculate the dual tariff for a single row
    def calculate_tariff_row(row, peak_tariff, offpeak_tariff, fixed_tariff=0):
        
        #Calculates the dual tariff for a single row
        grid_flow = row['GridFlow']
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
        return cost
    
    # Apply the calculation function to each row with vectorized operations
    self.pd['DualTariff'] = self.pd.apply(
        lambda row: calculate_tariff_row(row=row, peak_tariff=peak_tariff,offpeak_tariff=offpeak_tariff, fixed_tariff=fixed_tariff), axis=1
        )
    
    return None


