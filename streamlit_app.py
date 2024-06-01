import streamlit as st
import pandas as pd
import math
from pathlib import Path
import time
import numpy as np
from datetime import datetime, timedelta
import pytz
# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='GDP Dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
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
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: GDP Dashboard

View the electricity meter data
'''

# Add some spacing
''
''



st.header('GDP over time', divider='gray')
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
#footer {visibility: hidden;}
div[data-testid="stToolbar"] {visibility: hidden;}
div[data-testid="stDecoration"] {visibility: hidden;}
div[data-testid="stStatusWidget"] {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
''
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

# Containers for dynamic content
chart_container = st.empty()
metrics_container = st.empty()

# Function to update data every minute
def update_data():
    meter_data = get_meter_data()
    filtered_data = meter_data[(meter_data['time'] >= start_datetime) & (meter_data['time'] <= end_datetime)]
    filtered_data = filtered_data.set_index('time').resample(f'{interval}T').mean().reset_index()

    # Update line chart
    chart_container.line_chart(filtered_data[['time', meter]].set_index('time'))

    # Calculate statistical metrics
    avg_value = filtered_data[meter].mean()
    min_value = filtered_data[meter].min()
    max_value = filtered_data[meter].max()

    # Display statistical metrics
    with metrics_container:
        st.subheader(f'Statistical Metrics for {meter} (From {start_datetime} to {end_datetime})')
        st.write(f'**Average:** {avg_value:.2f}')
        st.write(f'**Minimum:** {min_value:.2f}')
        st.write(f'**Maximum:** {max_value:.2f}')

# Initial call to display data
update_data()

# Refresh data every minute
while True:
    time.sleep(60)
    update_data()

