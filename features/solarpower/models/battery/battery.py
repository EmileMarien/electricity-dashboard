class Battery:
    def __init__(self, battery_cost, battery_lifetime, battery_capacity, battery_inverter,
                 battery_Roundtrip_Efficiency, battery_PeakPower, battery_Degradation, battery_count, battery_type: str=None):
        if battery_type is None:
            self.battery_cost = battery_cost
            self.battery_lifetime = battery_lifetime
            self.battery_capacity = battery_capacity
            self.battery_inverter = battery_inverter
            self.battery_Roundtrip_Efficiency = battery_Roundtrip_Efficiency
            self.battery_PeakPower = battery_PeakPower
            self.battery_Degradation = battery_Degradation
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
            self.battery_Roundtrip_Efficiency = battery_types[battery_type]["battery_Roundtrip_Efficiency"]
            self.battery_PeakPower = battery_types[battery_type]["battery_PeakPower"]
    
            self.battery_Degradation = battery_types[battery_type]["battery_Degradation"]
            self.battery_count = battery_types[battery_type]["battery_count"]

    from _getters import get_battery_inverter, get_battery_cost, get_battery_lifetime, get_battery_capacity, get_battery_Roundtrip_Efficiency, get_battery_PeakPower, get_battery_Degradation, get_battery_count