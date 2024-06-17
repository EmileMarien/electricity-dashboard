import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def fetch_electricity_prices():
    """
    Fetches the electricity prices from the Elexys website and returns as a DataFrame.
    
    Returns:
        pd.DataFrame: A DataFrame containing the electricity prices with timestamps.
    """
    # URL of the page to scrape
    url= 'https://my.elexys.be/MarketInformation/SpotBelpex.aspx'
    
    # Send a GET request to fetch the HTML content
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page content: {response.status_code}")
    
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table with the data
    table = soup.find('table', {'class': 'table'})
    
    # Initialize lists to store the dates and prices
    dates = []
    prices = []
    
    # Loop through the table rows and extract data
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cols = row.find_all('td')
        date_str = cols[0].text.strip()
        price_str = cols[1].text.strip().replace('€', '').replace(',', '.')
        
        # Convert strings to appropriate data types
        date = datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S')
        price = float(price_str)
        
        dates.append(date)
        prices.append(price)
    
    # Create a DataFrame with the scraped data
    df = pd.DataFrame({'Date': dates, 'Price (Euro)': prices})
    df.set_index('Date', inplace=True)
    
    return df

# URL of the page to scrape
url = 

# Fetch the electricity prices and store in a DataFrame
df = fetch_electricity_prices(url)

# Display the DataFrame
print(df)
