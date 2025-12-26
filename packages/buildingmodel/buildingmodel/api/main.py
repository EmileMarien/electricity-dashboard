from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from buildingmodel.buildingmodel.api.schemas import CreateModelRequest, ChangeComponentsRequest, HouseCatalogItem, HouseSceneState, HouseInsightsResponse
from buildingmodel.buildingmodel.app.state import buildingmodelApp

from models.Component import HouseComponentService

from buildingmodel.infrastructure.firestore_init import get_firestore_client
from buildingmodel.buildingmodel.models.Component.component import HouseDesignService


def build_app() -> FastAPI:
    api = FastAPI(title="buildingmodel API", version="0.1.0")
    
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    db = get_firestore_client()

    app = buildingmodelApp()

    # House Builder domain service
    house_components = HouseComponentService()
    house_design = HouseDesignService(components=house_components)

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


    # ----------------------------
    # House Builder endpoints
    # ----------------------------
    @api.get("/house/catalog")
    def house_catalog():
        return house_components.get_catalog()

    @api.post("/house/insights")
    def house_insights(scene: dict):
        return house_components.compute_insights(scene)

    @api.post("/house/concept", response_model=HouseConceptResponse)
    def house_concept(req: HouseConceptRequest):
        payload = house_design.generate_concept(
            building_type=req.building_type,
            shape=req.shape,
            area_m2=req.area_m2,
            functions=req.functions,
        )
        return payload

    @api.get("/house/ifc/{ifc_file_id}")
    def house_ifc(ifc_file_id: str):
        # HouseDesignService writes to disk. We reconstruct the expected filename.
        # (In production, store this mapping in DB/object storage.)
        directory = house_design._ensure_ifc_dir()
        path = directory / f"housebuilder_{ifc_file_id}.ifc"
        if not path.exists():
            # try alternate pattern used by export_ifc_minimal (includes uuid in filename)
            # scan quickly (MVP)
            for p in directory.glob("housebuilder_*.ifc"):
                if ifc_file_id in p.name:
                    path = p
                    break
        if not path.exists():
            # FastAPI will convert this to a 404 response
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="IFC file not found")
        return FileResponse(str(path), media_type="application/octet-stream", filename=path.name)

    return api


app = build_app()
