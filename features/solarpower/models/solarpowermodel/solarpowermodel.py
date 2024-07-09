
from math import acos, asin, cos, pi, sin, tan
import math
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from features.solarpower.models.battery.battery import Battery
from features.solarpower.models.solarpanel.solarpanel import SolarPanel
from features.solarpower.models.inverter.inverter import Inverter
from torch import sgn

class SolarPowerModel():
    def __init__(self, solarpanel=None, inverter=None, battery=None,reference_id=None):
        if solarpanel is None:
            solarpanel = SolarPanel(solar_panel_type="Jinko")
        if inverter is None:
            inverter = Inverter(inverter_type="Sungrow_3")
        if battery is None:
            battery = Battery(battery_type="LG RESU 2.9")

        self.pd=pd.DataFrame()
        # Initialize the columns that will be used for the calculations
        self.pd['DateTime'] = None
        #Set a datetime index
        self.pd.set_index('DateTime', inplace=True)
        self.pd['Load_kW'] = None
        self.pd['DirectIrradiance'] = None    # [W]  
        self.pd['PV_Power_kW'] = None  # [kW]
        self.pd['GridFlow'] = None           # [kW], if neg, then subtracted from grid, if pos the added to the grid
        self.pd['GridFlow_Load'] = None
        self.pd['BatteryCharge'] = None       # [kW]
        self.pd['NettoProduction'] = None # Netto production is the difference between the PV generated power and the load
        self.pd['EVLoad'] = None # [kW]
        self.pd['PowerLoss'] = None # [kW]
        self.pd['BatteryFlow'] = None
        self.pd['DualTariff'] = None
        self.pd['DualTariff_Load'] = None
        self.pd['DynamicTariff'] = None
        self.pd['DynamicTariff_Load'] = None

        self.solarpanel=solarpanel
        self.T_STC=25
        self.inverter=inverter
        self.battery=battery

        self.tariff_dual_peak=0.1701
        self.tariff_dual_offpeak=0.146
        self.tariff_dual_fixed=0.0155
        self.tariff_dual_injection=0.03

        self.tariff_dynamic_A_injection=0.1
        self.tariff_dynamic_B_injection=-0.905
        self.tariff_dynamic_A_offtake=0.1
        self.tariff_dynamic_B_offtake=1.1

    # Imported methods
    from .utils._datacleaning import filter_data_by_date_interval
    from .utils._datacleaning import interpolate_columns
    from .utils._datacleaning import find_duplicate_indices
    from .utils._datacleaning import empty_column
    from .utils._datacleaning import update_column

    from .utils._pvpower import refresh_PV_Power_kW, update_PV_Power_kW
    from .utils._pvpower import PV_Power_kW_SPP

    #from .OLD._visualisations import plot_columns
    #from .OLD._visualisations import plot_dataframe
    #from .OLD._visualisations import plot_series
    
    from .utils._directirradiance import calculate_direct_irradiance
    from .utils._directirradiance import calculate_solar_angles

    from .utils._powerflows import refresh_power_flow
    from .utils._powerflows import update_power_flow
    from .utils._powerflows import nettoProduction

    from .utils._getters import get_dataset
    from .utils._getters import get_irradiance
    from .utils._getters import get_load
    from .utils._getters import get_direct_irradiance
    from .utils._getters import get_PV_Power_kW
    from .utils._getters import get_energy_TOT
    from .utils._getters import get_average_per_hour
    from .utils._getters import get_grid_power
    from .utils._getters import get_columns
    from .utils._getters import get_monthly_peaks
    from .utils._getters import get_total_injection_and_consumption
    from .utils._getters import get_average_per_minute_day
    from .utils._getters import get_total_cost

    from .utils._export import export_dataframe_to_excel

    from .utils._EVload import add_EV_load

    from .utils._tariffs import capacity_tariff
    from .utils._tariffs import refresh_dual_tariff, update_dual_tariff, refresh_dynamic_tariff, update_dynamic_tariff

    from .utils._setters import set_belpex_df
    from .utils._setters import set_belpex_xlsx
    from .utils._setters import set_irradiance_df
    from .utils._setters import set_irradiance_xlsx
    from .utils._setters import set_load_df
    from .utils._setters import set_load_xslx
    from .utils._setters import set_pv_power_df
    from .utils._setters import append_pv_power_df
    from .utils._setters import set_pv_power_spp_df
    from .utils._setters import append_belpex_df
    from .utils._setters import append_irradiance_df
    from .utils._setters import append_load_df

    from .utils._repository import from_snapshot
