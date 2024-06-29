
def PV_generated_power(self,cell_area:int=2, panel_count:int=1, T_STC:int=25, efficiency_max = 0.223, Temp_coeff = -0.0026 ):
    """
    Calculates the PV generated power in [kW] based on the DirectIrradiance column in the DataFrame.
    The formula used is:
    P = (1/1000)*efficiency_max*cell_area*DirectIrradiance*(1+Temp_coeff)*(T_STC-T_cell)*panel_count
    
    Args:
    - P is the PV generated power in [kW]
    - efficiency_max is the maximum efficiency of the panel
    - cell_area is the area of the cell in [m^2]
    - DirectIrradiance is the direct irradiance in [W/m^2]
    - Temp_coeff is the temperature coefficient of the panel
    - T_STC is the standard test condition temperature in [°C]
    - T_cell is the cell temperature in [°C]
    - panel_count is the number of panels

    Returns:
    - None   
    """
    
    T_cell=self.pd['T_RV_degC']
    # Check if the 'beamirradiance' column is empty
    if 'DirectIrradiance' in self.pd.columns and not self.pd['DirectIrradiance'].empty:
        # Calculate the PV generated power in [kW]
        self.pd['PV_generated_power'] = (1/1000)*efficiency_max*cell_area*self.pd['DirectIrradiance']*(1+(Temp_coeff*(T_cell-T_STC)))*panel_count
    else:
        raise ValueError("The 'DirectIrradiance' column is empty or not present in the DataFrame")
    return None

def PV_generated_power_SPP(self,SPP_path:str,sheet_name:str,max_power:float,efficiency_coefficient):
    """
    Calculates the PV generated power in [kW] based on the provided synthetic production profile (SPP) in the Excel file.
    """

    # Load the synthetic production profile (SPP) from the Excel file
    SPP = self.pd.read_excel(SPP_path, sheet_name=sheet_name)
    
    # get the right column of the excel
    
    if 'DirectIrradiance' in SPP.columns:
        # Calculate the PV generated power in [kW] based on the synthetic production profile (SPP)
        SPP['PV_generated_power'] = max_power * SPP['5414494999996'] * efficiency_coefficient
    else:
        raise ValueError("The 'DirectIrradiance' column is not present in the synthetic production profile (SPP)")

    # Check if the 'time' column is present in the synthetic production profile (SPP)
    if 'UTC' in SPP.columns:
        # Merge the synthetic production profile (SPP) with the DataFrame
        self.pd = self.pd.merge(SPP, on='time', how='left')
        
        # Calculate the PV generated power in [kW] based on the synthetic production profile (SPP)
        self.pd['PV_generated_power'] = max_power * self.pd[sheet_name] * efficiency_coefficient
    else:
        raise ValueError("The 'time' column is not present in the synthetic production profile (SPP)")
    return None

PV_generated_power_SPP(SPP_path='solar_load_ROI_calculation/data/SPP.xlsx',sheet_name='5414494999996',max_power=100,efficiency_coefficient=0.223)