from fastapi import FastAPI
from app.api.routes import router as aggregator_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

app.include_router(aggregator_router, prefix="/aggregator", tags=["Aggregator"])
