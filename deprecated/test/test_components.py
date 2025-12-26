
import unittest
from context import fetch_electricity_prices
from context import Inverter
from context import Battery
from context import SolarPanel
class TestComponents(unittest.TestCase):
    def test_inverter(self):
        inverter=Inverter(inverter_type='Sungrow_3')
        print(inverter.to_dict())

    def test_battery(self):
        battery=Battery(battery_type="LG RESU 2.9")
        print(battery.get_battery_type())
        print(battery.to_dict())

    def test_solarpanel(self):
        solarpanel=SolarPanel(solar_panel_type="Jinko")
        print(solarpanel.to_dict())
        

if __name__ == '__main__':
    unittest.main()