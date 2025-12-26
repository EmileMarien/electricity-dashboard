
import pandas as pd

class Meter:
    def __init__(self,location,owner,date_of_initialisation):
        self.location=location
        self.owner=owner
        self.date_of_initialisation=date_of_initialisation
        self.model = SolarPower()

    # Getter for the DataFrame
    def get_location(self):
        return self.location

    # Setter for the DataFrame
    def set_location(self, new_location):
        if isinstance(new_data, pd.DataFrame):
            self.data = new_data
        else:
            print("Invalid data. Please provide a pandas DataFrame.")

    # Getter for the PowerModels instance
    def get_model(self):
        return self.model

    # Setter for the PowerModels instance
    def set_model(self, new_model):
        # Assuming the type of new_model should be the same as the type of self.model
        if isinstance(new_model, type(self.model)):
            self.model = new_model
        else:
            print("Invalid model. Please provide a correct PowerModels instance.")