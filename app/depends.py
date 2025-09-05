from app.repositories.database import db
from app.services.url_checks import URLInspector

inspector: URLInspector | None = None

async def get_inspector() -> URLInspector:
    if inspector is None:
        raise RuntimeError("Inspector is not initialized")
    return inspector

async def get_links_collection():
    return db["links"]
