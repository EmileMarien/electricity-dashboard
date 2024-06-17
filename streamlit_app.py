import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import time
import streamlit as st
from css import apply_custom_css
# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Electricity Meter Dashboard',
    page_icon=':electric_plug:',  # This is an emoji shortcode. Could be a URL too.
)

# Hide Streamlit's default menu and footer using custom CSS
apply_custom_css()

col1, col2, col3 = st.beta_columns([1,6,1])
with col1:
    st.write("")
with col2:
    st.image("data/logo_lama.png", use_column_width='always') # caption='Lama Icon'
with col3:
    st.write("")
st.write("# Lama energies")
st.write("laten we die daken nekeer volleggen")


st.sidebar.success("Select a demo above.")
