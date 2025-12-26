# packages/buildingmodel/buildingmodel/api/main.py

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from buildingmodel.buildingmodel.infrastructure.firestore_init import get_firestore_client

# App service + infrastructure
from buildingmodel.buildingmodel.app.state import BuildingModelApp
from buildingmodel.buildingmodel.repositories.project import DataRepositoryProject
from buildingmodel.buildingmodel.models.Project.utils.output import IfcExporter

# Domain models
from buildingmodel.buildingmodel.models.Project.project import Component

# API schemas (you'll need to add these to schemas.py)
from buildingmodel.buildingmodel.api.schemas import (
    CreateProjectRequest,
    CreateProjectResponse,
    UpdateProjectParametersRequest,
    ProjectResponse,
    AddComponentRequest,
    AddComponentsRequest,
    SetComponentsRequest,
    UpdateComponentPositionRequest,
    ComponentResponse,
    MeetstaatResponse,
    LastenboekResponse,
    IfcExportResponse,
)


def build_app() -> FastAPI:
    api = FastAPI(title="buildingmodel API", version="0.2.0")

    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ----------------------------
    # Wiring (Firestore + repo + exporter + app service)
    # ----------------------------
    db = get_firestore_client()
    project_repo = DataRepositoryProject(db)
    ifc_exporter = IfcExporter(output_dir="generated_ifc")
    app = BuildingModelApp(project_repo=project_repo, ifc_exporter=ifc_exporter)

    # ----------------------------
    # Health
    # ----------------------------
    @api.get("/health")
    def health():
        return {"ok": True}

    # ----------------------------
    # Project lifecycle
    # ----------------------------
    @api.post("/projects", response_model=CreateProjectResponse)
    def create_project(req: CreateProjectRequest):
        p = app.create_project(reference_id=req.reference_id, project_name=req.project_name or "test")
        return {"reference_id": p.get_reference_id()}

    @api.get("/projects/{reference_id}", response_model=ProjectResponse)
    def get_project(reference_id: str):
        try:
            p = app.load_project(reference_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Project not found")
        return p.to_dict()

    # ----------------------------
    # Project parameters
    # ----------------------------
    @api.patch("/projects/{reference_id}/parameters", response_model=ProjectResponse)
    def update_project_parameters(reference_id: str, req: UpdateProjectParametersRequest):
        try:
            p = app.set_project_parameters(
                reference_id,
                building_type=req.building_type,
                shape=req.shape,
                area_m2=req.area_m2,
                functions=req.functions,
            )
        except KeyError:
            raise HTTPException(status_code=404, detail="Project not found")
        return p.to_dict()

    # ----------------------------
    # Components
    # ----------------------------
    @api.post("/projects/{reference_id}/components", response_model=ProjectResponse)
    def add_component(reference_id: str, req: AddComponentRequest):
        try:
            comp = Component.new(
                type=req.type,
                label=req.label or "",
                quantity=req.quantity or 1.0,
                unit=req.unit or "st",
                properties=req.properties or {},
            )
            # If ID is provided, use it
            if req.id:
                comp.id = req.id
            p = app.add_component(reference_id, comp)
        except KeyError:
            raise HTTPException(status_code=404, detail="Project not found")
        return p.to_dict()

    @api.post("/projects/{reference_id}/components/batch", response_model=ProjectResponse)
    def add_components(reference_id: str, req: AddComponentsRequest):
        try:
            comps = [
                Component.new(
                    type=c.type,
                    label=c.label or "",
                    quantity=c.quantity or 1.0,
                    unit=c.unit or "st",
                    properties=c.properties or {},
                )
                for c in req.components
            ]
            # Preserve IDs if provided
            for i, c in enumerate(req.components):
                if c.id:
                    comps[i].id = c.id
            p = app.add_components(reference_id, comps)
        except KeyError:
            raise HTTPException(status_code=404, detail="Project not found")
        return p.to_dict()

    @api.put("/projects/{reference_id}/components", response_model=ProjectResponse)
    def set_components(reference_id: str, req: SetComponentsRequest):
        """Replace all components in the project."""
        try:
            comps = [
                Component.new(
                    type=c.type,
                    label=c.label or "",
                    quantity=c.quantity or 1.0,
                    unit=c.unit or "st",
                    properties=c.properties or {},
                )
                for c in req.components
            ]
            # Preserve IDs if provided
            for i, c in enumerate(req.components):
                if c.id:
                    comps[i].id = c.id
            p = app.set_components(reference_id, comps)
        except KeyError:
            raise HTTPException(status_code=404, detail="Project not found")
        return p.to_dict()

    @api.get("/projects/{reference_id}/components", response_model=list[ComponentResponse])
    def get_components(reference_id: str):
        try:
            comps = app.get_components(reference_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Project not found")
        return [c.to_dict() for c in comps]

    @api.patch("/projects/{reference_id}/components/{component_id}/position", response_model=ProjectResponse)
    def update_component_position(reference_id: str, component_id: str, req: UpdateComponentPositionRequest):
        """Update the position of a specific component."""
        try:
            p = app.update_component_position(
                reference_id,
                component_id,
                position=req.position,
                rotation_y=req.rotation_y,
            )
        except KeyError:
            raise HTTPException(status_code=404, detail="Project or component not found")
        return p.to_dict()

    @api.delete("/projects/{reference_id}/components/{component_id}", response_model=ProjectResponse)
    def delete_component(reference_id: str, component_id: str):
        """Delete a specific component."""
        try:
            p = app.delete_component(reference_id, component_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Project or component not found")
        return p.to_dict()

    # ----------------------------
    # Outputs: Meetstaat & Lastenboek
    # ----------------------------
    @api.get("/projects/{reference_id}/meetstaat", response_model=MeetstaatResponse)
    def get_meetstaat(reference_id: str):
        try:
            meetstaat = app.compute_meetstaat(reference_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Project not found")
        return meetstaat.to_dict()

    @api.get("/projects/{reference_id}/lastenboek", response_model=LastenboekResponse)
    def get_lastenboek(reference_id: str):
        try:
            lastenboek = app.compute_lastenboek(reference_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Project not found")
        return lastenboek.to_dict()

    # ----------------------------
    # IFC export + file download
    # ----------------------------
    @api.post("/projects/{reference_id}/ifc", response_model=IfcExportResponse)
    def export_ifc(reference_id: str):
        try:
            payload = app.export_ifc(reference_id)  # returns dict with file info
        except KeyError:
            raise HTTPException(status_code=404, detail="Project not found")
        return payload

    @api.get("/ifc/{filename}")
    def download_ifc(filename: str):
        # simple download endpoint (MVP). In production, store in object storage.
        path = ifc_exporter._ensure_dir() / filename
        if not path.exists():
            raise HTTPException(status_code=404, detail="IFC file not found")
        return FileResponse(str(path), media_type="application/octet-stream", filename=path.name)

    return api


app = build_app()
