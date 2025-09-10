from fastapi import FastAPI
import uvicorn

from app.routing.analyze import router as analyze_router
from app.routing.history import router as history_router
from app.routing.report import router as report_router
from app.services.url_checks import URLInspector
import app.depends as depends

app = FastAPI()

app.include_router(analyze_router)
app.include_router(history_router)
app.include_router(report_router)

@app.on_event("startup")
async def startup_event():
    depends.inspector = URLInspector(timeout=10.0)

@app.on_event("shutdown")
async def shutdown_event():
    if depends.inspector:
        await depends.inspector.close()

@app.get("/")
async def root():
    return {"Url": "Inspector"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
