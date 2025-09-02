from app.repositories.database import db

async def get_links_collection():
    return db["links"]
