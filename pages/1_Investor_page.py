import streamlit as st
import time
import numpy as np
from css import apply_custom_css
from menu import menu_with_redirect
st.set_page_config(page_title="Plotting Demo", page_icon="📈")
# Hide Streamlit's default menu and footer using custom CSS
menu_with_redirect()
apply_custom_css()

st.markdown("# Portfolio Simulation")
st.sidebar.header("Portfolio Simulation")
st.write(
    """An example of future evolution of your portfolio value"""
)

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()
last_rows = np.random.randn(1, 1)
chart = st.line_chart(last_rows)

for i in range(1, 101):
    new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
    status_text.text("%i%% Complete" % i)
    chart.add_rows(new_rows)
    progress_bar.progress(i)
    last_rows = new_rows
    time.sleep(0.05)

progress_bar.empty()

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")