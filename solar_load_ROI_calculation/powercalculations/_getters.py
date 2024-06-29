
from typing import List
import pandas as pd


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
    #print(self.pd.index.dtype)
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

def get_energy_TOT(self,column_name:str='Load_kW',peak:str='all'):
    """
    Calculates the total energy in kWh for the entire year in the DataFrame. The energy is calculated for the specified power values and peak or offpeak period.

    Args:
    column_name (str): The name of the column to be used for the calculation. Choose between: 'Load_kW', 'GridPower', 'PV_generated_power'. Default: 'Load_kW'
    peak (str): The period to calculate the energy. Choose between: 'peak', 'offpeak'. Default: 'peak'
    
    Returns:
        float: The total energy in kWh in the period to the load, grid or from the PV between 8h and 18h during the week for 'peak' and outside those hours for 'offpeak'
    """

    # Select only load data
    if column_name=='Load_kW':
        df_load=self.pd['Load_kW']
    elif column_name=='GridFlow':
        df_load=self.pd['GridFlow']
    elif column_name=='PV_generated_power':
        df_load=self.pd['PV_generated_power']

    else:
        AssertionError('The column_name must be either Load_kW or PowerGrid')

    if peak=='peak':
        # Select data between 8:00 and 18:00 for the entire year
        df_filtered = df_load[(df_load.index.hour >= 8) & (df_load.index.hour < 18) & (df_load.index.weekday < 5)]
    elif peak=='offpeak':
        # Select data outside 8:00 and 18:00 for the entire year
        df_filtered = df_load[((df_load.index.hour < 8) | (df_load.index.hour >= 18)) & (df_load.index.weekday < 5) | (df_load.index.weekday >= 5)]
    elif peak=='all':
        df_filtered = df_load
    else:
        AssertionError('The peak must be either peak or offpeak')

    # Sum the 'Load_kW' values in the filtered DataFrame
    load_tot_day = df_filtered.sum()
    
    # Check if the input data contains NA values
    assert not df_load.isnull().values.any(), 'The input data contains NA values'
    #Integrate the power over time to get the energy in [kWh]
    interval = pd.Timedelta(df_load.index.freq).total_seconds() / 3600 # Convert seconds to hours
    energy_peak=load_tot_day*interval# [kWh]

    return energy_peak

def get_columns(self,columns:List[str]):
    """
    Returns the dataset with the specific columns
    """
    if not (isinstance(col, str) for col in columns):
        return None
    
    if not(all(col in self.pd.columns for col in columns)):
        return None
    
    assert all(isinstance(col, str) for col in columns), 'The columns must be strings'
    assert all(col in self.pd.columns for col in columns), 'The columns must be present in the DataFrame'

    return self.pd[columns]

def get_PV_energy_per_hour(self):
    power=get_average_per_hour(self,"PV_generated_power")
    
def get_average_per_hour(self, column_name: str = 'Load_kW'):
    """
    Calculates the average power per hour for each hour of the day based on the entire year in the DataFrame. in kW

    Returns:
        pandas.Series: A Series containing the average 'Load_kW' for each hour of the day.
        The index of the Series is the hour (0-23).
    """

    # Extract the hour component from the index
    hour_component = self.pd.index.hour

    # Group the data by the hour component and calculate the mean
    df_hourly_avg = self.pd.groupby(hour_component)[column_name].mean()

    return df_hourly_avg

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

def get_average_per_day(self,column_name:str='Load_kW'):
    """
    Calculates the average load per day for each day of the year based on the entire year in the DataFrame. in kW

    Returns:
        pandas.Series: A Series containing the average 'Load_kW' for each day of the year.
        The index of the Series is the day of the year (1-365).
    """

    # Resample the DataFrame by day ('D') and calculate the mean
    df_daily_avg = self.pd[column_name].resample('D').mean()

    return df_daily_avg

def get_max_per_hour(self,column_name:str='Load_kW'):
    """
    Calculates the maximum load per hour for each hour in the day based on the entire year in the DataFrame. in kW

    Returns:
        pandas.Series: A Series containing the maximum 'Load_kW' for each hour of the day.
        The index of the Series is the hour (0-23).
    """

    # Resample the DataFrame by hour ('H') and calculate the mean
    df_hourly_max = self.pd[column_name].resample('h').max()

    return df_hourly_max

def get_grid_power(self):
    return [self.pd['GridFlow'], self.pd['BatteryCharge']]

def get_monthly_peaks(self,column_name:str='Load_kW'):
    """
    Calculates the monthly peaks for the specified column in the DataFrame. in kW

    Returns:
        pandas.Series: A Series containing the monthly peaks for the specified column.
        The index of the Series is the month (1-12).
    """

    # Group the data by the month and calculate the maximum value
    intervalled_data = self.pd[column_name].resample('15min').mean()
    df_monthly_peaks = intervalled_data.groupby(intervalled_data.index.month).min()
    return df_monthly_peaks


def get_total_injection_and_consumption(self):
    """
    Calculates the total injection and consumption for the entire year in the DataFrame. in kWh

    Returns:
        tuple: A tuple containing the total injection and consumption in kWh.
    """
    # injection during peak hours
    total_injection_peak = self.pd['GridFlow'][(self.pd['GridFlow'] > 0) & (self.pd.index.hour >= 8) & (self.pd.index.hour < 18) & (self.pd.index.weekday < 5)].sum()

    # injection during offpeak hours
    total_injection_offpeak = self.pd['GridFlow'][(self.pd['GridFlow'] > 0) & (((self.pd.index.hour < 8) | (self.pd.index.hour >= 18)) & (self.pd.index.weekday < 5) | (self.pd.index.weekday >= 5))].sum()

    # consumption during peak hours
    total_consumption_peak = -self.pd['GridFlow'][(self.pd['GridFlow'] < 0) & (self.pd.index.hour >= 8) & (self.pd.index.hour < 18) & (self.pd.index.weekday < 5)].sum()

    # consumption during offpeak hours
    total_consumption_offpeak = -self.pd['GridFlow'][(self.pd['GridFlow'] < 0) & (((self.pd.index.hour < 8) | (self.pd.index.hour >= 18)) & (self.pd.index.weekday < 5) | (self.pd.index.weekday >= 5))].sum()
    
    #Integrate the power over time to get the energy in [kWh]
    interval = pd.Timedelta(self.pd['GridFlow'].index.freq).total_seconds() / 3600 # Convert seconds to hours
    total_injection_peak_kWh = total_injection_peak * interval        # [kWh]
    total_injection_offpeak_kWh = total_injection_offpeak * interval  # [kWh]
    total_consumption_peak_kWh = total_consumption_peak * interval    # [kWh]
    total_consumption_offpeak_kWh = total_consumption_offpeak * interval  # [kWh]

    return total_injection_peak_kWh, total_injection_offpeak_kWh, total_consumption_peak_kWh, total_consumption_offpeak_kWh