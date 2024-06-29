import pandas as pd

class GridCost():
    def __init__(self, data,file_path_BelpexFilter:str=""):
        # Convert Series to DataFrame if data is a Series
        if isinstance(data, pd.Series):
            dataframe = pd.DataFrame({'GridFlow': data})
            dataframe.index = pd.to_datetime(dataframe.index)
        # Use DataFrame directly if data is a DataFrame
        elif isinstance(data, pd.DataFrame):
            dataframe = pd.DataFrame(data['GridFlow'])
        else:
            raise ValueError("Input data must be either a Series or a DataFrame")

        # Check if all required columns are present
        required_columns = ['GridFlow'] # [kW]
        missing_columns = [col for col in required_columns if col not in dataframe.columns]
        assert not missing_columns, f"The following columns are missing: {', '.join(missing_columns)}"

        if file_path_BelpexFilter != "":
            # Use the dataset directly if provided
            belpex_df = pd.read_excel(file_path_BelpexFilter)
    
            assert file_path_BelpexFilter.endswith('.xlsx'), 'The file must be an Excel file'
            

            # Assert that 'Load_kW' and 'DateTime' columns are present in the Excel file
            assert 'DateTime' in belpex_df.columns, "'DateTime' column not found in the Irradiance Excel file"
            
            # Merge the DataFrame with the one read from excel
            merged_df = pd.merge(belpex_df, dataframe, on='DateTime', how='right') 

        else:
            merged_df = dataframe
            merged_df['BelpexFilter'] = None
        
        # Assign the DataFrame to self.pd
        self.pd=merged_df

        #Scale belpex column
        self.pd['BelpexFilter'] = self.pd['BelpexFilter']*1.1261 # scale to 2024 values

        #Set a datetime index
        self.pd.set_index('DateTime', inplace=True)
        self.pd.index = pd.to_datetime(self.pd.index)

        #print(self.pd[self.pd.index.duplicated(keep=False)].index.unique())

        self.pd = self.pd.infer_objects()

        # Resample the DataFrame
        self.pd = self.pd.resample("1h").mean() #TODO: change to freq of above index

        
        # Interpolate the missing values
        self.pd = self.pd.interpolate(method='linear')
        # Initialize the columns that will be used for the calculations
        self.pd['DualTariff'] = None
        self.pd['DynamicTariff'] = None

        # (positive is added to the grid, negative is taken from the grid as seen from the consumer perspective in powercalculations
        



    # Imported methods
    from ._getters import get_dataset
    from ._getters import get_irradiance
    from ._getters import get_load
    from ._getters import get_direct_irradiance
    from ._getters import get_PV_generated_power
    from ._getters import get_grid_cost_perhour
    from ._getters import get_grid_cost_total
    from ._getters import get_total_energy_from_grid
    from ._getters import get_columns
    from ._getters import get_average_per_minute_day


    from ._export import export_dataframe_to_excel

    from ._dualtariff import dual_tariff
    from ._dynamictariff import dynamic_tariff

    from ._capacitytariff import capacity_tariff
