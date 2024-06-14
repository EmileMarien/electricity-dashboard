from datetime import datetime, timedelta
import random
from matplotlib import pyplot as plt
import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from google.cloud import firestore
import json
# Hide Streamlit's default menu and footer using custom CSS
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
def load_key():
    try:
        key_dict = json.loads(st.secrets["textkey"])
        return key_dict
    except KeyError:
        st.error("Service account key not found in Streamlit secrets.")
        return None

def authenticate_to_firestore(key_dict):
    try:
        creds = service_account.Credentials.from_service_account_info(key_dict)
        db = firestore.Client(credentials=creds, project="electricitydashboard")
        st.success("Successfully authenticated to Firestore.")
        return db
    except Exception as e:
        st.error(f"Failed to authenticate to Firestore: {e}")
        return None

def fetch_document(db):
    try:
        doc_ref = db.collection("meters").document("meter_test")
        doc = doc_ref.get()
        if doc.exists:
            st.write("Document data:", doc.to_dict())
        else:
            st.write("No such document!")
    except Exception as e:
        st.error(f"Failed to fetch document: {e}")


def add_meter(db, meter_id, location, status):
    try:
        meter_data = {
            "meter_id": meter_id,
            "location": location,
            "status": status
        }
        db.collection("meters").document(meter_id).set(meter_data)
        st.success(f"Meter {meter_id} added successfully!")
    except Exception as e:
        st.error(f"Failed to add meter: {e}")

def show_meters(db):
    st.subheader("Existing Meters")
    meters_ref = db.collection('meters')
    meters = meters_ref.get()
    
    # Prepare data for the table
    table_data = []  # Adding headers
    for meter in meters:
        meter_data = meter.to_dict()
        meter_name = meter_data.get('name', '')
        location = meter_data.get('location', '')
        status = meter_data.get('status', '')
        meter_id = meter_data.get('meter_id', '')
        
        table_data.append([meter_id, meter_name, location, status])
    
    # Display the table
    if len(table_data) > 1:  # Check if there are meters (excluding headers)
        table_data_df=pd.DataFrame(table_data, columns=['Meter ID', 'Meter Name', 'Location', 'Status'])
        st.table(table_data_df)
    else:
        st.write("No meters found.")

# Function to fetch consumption data from Firestore and return as DataFrame
def get_consumption_data(db,meter_id):
    # Initialize an empty list to collect data points
    data_points = []

    # Fetch consumption data from Firestore for the specified meter_id
    meter_ref = db.collection('meters').document(meter_id)
    consumption_data = meter_ref.get().to_dict().get('consumptiondata', [])

    # Iterate over each data point and extract timestamp and reading
    for data_point in consumption_data:
        timestamp = data_point['timestamp']
        reading = data_point['reading']
        data_points.append((timestamp, reading))

    # Convert data_points to pandas DataFrame
    if data_points:
        df = pd.DataFrame(data_points, columns=['timestamp', 'reading'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])  # Convert timestamp to datetime object
        df.set_index('timestamp', inplace=True)  # Set timestamp as index
        return df
    else:
        return pd.DataFrame(columns=['timestamp', 'reading'])  # Return empty DataFrame if no data


# Function to plot consumption data
def plot_consumption_data(consumption_data, meter_id):
    timestamps = []
    readings = []

    for doc in consumption_data:
        data = doc.to_dict()
        timestamps.append(data['timestamp'])
        readings.append(data['reading'])

    # Convert timestamps to pandas datetime for easier plotting
    df = pd.DataFrame({'timestamp': timestamps, 'reading': readings})
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    # Resample data to quarterly frequency (sum of readings for each quarter)
    quarterly_data = df['reading'].resample('Q').sum()

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(quarterly_data.index, quarterly_data.values, marker='o', linestyle='-')
    plt.title(f"Quarterly Electricity Consumption for Meter {meter_id}")
    plt.xlabel("Quarter")
    plt.ylabel("Electricity Consumption")
    plt.grid(True)
    plt.xticks(rotation=45)
    st.pyplot()

def show_meterdata(db):
    st.subheader("Meter Data")

    meters_ref = db.collection('meters')
    meter_list = [meter.id for meter in meters_ref.get()]
    selected_meter = st.selectbox("Select Meter ID", meter_list)
    
    # Fetch consumption data and plot
    if selected_meter:
        consumption_data = get_consumption_data(db,selected_meter)
        if consumption_data:
            plot_consumption_data(db,consumption_data, selected_meter)
        else:
            st.write(f"No consumption data found for Meter {selected_meter}.")

# Function to add multiple datapoints of consumption data for a specified meter ID
def add_consumption_data(meter_id, num_datapoints):
    # Get current timestamp
    current_time = datetime.now()

    # Generate and add specified number of datapoints of consumption data
    for i in range(num_datapoints):
        # Simulate random reading (replace with actual data generation logic)
        reading = random.randint(100, 1000)
        
        # Generate timestamp for each datapoint (15 minutes interval)
        timestamp = current_time - timedelta(minutes=15 * i)

        # Create data object
        data = {
            'timestamp': timestamp,
            'reading': reading
        }

        # Add data to Firestore under 'consumptiondata' array for the specified meter ID
        meter_ref = db.collection('meters').document(meter_id)
        meter_ref.update({
            'consumptiondata': firestore.ArrayUnion([data])
        })
    
    return f"Added {num_datapoints} datapoints of consumption data for Meter {meter_id}"


key_dict = load_key()
if key_dict:
    db = authenticate_to_firestore(key_dict)

if db:
    add_consumption_data("meter_test", 10)
    st.header("Fetch a Document")
    st.write("Click the button below to fetch a document from Firestore.")
    if st.button("Fetch Document"):
        fetch_document(db)
    st.header("Meter data")
    show_meterdata(db)
    st.header("Existing Meters")
    show_meters(db)
    st.header("Add a Meter")
    with st.form("add_meter_form"):
        meter_id = st.text_input("Meter ID")
        location = st.text_input("Location")
        status = st.selectbox("Status", ["Active", "Inactive"])
        submitted = st.form_submit_button("Add Meter")

        if submitted:
            if meter_id and location and status:
                add_meter(db, meter_id, location, status)
            else:
                st.error("Please fill in all fields")