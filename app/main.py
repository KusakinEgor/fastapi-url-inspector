from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"hello": "world"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True
    )
