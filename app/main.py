from fastapi import FastAPI
import uvicorn

from app.routing.links import router as link_router

app = FastAPI()

app.include_router(link_router)

@app.get("/")
async def root():
    return {"hello": "world"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
