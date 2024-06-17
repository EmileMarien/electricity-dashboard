import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from google.cloud import firestore

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
        'Price': prices
    })
    
    return df


def add_belpex_to_firestore(belpex:pd.DataFrame, db:firestore.Client):
    """
    Adds the BELPEX prices to Firestore for the specified meter_id.

    Args:
        belpex (pd.DataFrame): DataFrame containing BELPEX prices.
        meter_id (str): The ID of the meter to add the prices to.
        db: Firestore client instance.

    Returns:
        str: A message indicating the number of data points added.
    """

    #latest_timestamp= get_latest_belpex_timestamp_from_firestore(db)
    data_to_add = []

    for index, row in belpex.iterrows():
        timestamp_str = row['DateTime']
        price_str = row['Price']

        # Parse timestamp (adjust according to your specific datetime format)
        timestamp = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M:%S')

        # Check if timestamp is after the latest timestamp in Firestore
        #if timestamp > latest_timestamp:
            # Prepare data object
        data = {
            'timestamp': timestamp,
            'value': float(price_str.replace(',', '.').strip().replace('€', ''))  # Assuming price needs to be stored as a float
        }
        data_to_add.append(data)

    # Update Firestore with new datapoints
    if data_to_add:
        prices_ref = db.collection('prices').document('belpex')
        prices_ref.update({
            'datapoints': firestore.ArrayUnion(data_to_add)
        })

    return f"Added {len(data_to_add)} new datapoints to Firestore under 'prices/belpex'"

"""
def get_latest_belpex_timestamp_from_firestore(db):
    prices_ref = db.collection('prices').document('belpex')
    doc = prices_ref.get()

    if doc.exists:
        data = doc.to_dict()
        datapoints = data.get('datapoints', [])

        if datapoints:
            # Sort datapoints by timestamp in descending order to get the latest
            datapoints_sorted = sorted(datapoints, key=lambda x: x['timestamp'], reverse=True)
            return datapoints_sorted[0]['timestamp']
        else:
            # Return a default timestamp if no datapoints exist
            return datetime.min
    else:
        # Handle case where document 'belpex' does not exist
        return datetime.min
"""

