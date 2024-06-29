
def dual_tariff(self, peak_tariff:int=0.1701, offpeak_tariff:int=0.1463,fixed_tariff:int=0.01554,injection_tariff:int=0.03):
    
    #Calculates the dual tariff for a specific time, day and colation
    
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


