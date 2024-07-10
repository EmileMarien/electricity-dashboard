from typing import List
import pandas as pd

def SLP_xls_to_pd(file_path: str) -> pd.DataFrame:
    """
    This function reads the SLP data from an Excel file and returns a DataFrame.
    """
    # Read the Excel file
    df = pd.read_excel(file_path,sheet_name='ENU_UTC')
    df['UTC'] = pd.to_datetime(df['UTC'])

    # Ensure the DataFrame has the correct columns
    expected_columns = ['UTC', 'EN']
    if not all(col in df.columns for col in expected_columns):
        raise Exception(f"Columns in Excel file do not match expected columns: {expected_columns}")

    # Ensure the DateTime column is of type datetime
    if df['UTC'].dtype != 'datetime64[ns]':
        raise Exception("DateTime column is not of type datetime")
    df=df[['UTC','EN']]
    df.rename(columns={'UTC':'DateTime','EN':'Load_SLP_kW'},inplace=True)
    # Set the DateTime column as the index
    df.set_index('DateTime', inplace=True)

    return df

def SPP_xls_to_pd(file_path: str) -> pd.DataFrame:
    """
    This function reads the SPP data from an Excel file and returns a DataFrame.

    Args:
    file_path (str): The path to the Excel file.

    Returns:
    pd.DataFrame: The DataFrame containing the SPP data.
    """
    # Read the Excel file
    df = pd.read_excel(file_path,sheet_name='Ex-ante 2022 (IP8)')
    df['UTC'] = pd.to_datetime(df['UTC'])

    # Ensure the DataFrame has the correct columns
    expected_columns = ['UTC', '5414488001704']
    if not all(col in df.columns for col in expected_columns):
        raise Exception(f"Columns in Excel file do not match expected columns: {expected_columns}")

    # Ensure the DateTime column is of type datetime
    if df['UTC'].dtype != 'datetime64[ns]':
        raise Exception("DateTime column is not of type datetime")
    df=df[['UTC','5414488001704']]
    df.rename(columns={'UTC':'DateTime','5414488001704':'PV_Power_SPP_kW'},inplace=True)
    # Set the DateTime column as the index
    df.set_index('DateTime', inplace=True)

    return df   