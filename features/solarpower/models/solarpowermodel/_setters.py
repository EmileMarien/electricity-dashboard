

import pandas as pd

#TODO: how to merge? don't forget to set datetimeindex

def set_load_df(self, df_load: pd.DataFrame):
    
    assert 'Load_kW' in df_load.columns and 'DateTime' in df_load.columns
    if not (df_load.index.name == 'DateTime' and df_load.index.format() == 'datetime64[ns]'):
        df_load.set_index('DateTime', inplace=True)
        df_load.index = pd.to_datetime(df_load.index)

    if self.pd.empty:
        self.pd['Load_kW'] = df_load
    else:
        self.pd = self.pd.merge(df_load, how='outer', left_index=True, right_index=True)
    return None

def set_load_slp_df(self, set:str,yearly_average:int):
    if set == 'SLP_2022':
        SLP=pd.read_csv('SLP_2022.csv')
        SLP['DateTime'] = pd.to_datetime(SLP['DateTime'])
        SLP.set_index('DateTime', inplace=True)
        SLP['Load_kW'] = SLP['Load_kW']*yearly_average
        self.pd['Load_kW'] = SLP['Load_kW']           # add data independent of the year  
    elif set == 'SLP_2023':
        SLP=pd.read_csv('SLP_2023.csv')
        SLP['DateTime'] = pd.to_datetime(SLP['DateTime'])
        SLP.set_index('DateTime', inplace=True)
        SLP['Load_kW'] = SLP['Load_kW']*yearly_average
        self.pd['Load_kW'] = SLP['Load_kW']
    return None



def append_load_df(self, df_load: pd.DataFrame):      
    assert 'Load_kW' in df_load.columns and 'DateTime' in df_load.columns
    if not (df_load.index.name == 'DateTime' and df_load.index.format() == 'datetime64[ns]'):
        df_load.set_index('DateTime', inplace=True)
        df_load.index = pd.to_datetime(df_load.index)

    if 'Load_kW' not in self.pd.columns:
        self.pd['Load_kW'] = df_load['Load_kW']
    else:
        self.pd['Load_kW'] = pd.concat([self.pd['Load_kW'], df_load['Load_kW']], axis=1, join="outer")
    if 'DateTime' not in self.pd.columns:
        self.pd['DateTime'] = df_load['DateTime']
        self.pd.set_index('DateTime', inplace=True)
    return None

def set_irradiance_df(self,df_irradiance:pd.DataFrame):
    
    assert 'DirectIrradiance' in df_irradiance.columns and 'DateTime' in df_irradiance.columns
    if not (df_irradiance.index.name == 'DateTime' and df_irradiance.index.format() == 'datetime64[ns]'):
        df_irradiance.set_index('DateTime', inplace=True)
        df_irradiance.index = pd.to_datetime(df_irradiance.index)


    # Ensure we only add values at indices already present in self.pd and df_irradiance
    common_indices = self.pd.index.intersection(df_irradiance.index)

    # Update self.pd with the values from df_irradiance at the common indices
    self.pd.loc[common_indices, 'DirectIrradiance'] = df_irradiance.loc[common_indices, 'DirectIrradiance']

    # Identify missing indices in df1 that are present in df2 and add them
    missing_indices = df_irradiance.index.difference(self.pd['DirectIrradiance'].index)
    missing_data = df_irradiance.loc[missing_indices]
    #print(missing_data)
    #print(self.pd)
    # Append the missing data to df1
    self.pd = pd.concat([self.pd,missing_data]).sort_index()

    # Set the previous data to nan
    missing_indices_2=self.pd.index.difference(df_irradiance.index)
    self.pd.loc[missing_indices_2, 'DirectIrradiance'] = None
    return None

def append_irradiance_df(self,df_irradiance:pd.DataFrame):
    assert 'DirectIrradiance' in df_irradiance.columns and 'DateTime' in df_irradiance.columns
    if not (df_irradiance.index.name == 'DateTime' and df_irradiance.index.format() == 'datetime64[ns]'):
        df_irradiance.set_index('DateTime', inplace=True)
        df_irradiance.index = pd.to_datetime(df_irradiance.index)

    if 'DirectIrradiance' not in self.pd.columns:
        self.pd['DirectIrradiance'] = df_irradiance['DirectIrradiance']
    else:
        self.pd['DirectIrradiance'] = pd.concat([self.pd['DirectIrradiance'], df_irradiance['DirectIrradiance']], axis=1, join="outer")
    if 'DateTime' not in self.pd.columns:
        self.pd['DateTime'] = df_irradiance['DateTime']
        self.pd.set_index('DateTime', inplace=True)
    return None

def set_belpex_df(self,df_belpex:pd.DataFrame):
    assert 'Belpex' in df_belpex.columns and 'DateTime' in df_belpex.columns
    if not (df_belpex.index.name == 'DateTime' and df_belpex.index.format() == 'datetime64[ns]'):
        df_belpex.set_index('DateTime', inplace=True)
        df_belpex.index = pd.to_datetime(df_belpex.index)

    self.pd['Belpex'] = df_belpex['Belpex']
    return None

def append_belpex_df(self,df_belpex:pd.DataFrame):
    assert 'Belpex' in df_belpex.columns and 'DateTime' in df_belpex.columns
    if not (df_belpex.index.name == 'DateTime' and df_belpex.index.format() == 'datetime64[ns]'):
        df_belpex.set_index('DateTime', inplace=True)
        df_belpex.index = pd.to_datetime(df_belpex.index)

    if 'Belpex' not in self.pd.columns:
        self.pd['Belpex'] = df_belpex['Belpex']
    else:
        self.pd['Belpex'] = pd.concat([self.pd['Belpex'], df_belpex['Belpex']], axis=1, join="outer")
    if 'DateTime' not in self.pd.columns:
        self.pd['DateTime'] = df_belpex['DateTime']
        self.pd.set_index('DateTime', inplace=True)
    return None

def set_irradiance_xlsx(self,file_path_Irradiance):
    # Add load data
    belpex_df = pd.read_excel(file_path_Irradiance)
    assert file_path_Irradiance.endswith('.xlsx'), 'The file must be an Excel file'
    # Assert that 'Load_kW' and 'DateTime' columns are present in the Excel file
    assert 'DateTime' in belpex_df.columns, "'DateTime' column not found in the Irradiance Excel file"
    assert 'Belpex' in belpex_df.columns, "'Belpex' column not found in the Irradiance Excel file"
    # Merge the DataFrame with the one read from excel
    self.pd = pd.concat(belpex_df, self.pd, join="outer") #TODO: check how to merge both
    return None

def set_load_xslx(self,file_path_Load):
    # Add load data
    belpex_df = pd.read_excel(file_path_Load)
    assert file_path_Load.endswith('.xlsx'), 'The file must be an Excel file'
    # Assert that 'Load_kW' and 'DateTime' columns are present in the Excel file
    assert 'DateTime' in belpex_df.columns, "'DateTime' column not found in the Irradiance Excel file"
    assert 'Belpex' in belpex_df.columns, "'Belpex' column not found in the Irradiance Excel file"
    # Merge the DataFrame with the one read from excel
    self.pd = pd.concat(belpex_df, self.pd, join="outer") #TODO: check how to merge both
    return None

def set_belpex_xlsx(self,file_path_BelpexFilter:str):
    # Add belpex data
    belpex_df = pd.read_excel(file_path_BelpexFilter)
    assert file_path_BelpexFilter.endswith('.xlsx'), 'The file must be an Excel file'
    # Assert that 'Load_kW' and 'DateTime' columns are present in the Excel file
    assert 'DateTime' in belpex_df.columns, "'DateTime' column not found in the Irradiance Excel file"
    assert 'Belpex' in belpex_df.columns, "'Belpex' column not found in the Irradiance Excel file"
    # Merge the DataFrame with the one read from excel
    self.pd = pd.concat(belpex_df, self.pd, join="outer") #TODO: check how to merge both
    return None

def set_pv_power_df(self,df_pv_power:pd.DataFrame):
    assert 'PV_Power_kW' in df_pv_power.columns and 'DateTime' in df_pv_power.columns
    if not (df_pv_power.index.name == 'DateTime' and df_pv_power.index.format() == 'datetime64[ns]'):
        df_pv_power.set_index('DateTime', inplace=True)
        df_pv_power.index = pd.to_datetime(df_pv_power.index)

    self.pd['PV_Power_kW'] = df_pv_power['PV_Power_kW']

    return None

def append_pv_power_df(self,df_pv_power:pd.DataFrame):
    assert 'PV_Power_kW' in df_pv_power.columns and 'DateTime' in df_pv_power.columns
    if not (df_pv_power.index.name == 'DateTime' and df_pv_power.index.format() == 'datetime64[ns]'):
        df_pv_power.set_index('DateTime', inplace=True)
        df_pv_power.index = pd.to_datetime(df_pv_power.index)

    if 'PV_Power_kW' not in self.pd.columns:
        self.pd['PV_Power_kW'] = df_pv_power['PV_Power_kW']
    else:
        self.pd['PV_Power_kW'] = pd.concat([self.pd['PV_Power_kW'], df_pv_power['PV_Power_kW']], axis=1, join="outer")
    if 'DateTime' not in self.pd.columns:
        self.pd['DateTime'] = df_pv_power['DateTime']
        self.pd.set_index('DateTime', inplace=True)
    return None

def set_pv_power_spp_df(self,set:str,peak_power:int):
    if set == 'SPP_2022':
        SPP=pd.read_csv('SPP_2022.csv')
        SPP['DateTime'] = pd.to_datetime(SPP['DateTime'])
        SPP.set_index('DateTime', inplace=True)
        self.pd['PV_Power_kW'] = SPP['PV_Power_kW']*peak_power #add independent of data
    elif set == 'SPP_2023':
        SPP=pd.read_csv('SPP_2023.csv')
        SPP['DateTime'] = pd.to_datetime(SPP['DateTime'])
        SPP.set_index('DateTime', inplace=True)
        self.pd['PV_Power_kW'] = SPP['PV_Power_kW']*peak_power  #add independent of data
    return None