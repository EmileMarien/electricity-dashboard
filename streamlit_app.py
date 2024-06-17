import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import time
import streamlit as st

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Electricity Meter Dashboard',
    page_icon=':electric_plug:',  # This is an emoji shortcode. Could be a URL too.
)

# Hide Streamlit's default menu and footer using custom CSS
#.stApp {
#    max-width: 800px; /* Adjust maximum width of the app */
#    margin: 0 auto; /* Center align content */
#    padding: 20px; /* Add padding for content */
#    text-align: center; /* Center align text */
#}
hide_streamlit_style ="""
<style>
    body {
        background-color: #C3E6CB; /* Light green background color */
        font-family: Arial, sans-serif; /* Adjust font family as needed */
    }

.stApp h1 {
    font-size: 3em; /* Adjust title font size */
    margin-bottom: 10px; /* Add space below title */
}

.stApp p {
    font-size: 1.5em; /* Adjust subtitle font size */
    margin-bottom: 20px; /* Add space below subtitle */
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
#footer {visibility: hidden;}
div[data-testid="stToolbar"] {visibility: hidden;}
div[data-testid="stDecoration"] {visibility: hidden;}
div[data-testid="stStatusWidget"] {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.image("data/logo_lama.png", width=150, use_column_width='always', caption='Lama Icon')
st.write("# Lama energies")
st.write("laten we die daken nekeer volleggen")

st.sidebar.success("Select a demo above.")
