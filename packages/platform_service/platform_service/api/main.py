from fastapi import FastAPI

from elecmodel.elecmodel.api.main import app as elec_app
from buildingmodel.buildingmodel.api.main import app as building_app  # your actual import

app = FastAPI(title="Platform Service", version="0.1.0")

app.mount("/elec", elec_app)
app.mount("/building", building_app)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def root():
    return {
        "services": {
            "elec": "/elec/docs",
            "building": "/building/docs",
        }
    }
