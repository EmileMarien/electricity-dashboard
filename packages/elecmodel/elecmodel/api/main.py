from fastapi import FastAPI

from elecmodel.api.schemas import CreateModelRequest, ChangeComponentsRequest
from elecmodel.app.state import ElecModelApp

from elecmodel.infrastructure.firestore_init import get_firestore_client
from elecmodel.repositories.solarmodel import DataRepositorySolarModel
from elecmodel.repositories.belpex import DataRepositoryBelpex
from elecmodel.repositories.syntheticprofiles import DataRepositorySLP, DataRepositorySPP


def build_app() -> FastAPI:
    api = FastAPI(title="elecmodel API", version="0.1.0")

    db = get_firestore_client()

    app = ElecModelApp(
        model_repo=DataRepositorySolarModel(db),
        belpex_repo=DataRepositoryBelpex(db),
        slp_repo=DataRepositorySLP(db),
        spp_repo=DataRepositorySPP(db),
    )

    @api.get("/health")
    def health():
        return {"ok": True}

    @api.post("/models")
    def create_model(req: CreateModelRequest):
        m = app.new_model(req.reference_id)
        return {"reference_id": m.get_reference_id()}

    @api.post("/models/{reference_id}/update-data")
    def update_data(reference_id: str):
        app.update_prices(reference_id)
        app.update_profiles(reference_id)
        return {"status": "data_updated"}

    @api.post("/models/{reference_id}/recompute")
    def recompute(reference_id: str):
        app.update_calculations(reference_id)
        return {"status": "recomputed"}

    @api.post("/models/{reference_id}/components")
    def change_components(reference_id: str, req: ChangeComponentsRequest):
        app.change_components(reference_id, **req.model_dump())
        return {"status": "components_updated"}

    @api.get("/models/{reference_id}/kpis")
    def kpis(reference_id: str):
        return app.kpis(reference_id)

    return api


app = build_app()
