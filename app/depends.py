from app.repositories.database import mongo_db
from app.services.url_checks import URLInspector

inspector: URLInspector | None = None

async def get_inspector() -> URLInspector:
    if inspector is None:
        raise RuntimeError("Inspector is not initialized")
    return inspector

async def get_links_collection():
    return mongo_db["links"]
