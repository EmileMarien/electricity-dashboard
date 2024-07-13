import pandas as pd
from features.solarpower.controllers.controller_solarpower import ControllerSolarPower
import streamlit as st
import time
import numpy as np
from core.css import apply_custom_css
from routes.menu import menu_with_redirect
st.set_page_config(page_title="Plotting Demo", page_icon="📈")
# Hide Streamlit's default menu and footer using custom CSS
menu_with_redirect()
apply_custom_css()

st.markdown("# Model overview")
st.sidebar.header("Model overview")


#progress_bar = st.sidebar.progress(0)
#status_text = st.sidebar.empty()
#last_rows = np.random.randn(1, 1)
#chart = st.line_chart(last_rows)

#for i in range(1, 101):
#    new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
#    status_text.text("%i%% Complete" % i)
#    chart.add_rows(new_rows)
#    progress_bar.progress(i)
#    last_rows = new_rows
#    time.sleep(0.05)

#progress_bar.empty()



# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.








# check if controller in session state
if "controller" not in st.session_state:
    st.session_state.controller = ControllerSolarPower()



# only upload if button is clicked
#if st.button("Upload model"):
#    st.write(st.session_state.controller.upload_model())     #todo: why does this not update the new values set by updtate_belpex and update_SLP? controller is not updated in the state

if st.button("update model"):
    st.write(st.session_state.controller.update_model())

st.header("Model components")
st.write("Your current home system contains following equipment:")
st.write("Inverter: ", st.session_state.controller.get_invertername()) #TODO: check if possible to let pop up the parameters if this is clicked
st.write("Battery: ", st.session_state.controller.get_batteryname())
st.write("Solarpanel: ", st.session_state.controller.get_solarpanelname())
if st.button("Edit model"):
    with st.form("Edit model"):
        new_inverter = st.selectbox('New inverter: ',['Sungrow_3','Fronius_3','Sungrow_5'])
        new_battery = st.selectbox('New battery: ',['LG RESU 2.9','LG RESU 5.9','LG RESU Prime 9.6'])
        #status = st.selectbox("Status", ["Active", "Inactive"])
        submitted = st.form_submit_button("Update model")

        if submitted:
            st.session_state.controller.change_model(inverter_type=new_inverter,battery_type=new_battery)
        else:
            st.error("Please fill in all fields")


st.header("Recent readings")
st.write(st.session_state.controller.get_SLP_belpex().tail(15))

#Display the last 15 gridflow and load values
st.write(st.session_state.controller.get_gridflow().tail(15))