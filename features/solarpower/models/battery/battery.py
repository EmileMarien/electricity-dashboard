import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot

class Battery:
    def __init__(self, battery_type=None, battery_cost=None, battery_lifetime=None, battery_capacity=None, battery_inverter=None,battery_Roundtrip_Efficiency=None, battery_PeakPower=None, battery_Degradation=None, battery_count=None,reference_id=None):
        """
        battery_cost: cost of a single battery
        battery_lifetime: lifetime of a single battery
        battery_capacity: capacity of a single battery
        battery_inverter: inverter choice for battery
        battery_Roundtrip_Efficiency: roundtrip efficiency of a single battery
        battery_PeakPower: peak power of a single battery
        battery_Degradation: degradation of a single battery
        battery_count: number of batteries
        battery_type: type of battery, choose from the following: "LG RESU 2.9", "LG RESU 5.9", "LG RESU Prime 9.6", "LG RESU Prime 16"
        """
        if battery_type is None:
            self.battery_cost = battery_cost
            self.battery_lifetime = battery_lifetime
            self.battery_capacity = battery_capacity
            self.battery_inverter = battery_inverter
            self.battery_roundtrip_efficiency = battery_Roundtrip_Efficiency
            self.battery_peak_power = battery_PeakPower
            self.battery_degradation = battery_Degradation
            self.battery_count = battery_count
        else:

            # Define different types of batteries
            battery_types = {
                "no battery": {
                    "battery_inverter": 1,  # if this is 0 switch off inverter choice, if this is 1 switch on
                    "battery_cost": 0,
                    "battery_lifetime": 0,
                    "battery_capacity": 0,
                    "battery_Roundtrip_Efficiency": 0,
                    "battery_PeakPower": 0,
                    "battery_Degradation": 0,
                    "battery_count": 0
                },
                "LG RESU 2.9": {
                    "battery_inverter": 1,
                    "battery_cost": 2349 * 1.25,
                    "battery_lifetime": 10,
                    "battery_capacity": 2.9,
                    "battery_Roundtrip_Efficiency": 95,
                    "battery_PeakPower": 3,
                    "battery_Degradation": 4,
                    "battery_count": 1
                },
                "LG RESU 5.9": {
                    "battery_inverter": 1,
                    "battery_cost": 3327.5 * 1.25,
                    "battery_lifetime": 10,
                    "battery_capacity": 5.9,
                    "battery_Roundtrip_Efficiency": 95,
                    "battery_PeakPower": 4.2,
                    "battery_Degradation": 4,
                    "battery_count": 1
                },
                "LG RESU Prime 9.6": {
                    "battery_inverter": 1,
                    "battery_cost": 6497 * 1.25,  # in Eur, times for installation cost
                    "battery_lifetime": 10,  # in years
                    "battery_capacity": 9.6,  # in kWh
                    "battery_Roundtrip_Efficiency": 97.5,  # in percent
                    "battery_PeakPower": 5,  # in kW, rated power
                    "battery_Degradation": 3,  # in percent per year
                    "battery_count": 1
                },
                "LG RESU Prime 16": {
                    "battery_inverter": 1,
                    "battery_cost": 8987 * 1.25,
                    "battery_lifetime": 10,
                    "battery_capacity": 16,
                    "battery_Roundtrip_Efficiency": 97.5,
                    "battery_PeakPower": 7,
                    "battery_Degradation": 3,
                    "battery_count": 1
                }
            }
            self.battery_cost = battery_types[battery_type]["battery_cost"]
            self.battery_lifetime = battery_types[battery_type]["battery_lifetime"]
            self.battery_capacity = battery_types[battery_type]["battery_capacity"]
            self.battery_inverter = battery_types[battery_type]["battery_inverter"]
            self.battery_roundtrip_efficiency = battery_types[battery_type]["battery_Roundtrip_Efficiency"]
            self.battery_peak_power = battery_types[battery_type]["battery_PeakPower"]
    
            self.battery_degradation = battery_types[battery_type]["battery_Degradation"]
            self.battery_count = battery_types[battery_type]["battery_count"]

        self.reference_id = reference_id


    
    from .utils._getters import get_battery_inverter
    from .utils._getters import get_battery_cost
    from .utils._getters import get_battery_lifetime
    from .utils._getters import get_battery_capacity
    from .utils._getters import get_battery_roundtrip_efficiency
    from .utils._getters import get_battery_peak_power
    from .utils._getters import get_battery_degradation
    from .utils._getters import get_battery_count


    @staticmethod
    def from_snapshot(snapshot: DocumentSnapshot):
        data = snapshot.to_dict()
        return Battery(**data, reference_id=snapshot.id)