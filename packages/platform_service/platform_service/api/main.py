from fastapi import FastAPI

from elecmodel.elecmodel.api.main import app as elec_app
from buildingmodel.buildingmodel.api.main import app as building_app

app = FastAPI(title="Platform Service")

app.mount("/elec", elec_app)
app.mount("/building", building_app)
