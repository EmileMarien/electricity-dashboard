import os
import sys
import pandas as pd
import pickle
import pvlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import powercalculations.powercalculations as pc

### Initialisation
# Load dataset
file=open('data/initialized_dataframes/pd_S_30','rb')
data=pickle.load(file)
file.close()
#data.filter_data_by_date_interval('2018-01-01','2018-12-31',interval_str='1min')
# Set coordinates of PV installation (GENk)
latitude=50.99461 # [degrees]
longitude=5.53972 # [degrees]

### test most optimal panel tilt angle for each azimuth angle case
"""
- Only using directIrradiance function. 
- the tilt angle at which the total direct irradiance over 1 full year, for a specific azimuth angle, is the highest, is the optimal tilt angle
"""
findAngle=True
if findAngle:
    
    orientations=["EW"]
    tiltAngles=[i/2 for i in range(20, 90)]  # Modify the range values to integers
    data.filter_data_by_date_interval('2018-01-01','2018-12-31',interval_str='15min')
    data.interpolate_columns(interval='15min')
    temperature = 10
    for orientation in orientations:
        optimalAngle=(-1,0) #(angle, total directIrradiance at that angle)

        for tiltAngle in tiltAngles:
            data.calculate_direct_irradiance(tilt_angle=tiltAngle,orientation=orientation)
            totalIrradiance=data.get_direct_irradiance().mean()
            print("irradiance:",totalIrradiance,"tiltangle:",tiltAngle)
            if totalIrradiance>optimalAngle[1]:
                optimalAngle=(tiltAngle,totalIrradiance)
            else:
                continue
        
        print("The optimal angle for the "+str(orientation)+ " Orientation is: "+ str(optimalAngle)+" degrees")

### test the average direct irradiance for each orientation
get_irradiance=False
if get_irradiance:
    data.calculate_direct_irradiance(latitude=latitude, tilt_angle=80,longitude=longitude,temperature=10,orientation='E')
    print(data.get_average_per_hour("DirectIrradiance"))

    data.calculate_direct_irradiance(latitude=latitude, tilt_angle=80,longitude=longitude,temperature=10,orientation='W')
    print(data.get_average_per_hour("DirectIrradiance"))

    data.calculate_direct_irradiance(latitude=latitude, tilt_angle=80,longitude=longitude,temperature=10,orientation='S')
    print(data.get_average_per_hour("DirectIrradiance"))
"""
To put in report:
- the irradiance output of the solar panels for the different orientations with optimal angle throughout the year
- waterfall chart 


"""
calculate_solar_angles=False
if calculate_solar_angles:
    # Define the date range for a day in August
    start = pd.Timestamp('2022-08-01', tz='Europe/Amsterdam')
    end = pd.Timestamp('2022-08-02', tz='Europe/Amsterdam')
    day_datetime_index = pd.date_range(start, end, freq='H')

    # Solar angles calculation
    A = pvlib.solarposition.get_solarposition(day_datetime_index, latitude=latitude, longitude=longitude, temperature=15)

    solar_zenith_angle = A['zenith']  # [degrees] starting from the vertical
    solar_azimuth_angle = A['azimuth']  # [degrees] starting from the north

    print(solar_zenith_angle, solar_azimuth_angle)