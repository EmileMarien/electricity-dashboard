
from typing import List

def get_irradiance(self):
    """
    Returns the irradiance data
    """
    return self.pd['DiffRad']

def get_load(self):
    """
    Returns the load data
    """
    return self.pd['Load_kW']   

def get_dataset(self):
    """
    Returns the dataset
    """
    return self.pd

def get_direct_irradiance(self):
    """
    Returns the direct irradiance data
    """
    return self.pd['DirectIrradiance']

def get_PV_generated_power(self):
    """
    Returns the PV generated power data
    """
    return self.pd['PV_generated_power']

def get_grid_cost_perhour(self,calculationtype:str="DualTariff"):
    """
    Returns the grid cost data based on the specified type of cost calculation
    """
    return self.pd[calculationtype]

def get_grid_cost_total(self,calculationtype:str="DualTariff"):
    cost_perhour=self.pd[calculationtype]
    cost_total=sum(cost_perhour)
    return cost_total

def get_columns(self,columns:List[str]):
    """
    Returns the dataset with the specific columns
    """

    assert all(col in self.pd.columns for col in columns), 'The columns must be present in the DataFrame'

    return self.pd[columns]

def get_total_energy_from_grid(self):
    """
    Returns the total energy in kWh taken from the grid
    """
    return sum(self.pd['GridFlow'])

def get_average_per_minute_day(self,column_name:str='Load_kW'):
    """
    Calculates the average load per minute for each day of the year based on the entire year in the DataFrame. in kW

    Returns:
        pandas.Series: A Series containing the average 'Load_kW' for each minute of the day.
        The index of the Series is the minute of the day (0-1439).
    """


    # Group by hour and minute and calculate average value
    avg_by_time = self.pd.groupby([self.pd.index.hour, self.pd.index.minute])[column_name].mean()        
    avg_by_time.index = [f"{x[0]:02d}:{x[1]:02d}" for x in avg_by_time.index]

    return avg_by_time
def get_total_energy_to_grid(self):
    """
    Returns the total energy in kWh sent to the grid
    """
    return -sum(self.pd['GridFlow'])

def get_total_energy_from_battery(self):
    """
    Returns the total energy in kWh taken from the battery
    """
    return sum(self.pd['BatteryCharge'])
