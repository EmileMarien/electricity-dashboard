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
    url = 'https://my.elexys.be/MarketInformation/SpotBelpex.aspx'
    
    # Send a GET request to fetch the HTML content
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page content: {response.status_code}")
    
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table with the data
    table = soup.find('table', {'class': 'table'})
    
    # Debugging: Print the table to ensure it is found
    print("Table found:", table is not None)
    print("HTML content:", soup.prettify())
    
    # Return if table is not found
    if table is None:
        raise Exception("Failed to find the table in the HTML content")

    # Initialize lists to store the dates and prices
    dates = []
    prices = []
    
    # Loop through the table rows and extract data
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cols = row.find_all('td')
        if len(cols) < 2:
            continue  # Skip rows that do not have enough columns
        
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

# Example usage
if __name__ == "__main__":
    df = fetch_electricity_prices
