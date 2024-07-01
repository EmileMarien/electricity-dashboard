from matplotlib import pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import time
from features.pricefetching.DataRetrieval import fetch_electricity_prices, add_belpex_to_firestore
from core.firestore_init import load_key, authenticate_to_firestore
from routes.menu import menu_with_redirect
st.set_page_config(page_title="Dashboard", page_icon="🌍")
from core.css import apply_custom_css
# Hide Streamlit's default menu and footer using custom CSS
apply_custom_css()
menu_with_redirect()
#st.sidebar.header("Dashboard")

# Dummy function to simulate live electricity meter data
@st.cache_data(ttl=60)
def get_meter_data():
    """Simulate fetching electricity meter data."""
    now = datetime.now(pytz.timezone('Europe/Berlin'))
    times = [now - timedelta(minutes=i) for i in range(60*24*7)]  # Simulate data for the past week
    meter1 = np.random.random(len(times)) * 100  # Simulated data for meter 1
    meter2 = np.random.random(len(times)) * 100  # Simulated data for meter 2
    meter3 = np.random.random(len(times)) * 100  # Simulated data for meter 3

    data = {
        'time': times,
        'Meter 1': meter1,
        'Meter 2': meter2,
        'Meter 3': meter3,
    }

    return pd.DataFrame(data)

# Fetch initial data
meter_data = get_meter_data()

# -----------------------------------------------------------------------------
# Section 1: Summary Statistics and Solar Panel Info
# -----------------------------------------------------------------------------

# Set the title that appears at the top of the page.
st.title(':electric_plug: Electricity Meter Dashboard')

# Number of installed solar panels
solar_panels_installed = 50  # Example number, replace with actual value

# Calculate the current peak electricity consumption
current_peak_consumption = meter_data['Meter 1'].max()

# Calculate the average consumption over the last 24 hours
last_24h = datetime.now(pytz.timezone('Europe/Berlin')) - timedelta(hours=24)
avg_last_24h = meter_data[meter_data['time'] >= last_24h]['Meter 1'].mean()

# Calculate the total consumption during the last week
total_last_week = meter_data['Meter 1'].sum()

# Display the metrics
st.header('Summary Statistics')
st.write(f'**Installed Solar Panels:** {solar_panels_installed}')
st.write(f'**Current Peak Electricity Consumption:** {current_peak_consumption:.2f} kWh')
st.write(f'**Average Consumption (Last 24h):** {avg_last_24h:.2f} kWh')
st.write(f'**Total Consumption (Last Week):** {total_last_week:.2f} kWh')

# -----------------------------------------------------------------------------
# Section 2: Chart and Controls
# -----------------------------------------------------------------------------

st.header('Electricity Meter Data')

# Create columns for chart and controls
col1, col2 = st.columns([3, 1])

with col2:
    # Dropdown to select meter
    meter = st.selectbox(
        'Select Meter',
        ['Meter 1', 'Meter 2', 'Meter 3']
    )

    # Date and time pickers for start and end date
    start_date = st.date_input('Start date', value=(datetime.now(pytz.timezone('Europe/Berlin')) - timedelta(days=7)).date())
    end_date = st.date_input('End date', value=datetime.now(pytz.timezone('Europe/Berlin')).date())

    start_time = st.time_input('Start time', value=datetime.now(pytz.timezone('Europe/Berlin')).time())
    end_time = st.time_input('End time', value=datetime.now(pytz.timezone('Europe/Berlin')).time())

    # Combine date and time
    start_datetime = datetime.combine(start_date, start_time).replace(tzinfo=pytz.timezone('Europe/Berlin'))
    end_datetime = datetime.combine(end_date, end_time).replace(tzinfo=pytz.timezone('Europe/Berlin'))

    # Interval for data points
    interval = st.selectbox('Select interval (minutes)', [1, 5, 10, 15, 30, 60])

# Filter data based on selected date and time range
filtered_data = meter_data[(meter_data['time'] >= start_datetime) & (meter_data['time'] <= end_datetime)]
filtered_data = filtered_data.set_index('time').resample(f'{interval}T').mean().reset_index()

# Display line chart
with col1:
    chart_container = st.empty()

# -----------------------------------------------------------------------------
# Section 3: Display last received data values
# -----------------------------------------------------------------------------
def plot_consumption(df):
    """
    Runs a Streamlit app that allows visualization of hourly energy data.
    
    Parameters:
    df (pd.DataFrame): A DataFrame with datetime index, hourly consumption values,
                       hourly prices, and hourly costs.
    """
    st.title('Energy Data Visualization')

    st.write("""
    This app allows you to visualize hourly energy consumption, prices, and costs.
    Use the checkboxes below to toggle the visibility of each dataset.
    """)

    # Sidebar for toggling datasets
    show_consumption = st.sidebar.checkbox('Show Consumption', value=True)
    show_price = st.sidebar.checkbox('Show Price', value=True)
    show_cost = st.sidebar.checkbox('Show Cost', value=True)

    # Plotting
    st.subheader('Hourly Data')

    fig, ax = plt.subplots()

    if show_consumption:
        ax.plot(df.index, df['consumption'], label='Consumption', color='blue')
    if show_price:
        ax.plot(df.index, df['price'], label='Price', color='green')
    if show_cost:
        ax.plot(df.index, df['cost'], label='Cost', color='red')

    ax.set_xlabel('Time')
    ax.set_ylabel('Values')
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

# Sample DataFrame creation for demonstration purposes
# This would normally be loaded from a data source
date_rng = pd.date_range(start='2023-01-01', end='2023-01-02', freq='H')
df = pd.DataFrame(date_rng, columns=['date'])
df = df.set_index('date')
df['consumption'] = np.random.randint(0, 100, size=(len(date_rng)))
df['price'] = np.random.uniform(0, 10, size=(len(date_rng)))
df['cost'] = df['consumption'] * df['price']
plot_consumption(df)
# -----------------------------------------------------------------------------
# Section 4: Display last received data values
# -----------------------------------------------------------------------------

st.header('Last Received Data Values')
# Containers for dynamic content
metrics_container = st.empty()

# Function to update data every minute
def update_data():
    meter_data = get_meter_data()
    filtered_data = meter_data[(meter_data['time'] >= start_datetime) & (meter_data['time'] <= end_datetime)]
    filtered_data = filtered_data.set_index('time').resample(f'{interval}T').mean().reset_index()

    # Update line chart
    chart_container.line_chart(filtered_data[['time', meter]].set_index('time'))

    # Display the last 5 data values received (excluding specified values)
    last_five_values = filtered_data.tail(5)
    last_five_values = last_five_values[~last_five_values[meter].isin([10008, 10009, 10010, 10011, 10012])]

    # Set 'time' as index to display it as the first row
    last_five_values.set_index('time', inplace=True)

    # Clear previous content of metrics_container
    metrics_container.empty()

    with metrics_container:
        st.subheader(f'Last 5 Data Values for {meter} (From {start_datetime} to {end_datetime})')
        st.write(last_five_values)

# Initial call to display data
update_data()

st.header("Fetching BELPEX prices")
data=fetch_electricity_prices()
#Show the data in a table
st.write(data)
# Authenticate to Firestore
db = authenticate_to_firestore(load_key())
st.write(add_belpex_to_firestore(belpex=data,db=db))

# -----------------------------------------------------------------------------
# Refresh data every minute
while True:
    time.sleep(60)
    update_data()




# Extra Guidance:
# 1. You could add an option to download the displayed data as a CSV file using `st.download_button`.
# 2. Include additional statistical metrics or visualizations as needed.
# 3. Implement a notification system for specific conditions (e.g., if the meter reading exceeds a certain threshold).
# 4. Allow comparison between multiple meters by selecting multiple meters and displaying them on the same graph.
# 5. Integrate with a real database or an API for actual data instead of the dummy function.
