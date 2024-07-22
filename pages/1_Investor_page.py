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
if st.button("Load model"):
    st.write(st.session_state.controller.load_model())     #todo: why does this not update the new values set by updtate_belpex and update_SLP? controller is not updated in the state

if st.button("update model"):
    st.write(st.session_state.controller.update_model())
    
if st.button("update belpex"):
    st.write(st.session_state.controller.update_belpex())

st.header("Model components")
st.write("Your current home system contains following equipment:")
st.write("Inverter: ", st.session_state.controller.get_invertername()) #TODO: check if possible to let pop up the parameters if this is clicked
st.write("Battery: ", st.session_state.controller.get_batteryname())
st.write("Solarpanel: ", st.session_state.controller.get_solarpanelname())
st.write("Peak power: ", st.session_state.controller.get_peak_power())

if st.button("Edit model"):
    with st.form("Edit model"):
        new_inverter = st.selectbox('New inverter: ',['Sungrow_3','Fronius_3','Sungrow_5'],key='new_inverter')
        new_battery = st.selectbox('New battery: ',['LG RESU 2.9','LG RESU 5.9','LG RESU Prime 9.6'],key='new_battery')
        new_solarpanel = st.selectbox('New solarpanel: ',['Canadian','Jinko'],key='new_solarpanel')
        peak_production_power = st.number_input('Peak production power (kW)',min_value=0.0, max_value=100.0, value=5.0, step=0.1,key='peak_production_power')
        yearly_consumption_energy= st.number_input('Yearly consumption energy (kWh)',min_value=0.0, max_value=100.0, value=2.0, step=0.1,key='yearly_consumption_energy')
        new_solarpanel_count= st.number_input('Amount of solar panels: ',min_value=0, max_value=100, value=10, step=1,key='new_solarpanel_count')
        submitted = st.form_submit_button('Update model', on_click=st.session_state.controller.change_model(inverter_type=st.session_state.new_inverter,battery_type=st.session_state.new_battery,peak_production_power=st.session_state.peak_production_power,yearly_consumption_energy=st.session_state.yearly_consumption_energy,solarpanel_type=st.session_state.new_solarpanel))
        if submitted:
            st.write("Model updated")

#status = st.selectbox("Status", ["Active", "Inactive"])


st.header("Recent readings")
st.write(st.session_state.controller.get_SLP_belpex().tail(15))

st.header("Performance metrics")
st.write("Total production: ", st.session_state.controller.get_total_production())
#st.write("Total consumption: ", st.session_state.controller.get_total_consumption())
st.write("Total savings: ", st.session_state.controller.get_total_savings())