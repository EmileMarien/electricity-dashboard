

def SLP_xls_to_pd(file_path: str) -> pd.DataFrame:
    """
    This function reads the SLP data from an Excel file and returns a DataFrame.

    Args:
    file_path (str): The path to the Excel file.

    Returns:
    pd.DataFrame: The DataFrame containing the SLP data.
    """
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Ensure the DataFrame has the correct columns
    expected_columns = ['DateTime', 'Load_kW']
    if not all(col in df.columns for col in expected_columns):
        raise Exception(f"Columns in Excel file do not match expected columns: {expected_columns}")

    # Ensure the DateTime column is of type datetime
    if df['DateTime'].dtype != 'datetime64[ns]':
        raise Exception("DateTime column is not of type datetime")

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
    df = pd.read_excel(file_path)

    # Ensure the DataFrame has the correct columns
    expected_columns = ['DateTime', 'PV_Power_kW']
    if not all(col in df.columns for col in expected_columns):
        raise Exception(f"Columns in Excel file do not match expected columns: {expected_columns}")

    # Ensure the DateTime column is of type datetime
    if df['DateTime'].dtype != 'datetime64[ns]':
        raise Exception("DateTime column is not of type datetime")

    # Set the DateTime column as the index
    df.set_index('DateTime', inplace=True)

    return df   