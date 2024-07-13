import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot

class Inverter:
    def __init__(self, inverter_type=None, inverter_cost=None, inverter_size_AC=None, inverter_maxbattery_DC=None, inverter_lifetime=None, inverter_efficiency=None, inverter_maxsolar_DC=None, reference_id=None):
        """
        

        
        inverter_cost: cost of a single inverter
        inverter_size_AC: size of a single inverter
        inverter_maxbattery_DC: maximum battery DC of a single inverter
        inverter_maxsolar_DC: maximum solar DC of a single inverter
        inverter_lifetime: lifetime of a single inverter
        inverter_efficiency: efficiency of a single inverter
        inverter_type: type of inverter, choose from the following: "Sungrow_3", "Sungrow_3.6", "Sungrow_4", "Sungrow_5", "Fronius_3", "Fronius_3.6", "Fronius_4", "Fronius_4.6", "Fronius_5", "Sungrow SG2.0RS-S", "Sungrow SG2.5RS-S", "Sungrow SG3.0RS-S", "Sungrow SG3.0RS", "Sungrow SG3.6RS", "Sungrow SG4.0RS", "Sungrow SG5.0RS"
        """
        inverter_types = {
                "no inverter": {
                    "inverter_cost": 0,
                    "inverter_size_AC": 100000,
                    "inverter_maxbattery_DC": 100000,
                    "inverter_maxsolar_DC": 100000,
                    "inverter_lifetime": 100,
                    "inverter_efficiency": 1,
                },
                "Sungrow_3": {
                    "inverter_cost": 1219,
                    "inverter_size_AC": 3,
                    "inverter_maxbattery_DC": 6.6,
                    "inverter_maxsolar_DC": 10,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.97,
                },
                "Sungrow_3.6": {
                    "inverter_cost": 1380,
                    "inverter_size_AC": 3.68,
                    "inverter_maxbattery_DC": 6.6,
                    "inverter_maxsolar_DC": 10.7,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.971,  
                },
                "Sungrow_4": {
                    "inverter_cost": 1460,
                    "inverter_size_AC": 4,
                    "inverter_maxbattery_DC": 6.6,
                    "inverter_maxsolar_DC": 11,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.972,
                },
                "Sungrow_5": {
                    "inverter_cost": 1570,
                    "inverter_size_AC": 5,
                    "inverter_maxbattery_DC": 6.6,
                    "inverter_maxsolar_DC": 12,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.972,
                },
                "Fronius_3": {
                    "inverter_cost": 1579,
                    "inverter_size_AC": 3,
                    "inverter_maxbattery_DC": 3.11,
                    "inverter_maxsolar_DC": 4.5,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.968,
                },
                "Fronius_3.6": {
                    "inverter_cost": 1650,
                    "inverter_size_AC": 3.68,
                    "inverter_maxbattery_DC": 3.81,
                    "inverter_maxsolar_DC": 5.52,        
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.97,   
                },
                "Fronius_4": {
                    "inverter_cost": 1702,
                    "inverter_size_AC": 4,
                    "inverter_maxbattery_DC": 4.14,
                    "inverter_maxsolar_DC": 6,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.971,    
                },
                "Fronius_4.6": {
                    "inverter_cost": 1826,
                    "inverter_size_AC": 4.6,
                    "inverter_maxbattery_DC": 4.75,
                    "inverter_maxsolar_DC": 6.9,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.972,    
                },
                "Fronius_5": {
                    "inverter_cost": 1922,
                    "inverter_size_AC": 5,
                    "inverter_maxbattery_DC": 5.17,
                    "inverter_maxsolar_DC": 7.5,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.972,    
                },
                "Sungrow SG2.0RS-S": {
                    "inverter_cost": 585,
                    "inverter_size_AC": 2,
                    "inverter_maxbattery_DC": 2,
                    "inverter_maxsolar_DC": 3,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.972,  
                },
                "Sungrow SG2.5RS-S": {
                    "inverter_cost": 590,
                    "inverter_size_AC": 2.5,
                    "inverter_maxbattery_DC": 2.5,
                    "inverter_maxsolar_DC": 3.75,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.972,  
                },
                "Sungrow SG3.0RS-S": {
                    "inverter_cost": 640,
                    "inverter_size_AC": 3,
                    "inverter_maxbattery_DC": 3,
                    "inverter_maxsolar_DC": 4.5,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.972,  
                },
                "Sungrow SG3.0RS": {
                    "inverter_cost": 690,
                    "inverter_size_AC": 3,
                    "inverter_maxbattery_DC": 3,
                    "inverter_maxsolar_DC": 4.5,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.972,  
                },
                "Sungrow SG3.6RS": {
                    "inverter_cost": 790,
                    "inverter_size_AC": 3.6,
                    "inverter_maxbattery_DC": 3.68,
                    "inverter_maxsolar_DC": 5.4,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.972,  
                },
                "Sungrow SG4.0RS": {
                    "inverter_cost": 820,
                    "inverter_size_AC": 4,
                    "inverter_maxbattery_DC": 4,
                    "inverter_maxsolar_DC": 6,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.972,  
                },
                "Sungrow SG5.0RS": {
                    "inverter_cost": 890,
                    "inverter_size_AC": 5,
                    "inverter_maxbattery_DC": 5,
                    "inverter_maxsolar_DC": 7.5,
                    "inverter_lifetime": 10,
                    "inverter_efficiency": 0.972,  
                },
            }
        if inverter_type not in inverter_types.keys:
            self.inverter_type = inverter_type
            self.inverter_cost = inverter_cost
            self.inverter_size_AC = inverter_size_AC
            self.inverter_maxsolar_DC = inverter_maxsolar_DC
            self.inverter_lifetime = inverter_lifetime
            self.inverter_efficiency = inverter_efficiency
            self.inverter_maxbattery_DC = inverter_maxbattery_DC
        else:
            # Define different types of inverters
        
            self.inverter_cost = inverter_types[inverter_type]["inverter_cost"]
            self.inverter_size_AC = inverter_types[inverter_type]["inverter_size_AC"]
            self.inverter_maxbattery_DC = inverter_types[inverter_type]["inverter_maxbattery_DC"]
            self.inverter_maxsolar_DC = inverter_types[inverter_type]["inverter_maxsolar_DC"]
            self.inverter_lifetime = inverter_types[inverter_type]["inverter_lifetime"]
            self.inverter_efficiency = inverter_types[inverter_type]["inverter_efficiency"]
            self.inverter_type=inverter_type

        self.reference_id = reference_id
    # Imported methods
    
    from .utils._getters import get_inverter_cost
    from .utils._getters import get_inverter_size_AC
    from .utils._getters import get_inverter_maxsolar_DC
    from .utils._getters import get_inverter_lifetime
    from .utils._getters import get_inverter_efficiency
    from .utils._getters import get_inverter_maxbattery_DC
    from .utils._getters import get_inverter_type



    @staticmethod
    def from_snapshot(snapshot: DocumentSnapshot):
        data = snapshot.to_dict()
        return Inverter(**data, reference_id=snapshot.id)    

    def to_dict(self):
        return {
            "inverter_cost": self.inverter_cost,
            "inverter_size_AC": self.inverter_size_AC,
            "inverter_maxsolar_DC": self.inverter_maxsolar_DC,
            "inverter_lifetime": self.inverter_lifetime,
            "inverter_efficiency": self.inverter_efficiency,
            "inverter_maxbattery_DC": self.inverter_maxbattery_DC,
            "reference_id": self.reference_id
        }