
def dynamic_tariff(self):
    """
    Calculates the dynamic tariff for a specific time, day and location
    """ 
    # Define a function to calculate the dynamic tariff for a single row
    def calculate_tariff_row(row):
        grid_flow = row['GridFlow']
        dynamic_cost = row['BelpexFilter'] # euro per MWh to cent per kWh
        if grid_flow < 0: # Energy is being consumed
            cost_per = ((0.1*dynamic_cost+1.1)*1.06) # cent cost per kWh
            cost = (-grid_flow)*(cost_per) # total cost
        elif grid_flow > 0: # Energy is being injected in the grid
            cost_per = (0.1*dynamic_cost - 0.905) # cent profit per kWh
            cost = (-grid_flow)*(cost_per) # cent total profit 
        else:
            cost = 0
        return (cost*0.01)

    
    self.pd['DynamicTariff'] = self.pd.apply(
        lambda row: calculate_tariff_row(row=row), axis=1
    )
    return None