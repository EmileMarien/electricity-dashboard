
from typing import List
import pandas as pd


def get_irradiance(self):
    """
    Returns the irradiance data
    """
    return self.pd['DiffRad']

def get_datetimerange(self):
    return self.pd.index #TODO: how??

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

def get_PV_Power_kW(self):
    """
    Returns the PV generated power data
    """
    return self.pd['PV_Power_kW']

def get_energy_TOT(self,column_name:str='Load_kW',peak:str='all'):
    """
    Calculates the total energy in kWh for the entire year in the DataFrame. The energy is calculated for the specified power values and peak or offpeak period.

    Args:
    column_name (str): The name of the column to be used for the calculation. Choose between: 'Load_kW', 'GridPower', 'PV_Power_kW'. Default: 'Load_kW'
    peak (str): The period to calculate the energy. Choose between: 'peak', 'offpeak'. Default: 'peak'
    
    Returns:
        float: The total energy in kWh in the period to the load, grid or from the PV between 8h and 18h during the week for 'peak' and outside those hours for 'offpeak'
    """

    # Select only load data
    if column_name=='Load_kW':
        df_load=self.pd['Load_kW']
    elif column_name=='GridFlow':
        df_load=self.pd['GridFlow']
    elif column_name=='PV_Power_kW':
        df_load=self.pd['PV_Power_kW']

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
    power=get_average_per_hour(self,"PV_Power_kW")
    
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

def get_total_cost(self,tariff: str='DynamicTariff',start_date:str=self.pd.index[0],end_date:str=self.pd.index[-1],interval_str:str="10min",purchase_rate_injection:float=0.00414453,purchase_rate_consumption=0.0538613,data_management_cost: float =13.95,capacity_rate: float=41.3087,fixed_component_dual=111.3,fixed_component_dynamic=100.7,excise_duty_energy_contribution_rate=0,include_PV:bool=True): #TODO: fix
    """
    Calculate the electricity cost for a given solar panel configuration and tariff.

    Args:
    fixed_component_dual [€/year]
    fixed_component_dynamic [€/year]
    """


    print("1/4: start calculations")
    self.pd.filter_data_by_date_interval(start_date=start_date,end_date=end_date,interval_str=interval_str)
    #TODO: check if the right data is available (no None rows or columns)
    
    
    ## Electricity cost
    energy_cost=sum(self.pd[tariff])

    fixed_component = fixed_component_dual if tariff=='DualTariff' else fixed_component_dynamic
    ## Network rates
    #data_management_cost

    ## Special excise duty and energy contribution
    levy_cost=excise_duty_energy_contribution_rate*(get_total_injection_and_consumption()[2]+get_total_injection_and_consumption()[3])

    # Calculate the purchase cost
    purchase_cost_injection=purchase_rate_injection*(get_total_injection_and_consumption()[0]+get_total_injection_and_consumption()[1])
    purchase_cost_consumption=purchase_rate_consumption*(get_total_injection_and_consumption()[2]+get_total_injection_and_consumption()[3])

    purchase_cost=purchase_cost_injection+purchase_cost_consumption
    capacity_cost = max(-(get_monthly_peaks('GridFlow').sum() / 12), 2.5) * capacity_rate #TODO: check calculations

    # Total cost
    cost=energy_cost+data_management_cost+purchase_cost+capacity_cost+levy_cost+fixed_component
    print("Components of the cost:")
    print("Fixed component:", fixed_component)
    print("Energy cost:", energy_cost)
    print("Data management cost:", data_management_cost)
    print("Purchase cost (injection):", purchase_cost_injection)
    print("Purchase cost (consumption):", purchase_cost_consumption)
    print("Capacity cost:", capacity_cost)
    print("Levy cost:", levy_cost)
    print("Total cost:", cost)
    print("Total production:",get_energy_TOT(column_name='PV_Power_kW'))
    print("Total injection: peak:", get_total_injection_and_consumption()[0],"offpeak:",get_total_injection_and_consumption()[1])    
    print("Total consumption: peak:", get_total_injection_and_consumption()[2],"offpeak:",get_total_injection_and_consumption()[3])

    return cost

def get_npv(battery_cost, total_solar_panel_cost, inverter_cost, discount_rate, annual_degradation):
    
    initial_cash_flow=get_total_cost()-
    # Calculate the least common multiple (LCM) of battery and solar panel lifetimes

    installation_cost = total_solar_panel_cost*0.3/0.35
    print("Installation cost:", installation_cost*(1+0.21))
    BOS_cost = total_solar_panel_cost/0.35*0.125
    print("BOS_cost:", BOS_cost*(1+0.21))
    inverter = inverter_cost + (inverter_cost + battery_cost) / pow(1 + discount_rate, 10) + \
                      (inverter_cost + battery_cost) / pow(1 + discount_rate, 20) - \
                      (inverter_cost + battery_cost) / pow(1 + discount_rate, 25) 
    print("Inverter cost:",inverter)
    print("total_solar_panel_cost:",total_solar_panel_cost*(1+0.21))
    capex = (BOS_cost + installation_cost + total_solar_panel_cost)*(1+0.21)  + inverter_cost  + battery_cost  # multiplication for installation_cost + maintenance_cost
   
    investment_cost = capex+ \
                      (inverter_cost + battery_cost) / pow(1 + discount_rate, 10) + \
                      (inverter_cost + battery_cost) / pow(1 + discount_rate, 20) - \
                      (inverter_cost + battery_cost) / pow(1 + discount_rate, 25) 
    print("Investment cost:", investment_cost)
    Year_1_payback = initial_cash_flow/investment_cost
    payback = 1/Year_1_payback
    print("payback",payback)
    print("Year 1 payback:", Year_1_payback)
    cost_savings = sum((initial_cash_flow * pow(1 - annual_degradation, t - 1)) / pow(1 + discount_rate, t) for t in range(1, 26))
    print("Total cost savings:", cost_savings)
    npv = -investment_cost + cost_savings
    return npv