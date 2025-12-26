

from elecmodel.models.solarpanel.solarpanel import SolarPanel


def refresh_PV_Power_kW(self,new_solarpanel:SolarPanel=SolarPanel(),T_STC:int=25):
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
    # Update the solarpanel object with the new solarpanel object
    self.solarpanel=new_solarpanel
    self.T_STC=T_STC
    # Update the parameters with values from the solarpanel object
    cell_area=self.solarpanel.get_panel_surface()
    panel_count=self.solarpanel.get_solar_panel_count()
    efficiency_max=self.solarpanel.get_panel_efficiency()
    Temp_coeff=self.solarpanel.get_temperature_coefficient()

    
    T_cell=self.pd['T_RV_degC']
    # Check if the 'beamirradiance' column is empty
    if 'DirectIrradiance' in self.pd.columns and not self.pd['DirectIrradiance'].empty: #TODO: return which rows are empty so also check rows that are empty
        # Calculate the PV generated power in [kW]
        self.pd['PV_Power_kW'] = (1/1000)*efficiency_max*cell_area*self.pd['DirectIrradiance']*(1+(Temp_coeff*(T_cell-T_STC)))*panel_count
    else:
        raise ValueError("The 'DirectIrradiance' column is empty or not present in the DataFrame")
    return None

def PV_Power_kW_SPP(self,SPP_path:str,sheet_name:str,max_power:float,efficiency_coefficient):
    """
    Calculates the PV generated power in [kW] based on the provided synthetic production profile (SPP) in the Excel file.
    """

    # Load the synthetic production profile (SPP) from the Excel file
    SPP = self.pd.read_excel(SPP_path, sheet_name=sheet_name)
    
    # get the right column of the excel
    
    if 'DirectIrradiance' in SPP.columns:
        # Calculate the PV generated power in [kW] based on the synthetic production profile (SPP)
        SPP['PV_Power_kW'] = max_power * SPP['5414494999996'] * efficiency_coefficient
    else:
        raise ValueError("The 'DirectIrradiance' column is not present in the synthetic production profile (SPP)")

    # Check if the 'time' column is present in the synthetic production profile (SPP)
    if 'UTC' in SPP.columns:
        # Merge the synthetic production profile (SPP) with the DataFrame
        self.pd = self.pd.merge(SPP, on='time', how='left')
        
        # Calculate the PV generated power in [kW] based on the synthetic production profile (SPP)
        self.pd['PV_Power_kW'] = max_power * self.pd[sheet_name] * efficiency_coefficient
    else:
        raise ValueError("The 'time' column is not present in the synthetic production profile (SPP)")
    return None

#PV_Power_kW_SPP(SPP_path='solar_load_ROI_calculation/data/SPP.xlsx',sheet_name='5414494999996',max_power=100,efficiency_coefficient=0.223)


def update_PV_Power_kW(self):
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
    # Update the parameters with values from the solarpanel object
    cell_area = self.solarpanel.get_panel_surface()
    panel_count = self.solarpanel.get_solar_panel_count()
    efficiency_max = self.solarpanel.get_panel_efficiency()
    Temp_coeff = self.solarpanel.get_temperature_coefficient()
    T_STC = self.T_STC
    
    # Check if necessary columns are present
    if 'DirectIrradiance' not in self.pd.columns:
        raise ValueError("The 'DirectIrradiance' column is not present in the DataFrame")
    
    if 'T_RV_degC' not in self.pd.columns:
        raise ValueError("The 'T_RV_degC' column is not present in the DataFrame")
    
    # Calculate T_cell based on 'T_RV_degC'
    T_cell = self.pd['T_RV_degC']
    
    # Calculate PV power only for rows where 'PV_Power_kW' is NaN
    mask = self.pd['PV_Power_kW'].isna()
    
    self.pd.loc[mask, 'PV_Power_kW'] = (
        (1/1000) * efficiency_max * cell_area * self.pd.loc[mask, 'DirectIrradiance'] * 
        (1 + (Temp_coeff * (T_cell - T_STC))) * panel_count
    )
    
    return None
