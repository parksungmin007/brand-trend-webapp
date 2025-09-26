
from fastapi import FastAPI
from app.routers import ingest, analytics, search

app = FastAPI(title="Brand & Product Trend API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(ingest.router, prefix="")
app.include_router(analytics.router, prefix="/analytics")
app.include_router(search.router, prefix="")
