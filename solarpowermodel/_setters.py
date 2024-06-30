

import pandas as pd

#TODO: how to merge? don't forget to set datetimeindex

def set_load_df(self,df_load:pd.Dataframe):
    
    assert 'Load_kW' in df_load.columns and 'DateTime' in df_load.columns
    if not (df_load.index.name == 'DateTime' and df_load.index.format() == 'datetime64[ns]'):
        df_load.set_index('DateTime', inplace=True)
        df_load.index = pd.to_datetime(df_load.index)

    if self.pd is not None:
        self.pd = pd.concat([self.pd, df_load], axis=1, join="inner")
    else:
        self.pd = df_load
    return None

def set_irradiance_df(self,df_irradiance:pd.Dataframe):
    
    assert 'DirectIrradiance' in df_irradiance.columns and 'DateTime' in df_irradiance.columns
    if not (df_irradiance.index.name == 'DateTime' and df_irradiance.index.format() == 'datetime64[ns]'):
        df_irradiance.set_index('DateTime', inplace=True)
        df_irradiance.index = pd.to_datetime(df_irradiance.index)

    if self.pd is not None:
        self.pd = pd.concat([self.pd, df_irradiance], axis=1, join="inner")
    else:
        self.pd = df_irradiance
    return None

def set_belpex_df():
    return None

def set_belpex_xlsx():
    return None

def set_irradiance_xlsx():
    return None

def set_load_xslx():
    return None

def set_belpex_df(self,file_path_BelpexFilter:str):
    # Add belpex data
    belpex_df = pd.read_excel(file_path_BelpexFilter)
    assert file_path_BelpexFilter.endswith('.xlsx'), 'The file must be an Excel file'
    # Assert that 'Load_kW' and 'DateTime' columns are present in the Excel file
    assert 'DateTime' in belpex_df.columns, "'DateTime' column not found in the Irradiance Excel file"
    # Merge the DataFrame with the one read from excel
    self.pd = pd.merge(belpex_df, self.pd, on='DateTime', how='right') #TODO: check how to merge both
    return None