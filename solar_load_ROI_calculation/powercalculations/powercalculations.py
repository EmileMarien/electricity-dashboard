
from math import acos, asin, cos, pi, sin, tan
import math
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from torch import sgn

class PowerCalculations():
    def __init__(self, file_path_irradiance: str="",file_path_SPP:str="",file_path_SLP:str="",file_path_load: str="", file_path_combined:str=""):
        """
        Initializes the PowerCalculations class with the given dataset
        
        Args:
        file_path (str): The file path to the Excel file containing the dataset 
        dataset (DataFrame): The dataset to be used for the calculations if file_path is not provided       
        """
        if file_path_combined != "":
            # Use the dataset directly if provided
            merged_df = pd.read_excel(file_path_combined)
            print(merged_df)
        elif (file_path_SPP != "") and (file_path_SLP != ""):
            # Read the dataset from the Excel file
            SPP = pd.read_excel(file_path_SPP,sheet_name='Ex-ante 2022 (IP8)')
            # Check if all required columns are present
            required_columns = ['UTC', '5414494999996']
            missing_columns = [col for col in required_columns if col not in SPP.columns]
            assert not missing_columns, f"The following columns are missing: {', '.join(missing_columns)}"
            self.pd=SPP['UTC','5414494999996']

            # Read the dataset from the Excel file
            SLP = pd.read_excel(file_path_SLP,sheet_name='ENU_UTC')
            # Check if all required columns are present
            required_columns = ['UTC', 'EN']
            missing_columns = [col for col in required_columns if col not in SLP.columns]
            assert not missing_columns, f"The following columns are missing: {', '.join(missing_columns)}"
            self.pd = self.pd.merge(SLP, on='UTC', how='outer') #TODO: check if this is the right way to merge & correct reading of info
        else:
            assert file_path_irradiance.endswith('.xlsx'), 'The file must be an Excel file'
            assert file_path_load.endswith('.xlsx'), 'The file must be an Excel file'
            
            # Read the dataset from the Excel file
            irradiance_df = pd.read_excel(file_path_irradiance)
            
            # Read the Excel file into a DataFrame
            load_df = pd.read_excel(file_path_load)

            # Assert that 'Load_kW' and 'DateTime' columns are present in the Excel file
            assert 'DateTime' in irradiance_df.columns, "'DateTime' column not found in the Irradiance Excel file"
            assert 'DateTime' in load_df.columns, "'DateTime' column not found in the Load Excel file"
            
            # Merge the DataFrame with the one read from excel
            merged_df = pd.merge(irradiance_df, load_df, on='DateTime', how='outer') 
        
            # Check if all required columns are present
            required_columns = ['DateTime', 'GlobRad', 'DiffRad', 'T_RV_degC', 'T_CommRoof_degC','Load_kW']
            missing_columns = [col for col in required_columns if col not in merged_df.columns]
            assert not missing_columns, f"The following columns are missing: {', '.join(missing_columns)}"


            expected_columns = ['DateTime', 'Load_kW', 'GlobRad', 'DiffRad', 'T_RV_degC', 'T_CommRoof_degC']
            self.pd=merged_df[expected_columns]
        
        #Set a datetime index
        self.pd.set_index('DateTime', inplace=True)
        self.pd.index = pd.to_datetime(self.pd.index)

        # Initialize the columns that will be used for the calculations
        self.pd['DirectIrradiance'] = None    # [W]  
        self.pd['PV_generated_power'] = None  # [kW]
        self.pd['GridFlow'] = None           # [kW], if neg, then subtracted from grid, if pos the added to the grid
        self.pd['BatteryCharge'] = None       # [kW]
        self.pd['NettoProduction'] = None # Netto production is the difference between the PV generated power and the load
        self.pd['EVLoad'] = None # [kW]
        self.pd['PowerLoss'] = None # [kW]
        self.pd['BatteryFlow'] = None

    # Imported methods
    from ._datacleaning import filter_data_by_date_interval
    from ._datacleaning import interpolate_columns
    from ._datacleaning import find_duplicate_indices
    from ._datacleaning import empty_column
    from ._datacleaning import update_column

    from ._pvpower import PV_generated_power
    from ._pvpower import PV_generated_power_SPP

    from ._visualisations import plot_columns
    from ._visualisations import plot_dataframe
    from ._visualisations import plot_series
    
    from ._directirradiance import calculate_direct_irradiance
    from ._directirradiance import calculate_solar_angles

    from ._powerflows import power_flow
    from ._powerflows import nettoProduction
    from ._powerflows import power_flow_old
    
    from ._getters import get_dataset
    from ._getters import get_irradiance
    from ._getters import get_load
    from ._getters import get_direct_irradiance
    from ._getters import get_PV_generated_power
    from ._getters import get_energy_TOT
    from ._getters import get_average_per_hour
    from ._getters import get_grid_power
    from ._getters import get_columns
    from ._getters import get_monthly_peaks
    from ._getters import get_total_injection_and_consumption
    from ._getters import get_average_per_minute_day

    from ._export import export_dataframe_to_excel

    from ._EVload import add_EV_load
