import os
import sys
import pandas as pd
import pickle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import solarpowermodel.solarpowermodel as pc

print('test')

latitude=50.99461 # [degrees]
longitude=5.53972 # [degrees]


print('start')
file = open('data/initialized_dataframes/pd_S_30','rb')
irradiance_pd_S_30=pickle.load(file)
file.close()    
irradiance_pd_S_30.get_columns(['Load_EV_kW_with_SC'])
# Add Load_EV_kW_no_SC & Load_EV_kW_with_SC columns to each dataset
add_EV_load=True
if add_EV_load:
    file = open('data/initialized_dataframes/pd_S_30','rb')
    irradiance_pd_S_30=pickle.load(file)
    file.close()
    irradiance_pd_S_30.add_EV_load()
    file=open('data/initialized_dataframes/pd_S_30','wb')
    pickle.dump(irradiance_pd_S_30,file)
    file.close()
    print('upload 1 finished')

    file = open('data/initialized_dataframes/pd_EW_30','rb')
    irradiance_pd_EW_30=pickle.load(file)
    file.close()
    irradiance_pd_EW_30.add_EV_load()
    file=open('data/initialized_dataframes/pd_EW_30','wb')
    pickle.dump(irradiance_pd_EW_30,file)
    file.close()
    print('upload 2 finished')

    file = open('data/initialized_dataframes/pd_EW_opt_32','rb')
    irradiance_pd_EW_opt_32=pickle.load(file)
    file.close()
    irradiance_pd_EW_opt_32.add_EV_load()
    file=open('data/initialized_dataframes/pd_EW_opt_32','wb')
    pickle.dump(irradiance_pd_EW_opt_32,file)
    file.close()
    print('upload 3 finished')

    file = open('data/initialized_dataframes/pd_S_opt_37.5','rb')
    irradiance_pd_S_opt_37_5=pickle.load(file)
    file.close()
    irradiance_pd_S_opt_37_5.add_EV_load()
    file=open('data/initialized_dataframes/pd_S_opt_37.5','wb')
    pickle.dump(irradiance_pd_S_opt_37_5,file)
    file.close()
    print('upload 4 finished')

    file = open('data/initialized_dataframes/pd_E_30','rb')
    irradiance_pd_E_30=pickle.load(file)    
    file.close()
    irradiance_pd_E_30.add_EV_load()
    file=open('data/initialized_dataframes/pd_E_30','wb')
    pickle.dump(irradiance_pd_E_30,file)
    file.close()
    print('upload 5 finished')

    file = open('data/initialized_dataframes/pd_W_30','rb')
    irradiance_pd_W_30=pickle.load(file)
    file.close()
    irradiance_pd_W_30.add_EV_load()
    file=open('data/initialized_dataframes/pd_W_30','wb')
    pickle.dump(irradiance_pd_W_30,file)
    file.close()
    print('upload 6 finished')





calculate_irradiances=False
if calculate_irradiances:
    file = open('data/initialized_dataframes/pd_S_30','rb')
    irradiance=pickle.load(file)
    file.close()

    irradiance.calculate_direct_irradiance(tilt_angle=30,orientation='EW')
    file=open('data/initialized_dataframes/pd_EW_30','wb')
    pickle.dump(irradiance,file)
    file.close()
    print('upload 2 finished')

    irradiance.calculate_direct_irradiance(tilt_angle=32,orientation='EW')
    file=open('data/initialized_dataframes/pd_EW_opt_32','wb')
    pickle.dump(irradiance,file)
    file.close()
    print('upload 3 finished')



    irradiance.calculate_direct_irradiance(tilt_angle=37.5,orientation='S')
    file=open('data/initialized_dataframes/pd_S_opt_37.5','wb')
    pickle.dump(irradiance,file)
    file.close()
    print('upload 4 finished')

    irradiance.calculate_direct_irradiance(tilt_angle=30,orientation='E')
    file=open('data/initialized_dataframes/pd_E_30','wb')
    pickle.dump(irradiance,file)
    file.close()
    print('upload 5 finished')

    irradiance.calculate_direct_irradiance(tilt_angle=30,orientation='W')
    file=open('data/initialized_dataframes/pd_W_30','wb')
    pickle.dump(irradiance,file)
    file.close()
    print('upload 6 finished')

    irradiance.calculate_direct_irradiance(tilt_angle=30,orientation='S')
    file=open('data/initialized_dataframes/pd_S_30','wb')
    pickle.dump(irradiance,file)
    file.close()
    print('upload 7 finished')





