
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ingest, analytics, search

app = FastAPI(title="Brand & Product Trend API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(ingest.router, prefix="")
app.include_router(analytics.router, prefix="/analytics")
app.include_router(search.router, prefix="")
