import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fetch_electricity_prices_xlsx():
    """
    Fetches the electricity prices from the xlsx file and returns as a DataFrame.

    Args:
        file_path (str): The path to the xlsx file.

    Returns:
        pd.DataFrame: A DataFrame containing the electricity prices with timestamps.
    """
    file_path = 'data/Belpex.xlsx'
    assert file_path.endswith('.xlsx'), 'The file must be an Excel file'
    belpex_df = pd.read_excel(file_path)
    # Assert that 'Load_kW' and 'DateTime' columns are present in the Excel file
    assert 'DateTime' in belpex_df.columns, "'DateTime' column not found in the Irradiance Excel file"
    assert 'Belpex' in belpex_df.columns, "'Belpex' column not found in the Irradiance Excel file"
    # Convert 'DateTime' column to datetime
    # Convert DateTime column to datetime, assuming the original timezone is known, for example, 'Europe/Brussels'
    belpex_df['DateTime'] = pd.to_datetime(belpex_df['DateTime'], dayfirst=True)  # Adjust `dayfirst` based on the date format
    belpex_df['DateTime'] = belpex_df['DateTime'].dt.tz_localize('Europe/Brussels',ambiguous=True).dt.tz_convert('UTC')
    #dd
    # Set DateTime as index
    belpex_df.set_index('DateTime', inplace=True)
    return belpex_df

def fetch_electricity_prices():
    """
    Fetches the electricity prices from the Elexys website and returns as a DataFrame.
    
    Returns:
        pd.DataFrame: A DataFrame containing the electricity prices with timestamps.
    """
    # URL of the page to scrape
    url = 'https://my.elexys.be/MarketInformation/SpotBelpex.aspx'
    
    # Send a GET request to fetch the HTML content
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page content: {response.status_code}")
    
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table with the data
    table = soup.find('table', {'id': 'contentPlaceHolder_belpexFilterGrid_DXMainTable'})
    
    # Debugging: Print the table to ensure it is found
    #print("Table found:", table is not None)
    #print("HTML content:", soup.prettify())
    
    # Return if table is not found
    #if table is None:
        #raise Exception("Failed to find the table in the HTML content")

    # Initialize lists to store the dates and prices
    datetimes = []
    prices = []
    
    rows = table.find_all('tr', class_='dxgvDataRow_Office2010Blue')
    if rows is None or len(rows) == 0:
        return "No data rows found in the table"
    
    for row in rows:
        cols = row.find_all('td', class_='dxgv')
        if len(cols) == 2:
            datetimes.append(cols[0].get_text(strip=True))
            prices.append(cols[1].get_text(strip=True))

    # Create a DataFrame
    df = pd.DataFrame({
        'DateTime': datetimes,
        'Belpex': prices
    })


    # Function to convert Belpex column to numerical data
    def convert_to_numeric(value):
        return float(value.replace('€', '').replace(',', '.').strip())

    # Apply the function to the Belpex column
    df['Belpex'] = df['Belpex'].apply(convert_to_numeric)
    
    # Convert DateTime column to datetime, assuming the original timezone is known, for example, 'Europe/Brussels'
    df['DateTime'] = pd.to_datetime(df['DateTime'], dayfirst=True)  # Adjust `dayfirst` based on the date format
    df['DateTime'] = df['DateTime'].dt.tz_localize('Europe/Brussels',ambiguous='infer').dt.tz_convert('UTC')

    # Set DateTime as index
    df.set_index('DateTime', inplace=True)

    return df



