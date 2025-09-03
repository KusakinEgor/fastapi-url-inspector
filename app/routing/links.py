from fastapi import APIRouter, Depends
from app.depends import get_links_collection

router = APIRouter(prefix="/links", tags=["Links"])

@router.get("")
async def list_links(links_collection = Depends(get_links_collection)):
    cursor = links_collection.find({})
    results = []

    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    
    return results

@router.post("")
async def create_link(data: dict, links_collection = Depends(get_links_collection)):
    result = await links_collection.insert_one(data)
    return {"inserted_id": str(result.inserted_id)}
