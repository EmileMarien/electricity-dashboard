
from math import acos, asin, cos, pi, sin, tan
import math
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from elecmodel.models.battery.battery import Battery
from elecmodel.models.solarpanel.solarpanel import SolarPanel
from elecmodel.models.inverter.inverter import Inverter
from torch import sgn

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot

class SolarPowerModel():
    def __init__(self, solarpanel=None, inverter=None, battery=None,reference_id=None, dataframe: pd.DataFrame = pd.DataFrame()):
        if solarpanel is None:
            self.solarpanel = SolarPanel(solar_panel_type="Jinko")
        else:
            self.solarpanel = solarpanel
        if inverter is None:
            self.inverter = Inverter(inverter_type="Sungrow_3")
        else:
            self.inverter = inverter
        if battery is None:
            self.battery = Battery(battery_type="LG RESU 2.9")
        else:
            self.battery = battery

        self.yearly_consumption_energy = 1.0
        # Initialize the dataframe
        if dataframe.empty:
            self.pd=dataframe
            # Initialize the columns that will be used for the calculations

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
            self.pd['Belpex'] = None
            self.pd['T_RV_degC'] = None
            #Set a datetime index with name 'DateTime'
            self.pd.index.name = 'DateTime'
            self.pd.index = pd.to_datetime(self.pd.index)
        else:
            #check if datetimeformat
            if 'DateTime' in dataframe.columns:
                assert dataframe['DateTime'].dtype == 'datetime64[ns]', "DateTime column must be of type datetime64[ns]"
                dataframe.set_index('DateTime', inplace=True)
            else:
                assert dataframe.index.dtype == 'datetime64[ns, UTC]', f"DateTime index: {dataframe.index.dtype}"


            assert 'Load_kW' in dataframe.columns, "DataFrame must have a 'Load_kW' column"
            assert 'DirectIrradiance' in dataframe.columns, "DataFrame must have a 'DirectIrradiance' column"
            assert 'PV_Power_kW' in dataframe.columns, "DataFrame must have a 'PV_Power_kW' column"
            assert 'GridFlow' in dataframe.columns, "DataFrame must have a 'GridFlow' column"
            assert 'GridFlow_Load' in dataframe.columns, "DataFrame must have a 'GridFlow_Load' column"
            assert 'BatteryCharge' in dataframe.columns, "DataFrame must have a 'BatteryCharge' column"
            assert 'NettoProduction' in dataframe.columns, "DataFrame must have a 'NettoProduction' column"
            assert 'EVLoad' in dataframe.columns, "DataFrame must have a 'EVLoad' column"
            assert 'PowerLoss' in dataframe.columns, "DataFrame must have a 'PowerLoss' column"
            assert 'BatteryFlow' in dataframe.columns, "DataFrame must have a 'BatteryFlow' column"
            assert 'DualTariff' in dataframe.columns, "DataFrame must have a 'DualTariff' column"
            assert 'DualTariff_Load' in dataframe.columns, "DataFrame must have a 'DualTariff_Load' column"
            assert 'DynamicTariff' in dataframe.columns, "DataFrame must have a 'DynamicTariff' column"
            assert 'DynamicTariff_Load' in dataframe.columns, "DataFrame must have a 'DynamicTariff_Load' column"
            assert 'Belpex' in dataframe.columns, "DataFrame must have a 'Belpex' column"
            self.pd=dataframe

        self.T_STC=25

        self.tariff_dual_peak=0.1701
        self.tariff_dual_offpeak=0.146
        self.tariff_dual_fixed=0.0155
        self.tariff_dual_injection=0.03

        self.tariff_dynamic_A_injection=0.1
        self.tariff_dynamic_B_injection=-0.905
        self.tariff_dynamic_A_offtake=0.1
        self.tariff_dynamic_B_offtake=1.1

        self.reference_id=reference_id

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
    from .utils._getters import get_reference_id
    from .utils._getters import get_battery
    from .utils._getters import get_solarpanel
    from .utils._getters import get_inverter

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
    from .utils._setters import set_reference_id
    from .utils._setters import set_yearly_consumption_energy
    from .utils._setters import set_production_power


    @staticmethod
    def from_snapshot(snapshot: DocumentSnapshot):
        """
        Convert a Firestore snapshot to a SolarPowerModel object
        
        :param snapshot: Firestore snapshot
        :return: SolarPowerModel object
        """
        data = snapshot.to_dict()

        # Handle nested dictionaries
        battery_data = data.get('battery')  # Retrieve nested 'battery' dictionary

        # Convert nested 'battery' dictionary to a Battery object if present
        if battery_data:
            battery = Battery(**battery_data)
            data['battery'] = battery  # Replace dictionary with Battery object

        inverter_data = data.get('inverter')  # Retrieve nested 'inverter' dictionary

        # Convert nested 'inverter' dictionary to an Inverter object if present
        if inverter_data:
            inverter = Inverter(**inverter_data)
            data['inverter'] = inverter
        
        solarpanel_data = data.get('solarpanel')  # Retrieve nested 'solarpanel' dictionary

        # Convert nested 'solarpanel' dictionary to a SolarPanel object if present
        if solarpanel_data:
            solarpanel = SolarPanel(**solarpanel_data)
            data['solarpanel'] = solarpanel

        # convert dataframe to pd.DataFrame
        data['dataframe'] = pd.DataFrame.from_dict(data['dataframe'],orient='index')
        data['dataframe'].index = pd.to_datetime(data['dataframe'].index)
        # Set index name to 'DateTime'
        data['dataframe'].index.name = 'DateTime'

        # Create SolarPowerModel object with all data
        # Pass all data including reference_id conditionally
        if 'reference_id' not in data or data['reference_id'] is None:
            return SolarPowerModel(**data, reference_id=snapshot.id)
        else:
            return SolarPowerModel(**data)
        
    def to_dict(self):
        """
        Convert the SolarPowerModel object to a dictionary
        
        :return: dict
        """
        return {
            'solarpanel': self.solarpanel.to_dict(),
            'inverter': self.inverter.to_dict(),
            'battery': self.battery.to_dict(),
            'reference_id': self.reference_id,
            "dataframe": self.pd.rename(index=lambda x: x.strftime('%Y-%m-%d %H:%M:%S %Z')).to_dict(orient='index')
        }

    @staticmethod
    def from_dict(data: dict):
        """
        Convert a dictionary to a SolarPowerModel object
        
        :param data: dict
        """
        solarpanel = SolarPanel(**data['solarpanel'])
        inverter = Inverter(**data['inverter'])
        battery = Battery(**data['battery'])
        reference_id = data['reference_id']
        dataframe = pd.DataFrame(data['dataframe'])
        
        return SolarPowerModel(solarpanel=solarpanel, inverter=inverter, battery=battery, reference_id=reference_id, dataframe=dataframe)