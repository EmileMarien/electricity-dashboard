from google.cloud import firestore
from buildingmodel.buildingmodel.models.Project.project import Project

class DataRepositoryProject:
    def __init__(self, firestore_reference: firestore.Client):
        self.db = firestore_reference
        # pick a clean collection path; change if you have conventions
        self.collection = self.db.collection("buildingmodel").document("buildingmodel").collection("projects")

    def add_project(self, project: Project) -> str:
        if project.get_reference_id() is None:
            doc_ref = self.collection.document()  # auto id
            project.set_reference_id(doc_ref.id)
            doc_ref.set(project.to_dict())
            return doc_ref.id

        self.collection.document(project.get_reference_id()).set(project.to_dict())
        return project.get_reference_id()

    def update(self, project: Project, fields_to_update: dict = dict()) -> None:
        ref_id = project.get_reference_id()
        if not ref_id:
            raise ValueError("Project has no reference_id; cannot update.")

        if not fields_to_update:
            self.collection.document(ref_id).set(project.to_dict())
        else:
            self.collection.document(ref_id).update(fields_to_update)

    def get_project(self, reference_id: str) -> Project:
        snap = self.collection.document(reference_id).get()
        if not snap.exists:
            raise KeyError(f"Project {reference_id} not found.")
        data = snap.to_dict() or {}
        # ensure id is present
        data["reference_id"] = reference_id
        return Project.from_dict(data)
