from fastapi import FastAPI
import uvicorn
import asyncio

from app.routing.analyze import router as analyze_router
from app.routing.history import router as history_router
from app.routing.report import router as report_router
from app.services.url_checks import URLInspector
from app.repositories.database import mongo_db
import app.depends as depends

app = FastAPI()

app.include_router(analyze_router)
app.include_router(history_router)
app.include_router(report_router)

@app.on_event("startup")
async def startup_event():
    depends.inspector = URLInspector(timeout=10.0)

    try:
        collections = await mongo_db.list_collection_names()
        print("MongoDB connected. Collections:", collections)
    except Exception as e:
        print("MongoDB connection failed:", e)

@app.on_event("shutdown")
async def shutdown_event():
    if depends.inspector:
        await depends.inspector.close()

@app.get("/")
async def root():
    return {"Url": "Inspector"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
